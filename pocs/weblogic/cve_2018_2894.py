import sys
import requests
from config.config_requests import headers

VUL=['CVE-2018-2894']


def islive(ur,port):
    url='http://' + str(ur)+':'+str(port)+'/ws_utc/begin.do'
    r1 = requests.get(url, headers=headers)
    url='http://' + str(ur)+':'+str(port)+'/ws_utc/config.do'
    r2 = requests.get(url, headers=headers)
    return r1.status_code,r2.status_code

def run(rip,rport=7001):
    a,b=islive(rip,rport)
    if a == 200 or b == 200:
        return (VUL[0], 'http://' + rip + ':' + str(rport) + '/ws_utc/config.do')
    else:
        return None

if __name__=="__main__":
    if len(sys.argv) < 2:
        print('Usage: {} <ip> [port]'.format(sys.argv[0]))
        sys.exit()

    print(run(sys.argv[1],sys.argv[2]) if len(sys.argv)==3 else run(sys.argv[1]))