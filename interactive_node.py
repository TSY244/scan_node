import socket
import configparser
import loguru
import client


# init loguru
loguru.logger.add("log/error.log", rotation="1 MB", retention="10 days", level="DEBUG")


def get_config():
    config=configparser.ConfigParser()  
    config.read('config.ini')

    # server
    server_ip=config["COMMON"]["server_ip"]
    server_port = int(config["COMMON"]["server_port"])
    server_addr=(server_ip, server_port)

    return server_addr

def iteractive_node():
    '''
    a iteractive node
    '''
    server_addr=get_config()

    # create a iteractive node manager
    try:
        i_node_manager=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        i_node_manager.connect(server_addr)
    except Exception as e:
        loguru.logger.error(f"connect to server failed: {e}")
        return
    
    # woker
    while True:
        cmd=i_node_manager.recv(1024).decode()
        print(cmd)


if __name__ == "__main__":
    iteractive_node()    
    
