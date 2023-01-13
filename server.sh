#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

SIGNAL="summarization.py --port 4100"
JOB_NAME="Spelling server"
WORK_PATH="/servers/podcast_summarization"
#JAVA_HOME="/usr/lib/jvm/jre-11-openjdk-11.0.17.0.8-2.el7_9.x86_64"
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64


##
cd $WORK_PATH
printf "[.] Goto working path: $WORK_PATH \n"
export PYTHONPATH=$WORK_PATH
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export JAVA_HOME=$JAVA_HOME

FIND_SERVICE=$(ps -ef | grep -v grep | grep -c "$SIGNAL")
case "$1" in	
    stop)
        echo "[.] Find service $JOB_NAME ...."
        if [ $FIND_SERVICE -gt 0 ]; then
            PROCESS_ID=$(ps -ef | grep -v grep | grep "$SIGNAL" | cut -c10-17)
            printf "[.] Service runing pid: ${GREEN} $PROCESS_ID ${NC}\n"
            kill $PROCESS_ID
            echo "[.] Stopped."
        else
            echo "[.] Service not found."
        fi
    ;;
    restart)
        echo "[.] Find service $JOB_NAME ...."
        if [ $FIND_SERVICE -gt 0 ]; then
            PROCESS_ID=$(ps -ef | grep -v grep | grep "$SIGNAL" | cut -c10-17)
            printf "[.] Service runing pid: ${GREEN} $PROCESS_ID ${NC}\n"
            kill $PROCESS_ID
            echo "[.] Stopped."
        fi
        /root/miniconda3/envs/podcast_summarization/bin/python $SIGNAL > /dev/null 2>&1 &
        echo "[.] Done."
    ;;
    *)
        echo "[.] Find service $JOB_NAME ...."
        if [ $FIND_SERVICE -gt 0 ]; then
            PROCESS_ID=$(ps -ef | grep -v grep | grep "$SIGNAL" | cut -c10-17)
            printf "[.] Service runing pid: ${GREEN} $PROCESS_ID ${NC}\n"
        else
            /root/miniconda3/envs/podcast_summarization/bin/python ./$SIGNAL > /dev/null 2>&1 &
            echo "[.] Done"
        fi
    ;;
esac
