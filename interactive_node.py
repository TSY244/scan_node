import socket
import configparser
import loguru
import client
import os
import signal
from multiprocessing import Process
import tools.FileTransfer.client_tcp as download_client

# init loguru
loguru.logger.add("log/error.log", rotation="1 MB", retention="10 days", level="ERROR")


def get_config():
    config=configparser.ConfigParser()  
    config.read('config.ini')

    # server
    server_ip=config["COMMON"]["server_ip"]
    server_port = int(config["COMMON"]["server_port"])
    server_addr=(server_ip, server_port)

    return server_addr

def get_remote_config(conn,file_path):
    download_client.run(conn, file_path)

def do_kill(client_pid):
    loguru.logger.info("server kill the client")
    os.kill(client_pid, signal.SIGILL)
    with open("pid.txt", "w") as f:
        f.write("")
    with open("main_pid.txt", "w") as f:
        f.write("1")
    pid=os.getpid()
    os.kill(pid, signal.SIGILL)

def do_stop(i_node_manager,client_p,client_pid):
    if client_p==None:
        i_node_manager.send("client has not started".encode())
    os.kill(client_pid, signal.SIGILL)
    client_p=None
    loguru.logger.info("server stop the client")
    with open("pid.txt", "w") as f:
        f.write("")

def do_start(i_node_manager,client_p,client_pid):
    if client_p!=None:
        i_node_manager.send("client has started".encode())
        client_p=Process(target=client.client)
        client_p.start()
        client_pid=client_p.pid
        loguru.logger.info("server start the client")
        with open("pid.txt", "w") as f:
            f.write(str(client_p.pid))


def iteractive_node():
    '''
    a iteractive node
    '''
    
    server_addr=get_config()

    # create a iteractive node manager
    try:
        i_node_manager=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # i_node_manager.bind(("0.0.0.0", 24456))
        i_node_manager.connect(server_addr)
    except Exception as e:
        loguru.logger.error(f"connect to server failed: {e}")
        return
    
    client_p=Process(target=client.client)
    client_p.start()
    client_pid=client_p.pid
    with open("pid.txt", "w") as f:
        f.write(str(client_pid))

    # woker
    while True:
        cmd=i_node_manager.recv(1024).decode()
        
        if cmd=="kill":
            do_kill(client_pid)
        elif cmd=="stop":
            do_stop(i_node_manager,client_p,client_pid)
        elif cmd=="start":
            do_start(i_node_manager,client_p,client_pid)
        elif cmd=="is_live":
            i_node_manager.send("yes".encode())
        elif cmd=="reload_config":
            do_stop(i_node_manager,client_p,client_pid)
            get_remote_config(i_node_manager,"config.ini")
            do_start(i_node_manager,client_p,client_pid)
            i_node_manager.send("reload config done".encode())
        else:
            i_node_manager.send("unknow command".encode())
            
            



if __name__ == "__main__":
    iteractive_node()    
    
