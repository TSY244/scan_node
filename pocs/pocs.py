import sys

try:
    import pocs.weblogic as weblogic
except:
    import weblogic as weblogic

def run(rip,rport=7001):
    if weblogic.identification.check(rip,rport):
        print("Weblogic is running")
        result = weblogic.weblogic_scan.result(rip,rport)
        return result 


if __name__ == "__main__":
    run("192.168.79.128", 7001)