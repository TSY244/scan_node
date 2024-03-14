from multiprocessing import Process
import client
import interactive_node
import configparser
import signal
import os
import sys


g_config=configparser.ConfigParser()
g_config.read('config.ini')
g_mode=g_config["COMMON"]["mode"]

def signal_handler(signum, frame):
    print(f"signal {signum} received")
    with open("pid.txt", "r") as f:
        pid=f.read()
    if pid!="":
        os.kill(int(pid), signal.SIGILL)
    pid=os.getpid()
    os.kill(pid, signal.SIGILL)


def main():
    if g_mode=="1":
        interactive_node.iteractive_node()
    else:
        client.client()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    pid=os.getpid()
    with open("main_pid.txt", "w") as f:
        f.write(str(pid))
    main()    