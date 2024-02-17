import configparser
import os
import sys
from threading import Lock

try:
    import info_gathering.scan_port.nmap as nmap
except:
    import nmap
try:
    from server.tools import ip_tools as ip_tools
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..\\..\\ip_tools'))
    import server.tools.ip_tools as ip_tools


g_ports=[]
g_lock=Lock()

def getConfig():
    config=configparser.ConfigParser()
    config.read("config.ini")
    ports=config["PORT_RANGE"]["port"]
    return ports

def get_port_range(ports):
    ranges=ports.split(",")
    port_list=[]
    for r in ranges:
        if "-" in r:
            start,end=r.split("-")
            for port in range(int(start),int(end)+1):
                port_list.append(port)
        else:
            port_list.append(int(r))

    with open("port.txt","w") as f:
        for port in port_list:
            f.write(str(port)+"\n")
    return port_list

def scanner(host,port):
    try:
        nm=nmap.PortScanner()
        nm.scan(host,ports=str(port))
        ports=nm[host]['tcp'].keys()
        return ports
    except:
        print(f"端口扫描失败")
        return []

def run(host):
    ports=getConfig()
    return scanner(host,ports)


if __name__=="__main__":
    run("127.0.0.1")
