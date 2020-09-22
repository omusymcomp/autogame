# -*- coding:utf-8 -*-
import os
import json
import gspread
import sys
import subprocess
from oauth2client.service_account import ServiceAccountCredentials

def writeResults(order, branch, opp, result_map):
    doc_id = subprocess.Popen(
        'source ../config; echo ${GGSS_KEY}', stdout=subprocess.PIPE,
        shell=True, executable='/bin/bash').communicate()[0].decode("utf8").strip("\n")
    jsonfile = subprocess.Popen(
        'source ../config; echo ${GGSS_JSON}', stdout=subprocess.PIPE,
        shell=True, executable='/bin/bash').communicate()[0].decode("utf8").strip("\n")
    sheetname = subprocess.Popen(
        'source ../config; echo ${GGSS_SPREAD_SHEET_NAME}', stdout=subprocess.PIPE,
        shell=True, executable='/bin/bash').communicate()[0].decode("utf8").strip("\n")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    path = os.path.expanduser("./gametools/{}".format(jsonfile))  # set json file
    doc_id = doc_id  # documents id of google spread sheet
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize(credentials)
    gfile = client.open_by_key(doc_id)

    worksheet_list = gfile.worksheets()
    write_count = 0

    if sheetname not in [wks.title for wks in worksheet_list]:
        # create sheet
        gfile.add_worksheet(title=sheetname, rows=1000, cols=100, index=0)
        tmp_rows = []

        opplist = subprocess.run(
            'source ../config; echo ${OPP_TEAMS[@]}', stdout=subprocess.PIPE,
            shell=True, executable='/bin/bash').stdout.decode("utf8").strip().split()
        for i, opp in enumerate(opplist):
            if i == 0:
                tmp_rows.append(["", ""])
                tmp_rows.append(["ORDER", "branch"])
                write_count += 4
            tmp_rows[0].extend([opp, "", "", "", ""])
            tmp_rows[1].extend(["win", "draw", "lose", "our_score", "opp_score"])
            write_count += 10
        gfile.worksheet(sheetname).append_rows(tmp_rows)

    worksheet = gfile.worksheet(sheetname)  # choose your worksheet
    order_cell_list = worksheet.findall(order)
    branch_cell_list = worksheet.findall(branch)
    opp_cell = worksheet.find(opp)

    target_cell_col = opp_cell.col
    target_cell_row = 0
    for order_cell in order_cell_list:
        for branch_cell in branch_cell_list:
            if order_cell.row == branch_cell.row:
                target_cell_row = order_cell.row

    # initial write
    if target_cell_row == 0:
        worksheet.insert_row([order, branch], 3)
        target_cell_row = 3
        write_count += 2

    worksheet.update_cell(target_cell_row, target_cell_col, result_map["win"])
    worksheet.update_cell(target_cell_row, target_cell_col+1, result_map["draw"])
    worksheet.update_cell(target_cell_row, target_cell_col+2, result_map["lose"])
    worksheet.update_cell(target_cell_row, target_cell_col+3, result_map["our_score"])
    worksheet.update_cell(target_cell_row, target_cell_col+4, result_map["opp_score"])
    write_count += 5

    return write_count