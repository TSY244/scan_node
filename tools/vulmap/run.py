import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.dirname(os.path.abspath(__file__)))

import identify.identify as identify
import module.globals as globals
import module.api.dns as dns
import core.scan as scan
import core.core as core
from  gevent  import joinall
from concurrent.futures import ThreadPoolExecutor,wait,ALL_COMPLETED
import payload.RadHatJBoss as rj
from module.argparse import arg
import loguru
import tools.ip_tools.ip_tools as ip_tools

import payload.RadHatJBoss as RadHatJBoss

# init log
loguru.logger.add("log/error.log", rotation="5 MB", retention="10 days", level="ERROR")


def config(args):
    header = {
        'Accept': 'application/x-shockwave-flash, image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, '
                  'application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
        'User-agent': args.ua,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'close'
    }
    globals.init()  # 初始化全局变量模块
    globals.set_value("UA", args.ua)  # 设置全局变量UA
    globals.set_value("VUL", None)  # 设置全局变量VULN用于判断是否漏洞利用模式
    globals.set_value("CHECK", args.check)  # 目标存活检测
    globals.set_value("DEBUG", args.debug)  # 设置全局变量DEBUG
    globals.set_value("DELAY", args.delay)  # 设置全局变量延时时间DELAY
    globals.set_value("DNSLOG", args.dnslog)  # 用于判断使用哪个dnslog平台
    globals.set_value("DISMAP", "flase") # 是否接收dismap识别结果(false/true)
    globals.set_value("VULMAP", str(0.9))  # 设置全局变量程序版本号
    globals.set_value("O_TEXT", args.O_TEXT)  # 设置全局变量OUTPUT判断是否输出TEXT
    globals.set_value("O_JSON", "ret\\vuls.txt")  # 设置全局变量OUTPUT判断是否输出JSON
    globals.set_value("HEADERS", header)  # 设置全局变量HEADERS
    globals.set_value("TIMEOUT", args.TIMEOUT)  # 设置全局变量超时时间TOMEOUT
    globals.set_value("THREADNUM", args.thread_num)  # 设置全局变量THREADNUM传递线程数量

    # 替换自己的 ceye.io 的域名和 token
    globals.set_value("ceye_domain","xxxxxxxxxx")
    globals.set_value("ceye_token", "xxxxxxxxxx")

    # 替换自己的 http://hyuga.co 的域名和 token
    # hyuga的域名和token可写可不写，如果不写则自动获得
    globals.set_value("hyuga_domain", "xxxxxxxxxx")
    globals.set_value("hyuga_token", "xxxxxxxxxx")

    # fofa 邮箱和 key，需要手动修改为自己的
    globals.set_value("fofa_email", "xxxxxxxxxx")
    globals.set_value("fofa_key", "xxxxxxxxxx")

    # shodan key
    globals.set_value("shodan_key", "xxxxxxxxxx")


def test(url):
    rhj=RadHatJBoss.RedHatJBoss(url)
    rhj.cve_2010_0738_poc()
    rhj.cve_2010_1428_poc()
    rhj.cve_2015_7501_poc()
    rhj.cve_2017_12149_poc()

def start(ip,port:str):

    args=arg()

    config(args)

    webapps_identify=[]
    target="http://"+ip+":"+port
    thread_poc = [] 
    gevent_pool = [] 
    t_num = 10  
    thread_pool = ThreadPoolExecutor(t_num) 

    if dns.dns_request():
        pass
    else:
        loguru.logger.error("dns request failed")
        return

    scan_web_info=identify.Identify(target)
    if scan_web_info is None:
        loguru.logger.error("web_info is None")
        return
    
    if not ip_tools.check_ip_if_connectable(ip):
        loguru.logger.error("ip is not connectable")
        return

    # test(target)
    use_core=core.Core()
    scan_web_info.start(target,webapps_identify)
    use_core.scan_webapps(webapps_identify, thread_poc, thread_pool,gevent_pool,target)
    joinall(gevent_pool)
    wait(thread_poc, return_when=ALL_COMPLETED)
