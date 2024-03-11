from multiprocessing import Process
import client
import interactive_node
import configparser

g_config=configparser.ConfigParser()
g_config.read('config.ini')
g_mode=g_config["COMMON"]["mode"]

    


def main():
    if g_mode==1:
        interactive_node.iteractive_node()
    else:
        client.client()

if __name__ == "__main__":
    main()    