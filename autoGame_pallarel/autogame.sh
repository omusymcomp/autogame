#!/bin/bash

export LD_LIBRARY_PATH=$HOME/rcss/tools/lib:$LD_LIBRARY_PATH
export PATH=$HOME/rcss/tools/bin:$PATH

#日付のファイルを指定場所に作る
DATE=`date +%Y%m%d%0k%M%s`
mkdir ./log/${DATE}

LOGDIR="./log/${DATE}"
# game loop
TEAM_R="./Teams/CYRUS2022/bin/startAll"
TEAM_L="$HOME/rcss/ham/omuHam/src/start.sh"

PORT=$1
coach_PORT=$(($PORT+1))
olcoach_PORT=$(($PORT+2))
echo $PORT

REL_POS=$2
echo $REL_POS

# シンクモードを利用するかどうか
SYNCH='true'
# ログを圧縮するかどうか 0->圧縮しない，1~->圧縮する
COMPRESS=1


echo "--------------------"
echo " ${TEAM_L} vs ${TEAM_R}"
echo "--------------------"

team_l="'${TEAM_L} -p ${PORT} -P ${olcoach_PORT} -rp ${REL_POS}'"
team_r="'${TEAM_R} -p ${PORT} -P ${olcoach_PORT}'"

rcssserver server::auto_mode = 1 \
           server::synch_mode = ${SYNCH} \
           server::team_l_start = ${team_l} \
	   server::team_r_start = ${team_r} \
	   server::port=${PORT} \
	   server::coach_port=${coach_PORT} \
	   server::olcoach_port=${olcoach_PORT} \
	   server::kick_off_wait = 50 \
	   server::half_time = 300 \
	   server::nr_normal_halfs = 2 \
	   server::nr_extra_halfs = 0 \
	   server::penalty_shoot_outs = 0 \
	   server::game_logging = 1 \
	   server::text_logging = 1 \
	   server::game_log_dir = "${LOGDIR}" \
	   server::text_log_dir = "${LOGDIR}" \
	   server::game_log_compression=${COMPRESS} \
	   server::text_log_compression=${COMPRESS} &

	   2>&1 | tee ${LOGDIR}/${DATE}.log
wait $!

