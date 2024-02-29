import requests
import sys
from multiprocessing import Pool,Lock
import os 
import loguru

# init loguru
loguru.logger.add("/log/error.log", rotation="5 MB", retention="10 days", level="ERROR")


existence=[]
g_lock=Lock()

def worker(ip: str, path: str):
    url = "http://" + ip  + path
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            with g_lock:
                existence.append(path)
    except Exception as e:
        pass

# get path dir name from file
def get_dir(path:str):
    try:
        dir_path_list = []
        dir_path_list=os.listdir(path)
        return dir_path_list
    except Exception as e:
        loguru.logger.error(e)
        return False

def scanner(ip,file_name:str=None,file_path:list=None,threads=10):
    '''
    scan web path
    dir_path is a file path,only one file
    dirs is a list, please assignment a dir name
    '''
    if file_name==None and file_path==None:
        loguru.logger.error("dir_path and dirs is None")
        raise Exception("dir_path and dirs is None")
    try:
        if file_name!=None:
            if not os.path.exists(file_name):
                loguru.logger.error(f"{file_name} is not exist")
                raise Exception(f"{file_name} is not exist")

            pool=Pool(threads)
            with open(file_name, "r") as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    pool.apply_async(worker,(ip,line))
            pool.close()
            pool.join()
        else:
            if not os.path.exists(file_path):
                loguru.logger.error(f"{file_path} is not exist")
                raise Exception(f"{file_path} is not exist")
            
            file_list = os.listdir(file_path)

            for path in file_list: # dirs is a dir name list

                pool=Pool(threads)
                with open(file_path+"/"+path, "r") as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        pool.apply_async(worker,(ip,line))
                pool.close()
                pool.join()

    except Exception as e:
        loguru.logger.error(e)
        return False
    
    loguru.logger.success("Scan complete")
    return existence

        


    