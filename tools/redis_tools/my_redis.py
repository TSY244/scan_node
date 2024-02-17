'''
use redis as message queue
'''

import redis
import loguru

# init loguru
# loguru.logger.add("redis.log", rotation="500 MB", retention="10 days", level="INFO")
loguru.logger.add("/log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

class Redis():
    def __init__(self,redis_host,redis_port,message_name,redis_password=None):
        self.__redis_host = redis_host
        self.__redis_port = redis_port
        self.__redis_password = redis_password
        self.__message_name = message_name

    def add_message(self, value):
        try:
            self.__lpush_a_value(self.__message_name, value)
            return True
        except:
            loguru.logger.error("redis add message error")
            return False
        
    def get_message(self):
        '''
        only can get first message, get one message and delete it
        '''
        try:
            value = self.__rpop_a_value(self.__message_name)
            if value:
                return value
            return None
        except:
            loguru.logger.error("redis get message error")
            return None

    def add_ack_value(self, key, value):
        '''
        add key, value from message to ack
        '''
        try:
            self.__redis_cli.set(key, value)
            return True
        except:
            loguru.logger.error("redis add ack error")
            return False
    
    def delete_ack_value(self, key):
        '''
        delete message, only message has been received
        '''
        try:
            self.__redis_cli.delete(key)
            return True
        except:
            loguru.logger.error("redis delete ack error")
            return False
    
    def get_ack_value(self):
        '''
        return the first ack value
        '''
        try:
            keys = self.__redis_cli.keys()
            return keys[0], self.__redis_cli.get(keys[0])
        except:
            loguru.logger.error("redis get ack error")
            return None, None

    def connect(self):
        '''
        connect to redis
        '''
        try:
            self.__redis_cli = redis.Redis(host=self.__redis_host, 
                                           port=self.__redis_port,
                                           password=self.__redis_password)
            self.__redis_cli.ping()
            return True
        except Exception as e:
            loguru.logger.error(f"connect redis failed ==> {e}")
            return False
    
    def check_ack_if_hava_value(self):
        '''
        check if ack has value
        '''
        try:
            if len(self.__redis_cli.keys()) <= 1:
                return False
            return True
        except:
            loguru.logger.error("redis get ack lenth error")
            return False

    def __lpush_a_value(self, queue_name, value):
        '''
        add value to queue
        '''
        try:
            self.__redis_cli.lpush(queue_name, value)
            return True
        except:
            loguru.logger.error("redis add message error")
            return False
        
    def __rpop_a_value(self, queue_name):
        '''
        pop value from queue
        '''
        try:
            values=self.__redis_cli.brpop(queue_name)
            if values:
                return values[1]
            return None
        except:
            loguru.logger.error("redis get message error")
            return None

    @staticmethod
    def check_if_connectable(host, port,password=None):
        '''
        check if redis is connectable
        '''
        try:
            redis_cli = redis.Redis(host=host, port=port,password=password)
            redis_cli.ping()
            return True
        except:
            loguru.logger.error("redis can not connect")
            return False
        
    @property
    def redis_cli(self):
        return self.__redis_cli
    
    @staticmethod
    def get_all_pairs(redis:redis.Redis):
        '''
        get all keys and values
        '''
        try:
            keys = redis.keys()
            values=redis.mget(keys)
            pairs = dict(zip(keys, values))
            return pairs
        except:
            loguru.logger.error("can not get all keys and values")
            return None
    
    @staticmethod
    def get_all_keys(redis:redis.Redis):
        '''
        get all keys
        '''
        try:
            keys = redis.keys()
            return keys
        except:
            loguru.logger.error("can not get all keys")
            return None
    


if __name__ == "__main__":
    Redis.check_if_connectable("8.130.13.25",6379)
