pid=0
while true
do
    if [ $pid -eq 0 ]
    then
        # 写入日志
        time=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$time] start project" >> log/run.log
        python3 main.py &
        pid=$!
    fi

    tem=$(ps -ef | grep $pid)
    if [ -z "$tem" ] # 如果进程不存在
    then
        # 写入日志
        time=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$time] project is down, restart project" >> log/run.log
        pid=0
    fi
    sleep 10
done
