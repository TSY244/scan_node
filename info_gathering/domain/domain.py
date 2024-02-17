import requests
import re

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
TIMEOUT = 10
cmp = re.compile(r'{"domain":"http:\\/\\/(.*?)","title":".*?"}')      



def get_domain(ip):
    url = r'http://api.webscan.cc/?action=query&ip={}'.format(ip)
    try:
        ret=requests.get(url,headers=headers,timeout=TIMEOUT)
        text=ret.text
        if text:
            results=eval(text) 
            for result in results:
                domain=result['domain']
                if re.match(r"w{3}.*.com",domain):
                    print(domain)
                    return domain
    except Exception as e:
        print(e)
        return None
    
def run(ip):
    return get_domain(ip)

if __name__ == '__main__':
    get_domain('218.76.8.98')