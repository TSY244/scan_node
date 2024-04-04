import sys
import loguru
import configparser
import signal
import os 
import time 
import tools.redis_tools.my_redis as my_redis
import tools.ip_tools.ip_tools as ip_tools
import info_gathering.scan_port.scan_port as Scan_port
import info_gathering.areas.areas as Area
import tools.TideFinger.TideFinger as TideFinger
import tools.vulmap.run as Vulmap
import tools.read_scan_vuls_ret as read_vuls
import tools.UseElasticSearch.UseElasticSearch as ES
import info_gathering.web_path_scanner.scanner as web_path_scanner
import info_gathering.subdomain.subdomain as subdomain
import info_gathering.domain.domain as domain

# init loguru
# loguru.logger.add("server.log", rotation="500 MB", retention="10 days", level="INFO")
loguru.logger.add("log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

config=configparser.ConfigParser()
config.read("config.ini")
g_debug=int(config["COMMON"]["debug"])
if_use_log=int(config["COMMON"]["use_log"])

g_use_ips=[]
g_time=0

def signal_handler(signal, frame):
    loguru.logger.error("exit,beacuse of {} signal".format(signal))
    pid=os.getpid()
    os.kill(pid,signal)

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # redis
    redis_host = config['REDIS']['redis_host']
    redis_port = config['REDIS']['redis_port']
    redis_password = config['REDIS']['redis_password']
    message_name = config['REDIS']['message_queue']
    redis={
        "redis_host":redis_host,
        "redis_port":redis_port,
        "redis_password":redis_password,
        "message_name":message_name
    }

    # elasticsearch
    es_host = config['elasticsearch']['host']
    es_port = config['elasticsearch']['port']
    es_info_index = config['elasticsearch']['info_index']
    es_vuls_index = config['elasticsearch']['vuls_index']
    es = {
        "es_host": es_host,
        "es_port": es_port,
        "es_info_index": es_info_index,
        "es_vuls_index": es_vuls_index
    }

    # web_path_scan
    wpc_mode=config['web_path_scanner']['mode']
    wpc_thread=config['web_path_scanner']['thread']
    if wpc_mode=="file":
        wpc_file_name=config['web_path_scanner']['file_name']
        web_path_scan={
            "mode":wpc_mode,
            "file_name":wpc_file_name,
            "thread":int(wpc_thread)
        }
    elif wpc_mode=="dir":
        wpc_file_path=config['web_path_scanner']['file_path']
        web_path_scan={
            "mode":wpc_mode,
            "file_path":wpc_file_path,
            "thread":int(wpc_thread)
        }
    else:
        raise Exception("web_path_scanner mode is error")

    # subdomain_scanner
    subdomain_thread=config['subdomain_scanner']['thread']
    subdomain_mode=config['subdomain_scanner']['mode']
    if subdomain_mode=="file":
        subdomain_file_name=config['subdomain_scanner']['file_name']
        subdomain_scan={
            "mode":subdomain_mode,
            "file_name":subdomain_file_name,
            "thread":int(subdomain_thread)
        }
    elif subdomain_mode=="dir":
        subdomain_file_path=config['subdomain_scanner']['file_path']
        subdomain_scan={
            "mode":subdomain_mode,
            "file_path":subdomain_file_path,
            "thread":int(subdomain_thread)
        }
    else:
        raise Exception("subdomain_scanner mode is error")
    
    return redis,es,web_path_scan,subdomain_scan

def get_ip(redis: my_redis.Redis):
    value = None
    global g_use_ips
    while True:
        if redis.check_ack_if_hava_value():
            key, value = redis.get_ack_value()
            if value ==None:
                time.sleep(10)
                continue
            value = value.decode()
            if value in g_use_ips:
                value = redis.get_message().decode()
                redis.add_ack_value(key, value)
        else:
            value = redis.get_message().decode()

        if value == None:
            return None
            
        if len(g_use_ips) >= 10:
            for i in range(5):
                g_use_ips.pop(0)

        # loguru.logger.info(f"get message ==> ip is {value}")    
        g_use_ips.append(value)
        return value         

def check_es(es:dict):
    '''
    check es config, if not valid, raise Exception
    '''
    if len(es)!=4 or "es_host" not in es or "es_port" not in es or "es_info_index" not in es or "es_vuls_index" not in es:
        raise Exception("es config error")
    if not ip_tools.check_ip_if_valid(es["es_host"]):
        raise Exception("es_host is invalid")
    if not ip_tools.check_port_if_valid(es["es_port"]):
        raise Exception("es_port is invalid")
    if es["es_info_index"]!=None and not isinstance(es["es_info_index"],str):
        raise Exception("es_info_index is invalid")
    if es["es_vuls_index"]!=None and not isinstance(es["es_vuls_index"],str):
        raise Exception("es_vuls_index is invalid")
    return True


def check_web_path_scan(web_path_scan:dir): # delete you can use check_scanner
    if len(web_path_scan)!=3:
        raise Exception("web_path_scan config error")
    if web_path_scan["mode"] not in ["file","dir"]:
        raise Exception("web_path_scan mode is invalid")
    if not isinstance(web_path_scan["thread"],int):
        raise Exception("web_path_scan thread is invalid")
    if web_path_scan["mode"]=="file" and web_path_scan["file_name"]==None:
        raise Exception("web_path_scan file_name is None")
    if web_path_scan["mode"]=="dir" and web_path_scan["file_path"]==None:
        raise Exception("web_path_scan file_path is None")
    return True

def check_subdomain_scan(subdomain_scan:dir): # delete you can use check_scanner
    if len(subdomain_scan)!=3:
        raise Exception("subdomain_scan config error")
    if subdomain_scan["mode"] not in ["file","dir"]:
        raise Exception("subdomain_scan mode is invalid")
    if not isinstance(subdomain_scan["thread"],int):
        raise Exception("subdomain_scan thread is invalid")
    if subdomain_scan["mode"]=="file" and subdomain_scan["file_name"]==None:
        raise Exception("subdomain_scan file_name is None")
    if subdomain_scan["mode"]=="dir" and subdomain_scan["file_path"]==None:
        raise Exception("subdomain_scan file_path is None")
    return True

# todo check if exist path or file 
def check_scanner(scanner:dir):
    '''
    check scanner config, you can use web_path_scan ,subdomain_scan
    '''
    if len(scanner)!=3:
        raise Exception(f"scanner {scanner} config error")
    if scanner["mode"] not in ["file","dir"]:
        raise Exception(f"scanner {scanner} mode is invalid")
    if not isinstance(scanner["thread"],int):
        raise Exception(f"scanner {scanner} thread is invalid")
    if scanner["mode"]=="file" and scanner["file_name"]==None:
        raise Exception(f"scanner {scanner} file_name is None")
    if scanner["mode"]=="dir" and scanner["file_path"]==None:
        raise Exception(f"scanner {scanner} file_path is None")
    return True

def check_redis(redis_host, redis_port,redis_password):
    # each 5 seconds, try to connect redis, and connect 100 times 
    now_times=0
    max_times=100

    ip_tools.check_ip_if_valid(redis_host)

    try:
        while now_times<max_times:
            if my_redis.Redis.check_if_connectable(redis_host, redis_port, redis_password):
                return
            loguru.logger.info("can't connect redis")
            now_times+=1
            time.sleep(5)
        raise Exception
    except:
        loguru.logger.error("redis connect error")
        sys.exit(1)

def worker(redis: my_redis.Redis,es:dict,web_path_scan:dir=None,subdomain_scan:dir=None):
    '''
    worker function
    es is a dict
        key                   vlues
        es_host:str           str
        es_port:int           int
        es_info_index:str     str     #if not exist, use None. use default index - "info"
        es_vuls_index:str     str     #if not exist, use None. use default index - "vuls" 
    web_path_scan is a dir
        key                   vlues
        mode:str              str     #file or dir
        thread:int            int     #thread number
        file_path:str         str     #file path
        file_name:str         str     #file name
    subdomain_scan is a dir
        key                   vlues
        mode:str              str     #file or dir
        file_path:str         str     #file path
        file_name:str         str     #file name
        thread:int            int     #thread number
        ; if file_path is not "" use file_path, else use file_name
    '''
    
    # check es 
    try:
        check_es(es)
    except Exception as e:
        loguru.logger.error(e)
        sys.exit(1)
    es["es_port"]=int(es["es_port"]) if type(es["es_port"])==str else es["es_port"]

    # check web_path_scan
    try:
        check_web_path_scan(web_path_scan)
    except Exception as e:
        loguru.logger.error(e)
        sys.exit(1)

    # check web path scan
    try:
        check_scanner(web_path_scan)
    except Exception as e:
        loguru.logger.error(e)
        sys.exit(1)
    
    # check subdomain_scan
    try:
        check_scanner(subdomain_scan)
    except Exception as e:
        loguru.logger.error(e)
        sys.exit(1)

    # ip size is 10
    while True:
        if g_debug==1:
            value="192.168.79.137"
        else:
            value=get_ip(redis)
        # check if ip can connect
        if not ip_tools.check_ip_if_connectable(value):
            # add ack value
            redis.add_ack_value(value, value)
            continue
        loguru.logger.info(f"get ip ==> ip is {value}")

        # scan port
        if if_use_log==1:
            loguru.logger.info(f"begin scan port, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        temp = Scan_port.run(value) # return is a dict_keys
        if temp==None: # error
            continue
        ports = list(temp)
        if g_debug==1:
            loguru.logger.info(f"scan port ==> ports is {ports}")
        if if_use_log==1:
            loguru.logger.info(f"scan port end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # get area
        if if_use_log==1:
            loguru.logger.info(f"begin get area, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        area=Area.run(value)
        area=area.split(" ")
        ares=[i for i in area if i!=""]
        area=ares
        if g_debug==1:
            loguru.logger.info(f"get area ==> area is {area}")
        if if_use_log==1:
            loguru.logger.info(f"get area end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # domain 
        if if_use_log==1:
            loguru.logger.info(f"begin get domain, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        value2domian=domain.run(value)
        if g_debug==1:
            loguru.logger.info(f"get domain ==> domain is {value2domian}")
        if if_use_log==1:
            loguru.logger.info(f"get domain end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # subdomain
        if if_use_log==1:
            loguru.logger.info(f"begin get subdomains, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        subdomains=None
        if value2domian !=None:
            subdomain_thread_num=subdomain_scan["thread"]
            if subdomain_scan["mode"]=="file":
                subdomain_file_name=subdomain_scan["file_name"]
            elif subdomain_scan["mode"]=="dir":
                subdomain_file_path=subdomain_scan["file_path"]
            subdomain_scanner=subdomain.subdomain_scanner(value2domian[4:],threads=subdomain_thread_num,file_path=subdomain_file_path,file_name=subdomain_file_name)
            subdomains=subdomain_scanner.get_subdomains()
        if g_debug==1:
            loguru.logger.info(f"get subdomains ==> subdomains is {subdomains}")
        if if_use_log==1:
            loguru.logger.info(f"get subdomains end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # web file
        if if_use_log==1:
            loguru.logger.info(f"begin get web path, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        web_path_scan_mode=web_path_scan["mode"]
        thread_num=web_path_scan["thread"]
        if web_path_scan_mode=="file":
            web_path_file_name=web_path_scan["file_name"]
        elif web_path_scan_mode=="dir":
            web_path_file_path=web_path_scan["file_path"]
        web_path=None
        if web_path_scan_mode=="file":
            web_path=web_path_scanner.scanner(value,file_name=web_path_file_name,threads=thread_num)
        elif web_path_scan_mode=="dir":
            web_path=web_path_scanner.scanner(value,file_path=web_path_file_path,threads=thread_num)
        web_path=list(set(web_path))
        if g_debug==1:
            loguru.logger.info(f"get web path ==> web_path is {web_path}")
        if if_use_log==1:
            loguru.logger.info(f"get web path end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # Fingerprint collection
        if if_use_log==1:
            loguru.logger.info(f"begin Fingerprint collection, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        no_scan_ports=["20","21","22","25","53","80","110","143","443","1433","3389"]
        fingerprint=None
        tide=[]
        if g_debug==1:
            ports=["8080"]
            
        for port in ports:
            if str(port) in no_scan_ports:
                loguru.logger.info(f"port {port} is not scan")
                continue
            fingerprint=TideFinger.run(value,port)  # return is a dict
            if len(fingerprint["banner"]) != 0:
                for i in fingerprint["banner"]:
                   tide.append(i) 
            if fingerprint["cms_name"]!="Not Found":
                tide.append(fingerprint["cms_name"])
        tide=list(set(tide))
        if g_debug==1:
            loguru.logger.info(f"Fingerprint collection ==> fingerprint is {tide}")
        if if_use_log==1:
            loguru.logger.info(f"Fingerprint collection end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # Vulnerability detection
        if if_use_log==1:
            loguru.logger.info(f"begin Vulnerability detection, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        if g_debug==1:
            ports=["8080"]
        for port in ports:
            Vulmap.start(value,str(port))
        vuls=read_vuls.read_data("ret/vuls.txt")
        if g_debug==1:
            loguru.logger.info(f"Vulnerability detection ==> vuls is {vuls}")
        if if_use_log==1:
            loguru.logger.info(f"Vulnerability detection end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # crete info data
        if if_use_log==1:
            loguru.logger.info(f"begin create info data, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        info_data={}
        vul_numbs=[]
        for vul in vuls:
            vul=eval(vul)
            vul_numbs.append(vul["vul_numb"])
        info_data["site"]=value # ip is a string
        info_data["ports"]=ports # ports is a list
        info_data["area"]=area # area is a list
        info_data["tide"]=tide # tide is a list
        info_data["vuls"]=vul_numbs # vuls is a list
        info_data["web_path"]=web_path # web_path is a list
        info_data["domain"]=value2domian # domain is a string
        info_data["subdomains"]=subdomains # subdomains is a list
        if g_debug==1:
            loguru.logger.info(f"create info data ==> info_data is {info_data}")
        if if_use_log==1:
            loguru.logger.info(f"create info data end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # send info data to es
        if if_use_log==1:
            loguru.logger.info(f"begin send info data to es, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        use_es=ES.MyElasticSearch(es["es_host"],es["es_port"])
        try:
            use_es.connect()
            if es["es_info_index"]==None:
                use_es.create_index("info")
                es["es_info_index"]="info"
            else:
                use_es.create_index(es["es_info_index"])
            use_es.insert_data(es["es_info_index"],info_data)
        except Exception as e:
            loguru.logger.error(e)
        if g_debug==1:
            loguru.logger.info("send info data to es")
        if if_use_log==1:
            loguru.logger.info(f"send info data to es end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # crete vuls data
        if if_use_log==1:
            loguru.logger.info(f"begin send vuls to es, start time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")
        for vul in vuls:
            vul_data={}
            vul=eval(vul)
            vul_data["site"]=value
            vul_data["prt_name"]=vul["prt_name"]
            vul_data["vul_name"]=vul["vul_name"]
            vul_data["vul_numb"]=vul["vul_numb"]
            vul_data["vul_type"]=vul["vul_type"]
            vul_data["vul_urls"]=vul["vul_urls"]
            vul_data["vul_payd"]=vul["vul_payd"]
            try:
                if es["es_vuls_index"]==None:
                    use_es.create_index("vuls")
                else:
                    use_es.create_index(es["es_vuls_index"])
                use_es.insert_data(es["es_vuls_index"],vul_data)
            except Exception as e:
                loguru.logger.error(e)
                continue
            if g_debug==1:
                loguru.logger.info(f"send vuls is {vul_data}")
        if if_use_log==1:
            loguru.logger.info(f"send vuls to es end, end time is {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}")

        # notice
        if g_debug==1:
            loguru.logger.info("run all")

        # clear all ret, and into next loop
        try:
            if os.path.exists("ret/vuls.txt"):
                with open("ret/vuls.txt","w") as f: # clear vuls.txt
                    f.write("") 
                loguru.logger.info("clear vuls.txt")
        except Exception as e:
            loguru.logger.error(e)

def client():

    redis,es,wps,subdomain= get_config()

    redis_host=redis["redis_host"]
    redis_port=redis["redis_port"]
    redis_password=redis["redis_password"]
    message_queue_name=redis["message_name"]

    if redis_password== "None" or redis_password == "":
        redis_password = None

    # check redis host and port
    check_redis(redis_host, redis_port,redis_password)
    
    # init redis
    redis = my_redis.Redis(redis_host=redis_host,
                           redis_port=redis_port,
                           redis_password=redis_password,
                           message_name=message_queue_name)
    redis.connect()


    # run worker
    worker(redis=redis,es=es,web_path_scan=wps,subdomain_scan=subdomain)

def test(ip:str,port):
    # ret=TideFinger.run(ip,str(port))
    # print(type(ret))
    # print(ret)
    es=ES.MyElasticSearch("192.168.79.128",9200)
    es.connect()
    es.insert_data("vuls",{"site":"1","prt_name":"1","vul_name":"1","vul_numb":"1","vul_type":"1","vul_urls":"1","vul_payd":"1"})

if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    client()
    # test('192.168.79.128',8080)