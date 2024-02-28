import sys
import loguru
import configparser
import signal
import os 
import time 

now_path=sys.path[0]
sys.path.append(now_path[:now_path.rfind('\\')])
import tools.redis_tools.my_redis as my_redis
import tools.ip_tools.ip_tools as ip_tools
import info_gathering.scan_port.scan_port as Scan_port
import info_gathering.areas.areas as Area
import tools.TideFinger.TideFinger as TideFinger
import tools.vulmap.run as Vulmap
import tools.read_scan_vuls_ret as read_vuls
import tools.UseElasticSearch.UseElasticSearch as ES


# init loguru
# loguru.logger.add("server.log", rotation="500 MB", retention="10 days", level="INFO")
loguru.logger.add("/log/error.log", rotation="500 MB", retention="10 days", level="ERROR")



g_debug=0

g_use_ips=[]


def signal_handler(signal, frame):
    loguru.logger.error("exit")
    pid=os.getpid()
    os.kill(pid,signal)

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    redis_host = config['REDIS']['redis_host']
    redis_port = config['REDIS']['redis_port']
    redis_password = config['REDIS']['redis_password']
    message_name = config['REDIS']['message_queue']

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


    return redis_host, redis_port,redis_password,message_name,es

def get_ip(redis: my_redis.Redis):
    value = None
    global g_use_ips
    while True:
        if redis.check_ack_if_hava_value():
            key, value = redis.get_ack_value()
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
    if es_index is None, use default index - "vuls"
    '''
    if len(es)!=4 or "es_host" not in es or "es_port" not in es or "es_info_index" not in es or "es_vuls_index" not in es:
        raise Exception("es config error")
    if not ip_tools.check_ip_if_valid(es["es_host"]):
        raise Exception("es_host is invalid")
    if not ip_tools.check_port_if_valid(es["es_port"]):
        raise Exception("es_port is invalid")
    if es["es_info_index"]!=None and not isinstance(es["es_info_index"],str):
        raise Exception("es_index is invalid")
    if es["es_vuls_index"]!=None and not isinstance(es["es_vuls_index"],str):
        raise Exception("es_index is invalid")
    return True

def worker(redis: my_redis.Redis,es:dict):
    '''
    worker function
    es is a dict
        key                   vlues
        es_host:str           str
        es_port:int           int
        es_info_index:str     str     #if not exist, use None. use default index - "info"
        es_vuls_index:str     str     #if not exist, use None. use default index - "vuls" 
    '''
    
    # check es 
    try:
        check_es(es)
    except Exception as e:
        loguru.logger.error(e)
        sys.exit(1)

    es["es_port"]=int(es["es_port"]) if type(es["es_port"])==str else es["es_port"]

    # ip size is 10
    while True:
        if g_debug==1:
            value="192.168.79.128"
        else:
            value=get_ip(redis)
        # check if ip can connect
        if not ip_tools.check_ip_if_connectable(value):
            # add ack value
            redis.add_ack_value(value, value)
            continue
        loguru.logger.info(f"get ip ==> ip is {value}")

        # scan port
        temp = Scan_port.run(value) # return is a dict_keys
        ports = list(temp)
        if g_debug==1:
            loguru.logger.info(f"scan port ==> ports is {ports}")
        
        # get area
        area=Area.run(value)
        if g_debug==1:
            loguru.logger.info(f"get area ==> area is {area}")

        # subdomain

        # web file
        
        # Fingerprint collection
        no_scan_ports=["20","21","22","25","53","80","110","143","443","1433","3389"]
        fingerprint=None
        tide=[]
        if g_debug==1:
            ports=["8080"]
        for port in ports:
            if port in no_scan_ports:
                continue
            fingerprint=TideFinger.run(value,port)  # return is a dict
            if len(fingerprint["banner"]) != 0:
                tide+=fingerprint["banner"]
            if fingerprint["cms_name"]!="Not Found":
                tide.append(fingerprint["cms_name"])
        
        # Vulnerability detection
        for port in ports:
            Vulmap.start(value,str(port))
        vuls=read_vuls.read_data("ret/vuls.txt")

        # crete info data
        info_data={}
        vul_numbs=[]
        for vul in vuls:
            vul=eval(vul)
            vul_numbs.append(vul["vul_numb"])
        info_data["site"]=value # ip is a string
        info_data["ports"]=ports # ports is a list
        info_data["area"]=area # area is a string
        info_data["fingerprint"]=fingerprint # fingerprint is a dict
        info_data["vuls"]=vul_numbs # vuls is a list

        # send info data to es
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
            
        # crete vuls data
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

        # notice
        if g_debug==1:
            loguru.logger.info("test")
            break

        # 

        
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


def main():
    redis_host, redis_port,redis_password,message_queue_name,es= get_config()

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
    worker(redis=redis,es=es)

def test(ip,port):
    ret=TideFinger.run(ip,port)
    print(ret)

    

if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
    # test('192.168.79.128',8080)