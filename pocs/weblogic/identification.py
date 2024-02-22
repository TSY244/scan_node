# weblogic 指纹识别
import requests
import random
import config.config_requests as cr
import re
import ping3


flag=r'.*status code SHOULD be used if the server knows, through some internally configurable mechanism, that an old resource is permanently unavailable and has no forwarding address\..*'

def get_random_str():
    return ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10))

def if_connect(ip):
    if ping3.ping(ip, timeout=1) is None:
        return False
    else:
        return True

def check(ip,port=7001): 
    if not if_connect(ip):
        return False
    
    url='http://' + str(ip)+':'+str(port)
    result=requests.get(url,timeout=5,headers=cr.headers)
    if re.match(flag,result.text, re.DOTALL):
        return True

    file_path=get_random_str()+"/"+get_random_str()+'.jsp'
    url='http://' + str(ip)+':'+str(port)+'/bea_wls_internal/'+file_path
    result=requests.get(url,timeout=5,headers=cr.headers)
    if re.match(flag,result.text, re.DOTALL):
        return True
    
    url='http://' + str(ip)+':'+str(port)+'/bea_wls_internal/'
    result=requests.get(url,timeout=5,headers=cr.headers)
    if re.match("weblogic",result.text, re.DOTALL):
        return True
    
    url='http://' + str(ip)+':'+str(port)+'/console/login/LoginForm.jsp'
    result=requests.get(url,timeout=5,headers=cr.headers)
    if re.match("WebLogic Server",result.text, re.DOTALL):
        return True
    
    url='http://' + str(ip)+':'+str(port)+'/console/login/LoginForm.jsp'
    result=requests.get(url,timeout=5,headers=cr.headers)
    if re.match("WebLogic Server",result.text, re.DOTALL):
        return True
    
    return False
