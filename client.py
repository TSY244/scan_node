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

    return redis_host, redis_port,redis_password,message_name

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

        loguru.logger.info(f"get message ==> ip is {value}")    
        g_use_ips.append(value)
        return value         

def worker(redis: my_redis.Redis):
    '''
    worker function
    '''
    
    # ip size is 10

    while True:
        if g_debug==1:
            value="192.168.79.1"
        else:
            value=get_ip(redis)
        # check if ip can connect
        if not ip_tools.check_ip_if_connectable(value):
            # add ack value
            redis.add_ack_value(value, value)
            continue

        if g_debug==1:
            with open("client_test.txt",'w+b') as f:
                f.write(value.encode())

        # scan port
        ports = Scan_port.run(value)
        
        
        # get area
        area=Area.run(value)

        # subdomain

        # webfile
        

        # Fingerprint collection

        # Vulnerability detection




        

        
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
    redis_host, redis_port,redis_password,message_queue_name= get_config()

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

    worker(redis=redis)

def test(ip):
    ports = Scan_port.run(ip)
    print(ports)

    area=Area.run(ip)
    print(area)
    

    

if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
    # test('8.130.123.25')