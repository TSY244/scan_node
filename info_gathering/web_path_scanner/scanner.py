import requests
import sys
from multiprocessing.dummy import Pool as Pool
import os 
import loguru

# init loguru
loguru.logger.add("log/error.log", rotation="5 MB", retention="10 days", level="ERROR")


existence=[]


def worker(url: str, path: str):
    url = url + "/" + path
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return path
    except Exception as e:
        return None

# get path dir name from file
def get_dir(path:str):
    try:
        dir_path_list = []
        dir_path_list=os.listdir(path)
        return dir_path_list
    except Exception as e:
        loguru.logger.error(e)
        return False

def scanner(ip,port:int=80,file_name:str=None,file_path:list=None,threads=10):
    '''
    scan web path
    dir_path is a file path,only one file
    dirs is a list, please assignment a dir name
    '''
    global existence
    if file_name==None and file_path==None:
        loguru.logger.error("dir_path and dirs is None")
        raise Exception("dir_path and dirs is None")
    
    try:
        url = "http://"+ip+":"+str(port)
        if file_name!=None:
            if not os.path.exists(file_name):
                loguru.logger.error(f"{file_name} is not exist")
                raise Exception(f"{file_name} is not exist")

            pool=Pool(threads)
            results=[]
            with open(file_name, "r") as f:
                while True:
                    line = f.readline()
                    line = line.strip()
                    if not line:
                        break
                    ret=pool.apply_async(worker,(url,line))
                    results.append(ret)
            for ret in results:
                ret.wait() # wait for all worker finish

            for ret in results:
                i=ret.get()
                if i!=None:
                    existence.append(i)

            pool.close() 
            pool.join()
        else:
            if not os.path.exists(file_path):
                loguru.logger.error(f"{file_path} is not exist")
                raise Exception(f"{file_path} is not exist")
            
            file_list = os.listdir(file_path)
            pool=Pool(threads)
            requests = []
            for path in file_list: # dirs is a dir name list
                with open(file_path+"/"+path, "r") as f:
                    while True:
                        line = f.readline()
                        line = line.strip()
                        if not line:
                            break
                        ret=pool.apply_async(worker,(url,line))
                        requests.append(ret)
                for ret in requests:
                    ret.wait()

                for ret in requests:
                    i=ret.get()
                    if i!=None:
                        existence.append(i)

            pool.close()
            pool.join()

    except Exception as e:
        loguru.logger.error(e)
        return False
    
    loguru.logger.success("Scan complete")
    return existence

        


if __name__ == "__main__":
    ret=scanner("192.168.79.137",file_path="D:/code/vsc/PythonProject/AllNodes/scan_node/data/web_path",threads=10)
    # worker("http://192.168.79.137:80","admin.html",existence,g_lock)
    
    print(ret)