import requests
import config.config_requests as cr
import sys

VUL=['CVE-2014-4210']

def is_liva(ip,port,url):
    result=requests.get(url,timeout=5,headers=cr.headers)
    return result.status_code==200

def run(ip,port=7001):
    url='http://' + str(ip)+':'+str(port)+'/uddiexplorer/'
    if is_liva(ip,port,url):
        return (VUL[0],url)
    else:
        return None
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} <ip> [port]'.format(sys.argv[0]))
        sys.exit()
    print(run(sys.argv[1],sys.argv[2]) if len(sys.argv)==3 else run(sys.argv[1]))