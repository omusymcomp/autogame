# coding: utf-8
import os
import sys
import json
import time
import datetime
import subprocess
from typing import List, TypedDict

sys.path.append("{}/gametools".format(os.getcwd()))
import gametools.tools as tl
import gametools.ggssapi_gameresult as ggssapi


class ConfigDict(TypedDict):
    our: List[str]
    branch: List[str]
    opp: List[str]
    gamenum: int


class Config:
    def __init__(
        self, our: List[str], branch: List[str], opp: List[str], num: int
    ) -> None:
        self.our: List[str] = our
        self.branch: List[str] = branch
        self.opp: List[str] = opp
        self.num: int = num

    @classmethod
    def from_dict(cls, dict: ConfigDict) -> "Config":
        our = dict["our"]
        branch = dict["branch"]
        opp = dict["opp"]
        num = dict["gamenum"]
        return Config(our, branch, opp, num)

    @classmethod
    def loadFile(cls, path: str) -> "Config":
        print(f"File Path:{path}")
        with open(path) as f:
            option = json.load(f)
        print(f"option={option}")
        return cls.from_dict(option)


class TeamInf(TypedDict):
    path: str
    is_branch: bool
    is_synch: bool


def boolToStr(flag: bool) -> str:
    if flag:
        return "true"
    else:
        return "false"


def numCheck(str, sp):
    if not str[-1].isdecimal():
        print(f"  ***ERROR***:{sp}[{str[-1]}] is {sp}(Num){sp}(Num)...")
        return False
    else:
        return True


def chooseNewOrLoad():
    print(
        f"1:Choose new or load for game setting. ( ex. new )\n  new : start with new setting \n  load : start with load your setting"
    )
    while True:
        ans = input(" new or load: ")
        if ans in ["new", "load"]:
            return ans
        else:
            print(f' ***ERROR***:answer is "new" or "load"')


def chooseOurTeam():
    print(
        f'2:Choose the our team. ( ex. our1our12our13 )\n  When you choose "our", you can select all teams'
    )

    ourlist = tl.getOur()
    for i in range(len(ourlist)):
        print(f"  our{str(i)}:{ourlist[i]}")

    while True:
        ans = input("  our: ")
        ours = ans.split("our")
        if not numCheck(ours, "our"):
            continue
        for our in ours[1:]:
            if not our.isdecimal():
                print(f"  ***ERROR***:our[{our}] is our(Num)our(Num)...")
                break
            our = int(our)
            if not our in list(range(len(ourlist))):
                print(f"  ***ERROR***:our[{our}] is no ours")
                break
            if our == int(ours[-1]):
                tl.updateOption("our", ans)
                return ans


def chooseBranch(ours):
    if "our0" in ours:
        tl.updateOption("our", ours)
        print(
            f"3:Please set up to start the game.\n  Choose your branch.( ex. br0br5 )"
        )
        branchlist = tl.getBranch()
        for i in range(len(branchlist)):
            print(f"  br{str(i)} : {branchlist[i]}")

        while True:
            ans = input("  br: ")
            branches = ans.split("br")
            if not numCheck(branches, "br"):
                continue
            for branch in branches[1:]:
                if not branch.isdecimal():
                    print(f"  ***ERROR***:br[{branch}] is br(Num)br(Num)...")
                    break
                branch = int(branch)
                if not branch in list(range(len(branchlist))):
                    print(f"  ***ERROR***:br[{branch}] is no ours")
                    break
                if branch == int(branches[-1]):
                    tl.updateOption("branch", ans)
                    return ans
    else:
        print(f"3:No exist branch team")


def chooseOppTeam():
    print(
        f'4:Choose the opponent team. ( ex. opp1opp12opp13 )\n  When you choose "opp", you can select all teams'
    )

    opplist = tl.getOpponent()
    for i in range(len(opplist)):
        print(f"  opp{str(i)}:{opplist[i]}")

    while True:
        ans = input("  opp: ")
        opps = ans.split("opp")
        if not numCheck(opps, "opp"):
            continue
        for opp in opps[1:]:
            if not opp.isdecimal():
                print(f"  ***ERROR***:opp[{opp}] is opp(Num)opp(Num)...")
                break
            opp = int(opp)
            if not opp in list(range(len(opplist))):
                print(f"  ***ERROR***:opp[{opp}] is no opps")
                break
            if opp == int(opps[-1]):
                tl.updateOption("opponent", ans)
                return ans


def chooseGameNum():
    print(f"5:How many games do you want to run? ( ex. 100 )")

    while True:
        print("  num: ", end="")
        ans = input()
        if not ans.isdecimal():
            print(f"  ***ERROR***:num[{ans}] is int")
        else:
            tl.updateOption("gamenum", ans)
            return ans


def checkTime(ours, branches, opps, num):
    print(f"We run {num} games.")
    msg = tl.confirmSetting()
    print(f"{msg}")


class AutoGame:
    left_teams: List[TeamInf]
    right_teams: List[TeamInf]
    game_num: int

    def setLeftTeam(
        self, teams: List[str], branchies: List[str], branch_list: List[str]
    ) -> None:
        left_teams: List[TeamInf] = []
        for i, team in enumerate(teams + branchies):
            # check our team is branch or teams
            if team in branch_list:
                is_branch = True
                print(f"[{i}]:{team} is branch")
            else:
                is_branch = False
                print(f"[{i}]:{team} is not branch")

            left_teams.append(
                {
                    "path": team,
                    "is_branch": is_branch,
                    "is_synch": tl.is_available_synch(team),
                }
            )
        print(f"left_teams = {left_teams}")
        self.left_teams = left_teams

    def setRightTeam(self, teams: List[str]) -> None:
        right_teams: List[TeamInf] = []
        for team in teams:
            # check our team is branch or teams
            right_teams.append(
                {
                    "path": team,
                    "is_branch": False,
                    "is_synch": tl.is_available_synch(team),
                }
            )
        print(f"right_teams = {right_teams}")
        self.right_teams = right_teams


def doGame(option: Config):
    auto_game = AutoGame()

    dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    available_hostlist = tl.getHost()

    working_procs = {"proc": [], "setting": []}
    finished_procs = {"proc": [], "setting": []}
    all_settings = []

    # -------- #
    # execution
    # -------- #
    total_count = 0

    # set teams
    auto_game.setLeftTeam(option.our, option.branch, tl.getBranch())
    auto_game.setRightTeam(option.opp)

    # left loop
    for left_team in auto_game.left_teams:
        if left_team["is_branch"]:
            # send my team branch binary
            branchproc = subprocess.Popen(
                ["./gametools/branchcompile.sh", left_team["path"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        # right loop
        for rigth_team in auto_game.right_teams:
            if left_team["path"] == rigth_team["path"]:
                print(left_team, rigth_team, "same team")
                continue

            # dir name can be specified by dt_now, our_name and opp_name
            dirname = "{}/{}_{}".format(
                dt_now,
                left_team["path"].split("/")[-1],
                rigth_team["path"].replace("/", "-"),
            )

            # append setting information
            all_settings.append([dirname, left_team["path"], rigth_team["path"]])

            # game loop
            for game in range(option.num):
                # check host
                # loop until next host is found
                host = None
                while True:
                    # the order should be reversed for pop
                    for i in reversed(range(len(working_procs["proc"]))):
                        if working_procs["proc"][i].poll() is not None:
                            p = working_procs["proc"].pop(i)
                            s = working_procs["setting"].pop(i)
                            finished_procs["proc"].append(p)
                            finished_procs["setting"].append(s)

                            # recover available hostlist
                            available_hostlist.append(s[1])

                            # progress report
                            total_count += 1
                            if total_count % 1000 == 0:
                                msg = "Progress Report\n  {} games are finished.\n  {} games left.".format(
                                    total_count,
                                    len(auto_game.left_teams)
                                    * len(auto_game.right_teams)
                                    * option.num
                                    - total_count,
                                )
                                print(msg)

                    # if finished processes are found, "endgame.sh" will be executed
                    while finished_procs["proc"] and finished_procs["setting"]:
                        p = finished_procs["proc"].pop(0)
                        s = finished_procs["setting"].pop(0)
                        subprocess.Popen(
                            [
                                "./gametools/endgame.sh",
                                s[0],
                                s[1],
                                s[2]["path"],
                                str(s[3]),
                                s[4]["path"],
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )

                    for i, h in enumerate(available_hostlist):
                        check = (
                            subprocess.run(
                                ["./gametools/getHost.sh", h],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                            .stdout.decode("utf8")
                            .strip("\n")
                        )
                        if check == "1":
                            # the host is available
                            host = available_hostlist.pop(i)
                            break
                    if host is not None:
                        break

                # execute a game at a host
                if left_team["is_branch"]:
                    branchproc.wait()
                    print(f"Finish team building( branch = {left_team['path']}")

                msg = (
                    "Host {} is assigned (Settings: our {} gameID {} opp {})\n".format(
                        host, left_team["path"], game, rigth_team["path"]
                    )
                )
                print(msg)

                proc = subprocess.Popen(
                    [
                        "./gametools/startgame.sh",
                        dirname,
                        host,
                        left_team["path"],
                        str(game),
                        rigth_team["path"],
                        boolToStr(left_team["is_branch"]),
                        boolToStr(left_team["is_synch"] and rigth_team["is_synch"]),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # append process information
                working_procs["proc"].append(proc)
                working_procs["setting"].append(
                    [dirname, host, left_team, game, rigth_team]
                )

    # wait all process
    for subproc in working_procs["proc"]:
        subproc.wait()

    # all working processes are finished
    while working_procs["proc"] and working_procs["setting"]:
        p = working_procs["proc"].pop(0)
        s = working_procs["setting"].pop(0)
        subprocess.run(
            [
                "./gametools/endgame.sh",
                s[0],
                s[1],
                s[2]["path"],
                str(s[3]),
                s[4]["path"],
            ]
        )
        # recover available hostlist (but not needed)
        available_hostlist.append(s[1])

    # write results in ggss
    read_count = 0
    write_count = 0
    for setting in all_settings:
        dirname = setting[0]
        left_team = setting[1]
        rigth_team = setting[2]
        print(left_team, rigth_team)

        # initialize
        count = 0
        result_map = {
            "n_games": 0,
            "win": 0.0,
            "draw": 0.0,
            "lose": 0.0,
            "win_rate": 0.0,
            "our_score": 0.0,
            "opp_score": 0.0,
            "our_possession": 0.0,
            "our_passes": 0.0,
            "opp_passes": 0.0,
            "our_through_passes": 0.0,
            "opp_through_passes": 0.0,
            "our_shoot": 0.0,
            "opp_shoot": 0.0,
            "dead_players": [],
        }

        # calculate analyzed results
        for i, line in enumerate(open("./log/{}/results.csv".format(dirname), "r")):
            tmp = line.split("\n")[0].split(",")
            result_map["win"] += 1.0 if tmp[7] == "3" else 0
            result_map["win_rate"] += 1.0 if tmp[7] == "3" else 0
            result_map["draw"] += 1.0 if tmp[7] == "1" else 0
            result_map["lose"] += 1.0 if tmp[7] == "0" else 0
            result_map["our_score"] += float(tmp[3])
            result_map["opp_score"] += float(tmp[4])
            result_map["our_possession"] += float(tmp[10])
            result_map["our_passes"] += float(tmp[14])
            result_map["opp_passes"] += float(tmp[19])
            result_map["our_through_passes"] += float(tmp[24])
            result_map["opp_through_passes"] += float(tmp[25])
            result_map["our_shoot"] += float(tmp[30])
            result_map["opp_shoot"] += float(tmp[31])
            if int(tmp[38]) > 0:
                result_map["dead_players"].append(tmp[0])
            count += 1

        result_map["n_games"] = count

        # average
        for key in result_map.keys():
            if (
                key == "win"
                or key == "draw"
                or key == "lose"
                or key == "n_games"
                or key == "dead_players"
            ):
                continue
            result_map[key] /= float(count)

        # reformat
        result_map["dead_players"] = ",".join(result_map["dead_players"])

        # write result_map to ggss
        if write_count >= 80 or read_count >= 80:
            # write requests are restricted per 100 seconds
            print(
                "Requests for Google Spread Sheet are restricted per 100 seconds. Please wait..."
            )
            time.sleep(100)
            write_count = 0
            read_count = 0
        tmp_read_count, tmp_write_count = ggssapi.writeResults(
            dt_now, left_team, rigth_team, result_map
        )
        read_count += tmp_read_count
        write_count += tmp_write_count
        print("r:", read_count)
        print("w:", write_count)

    msg = "ORDER:" + dt_now + " finish!"
    print(msg)


def main():
    option = Config.loadFile("./order/match_test.json")
    doGame(option)


if __name__ == "__main__":
    print("start autogame")
    main()
