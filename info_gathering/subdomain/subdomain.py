import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import os 
import loguru

#init log
loguru.logger.add("/log/error.log", rotation="500 MB", retention="10 days", level="ERROR")



class subdomain_scanner:
    
    def __init__(self, domain,threads=10,file_path=None,file_name=None):
        '''
        :param domain: domain to be scanned
        :param threads: threads to be used
        :param file_path: path of the file containing subdomains
        :param file_name: name of the file containing subdomains

        if use file_path, then all files in the path will be used
        if use file_name, then only one file will be used, the path is /data/subdomain/
        '''
        self.domain = domain
        self.threads = threads
        self.subdomains = []
        self.lock = Lock() 
        if file_name:
            self.file_name = file_name
            self.mode="file" # only one file
        elif file_path:
            self.file_path = file_path 
            self.mode="path" # all files in the path
        else:
            raise Exception("file_path or file_name must be set")
        
    def _get_dict(self):
        """
        if mode is file, then read the file
        if mode is path, then read all files in the path; note!!! only return file name list
        """
        if self.mode == "file":
            try:
                with open(self.file_name, 'r') as f:
                    subdomains = f.readlines()
                return subdomains
            except Exception as e:
                loguru.logger.error(f"{e}")
                return None
        elif self.mode == "path":
            try:
                files=os.listdir(self.file_path)
                return files
            except Exception as e:
                loguru.logger.error(f"Error: {e}")
                return None
 
    def _run(self,domain,subdomain):
        '''
        :param domain: user input domain
        :param subdomain: subdomain to be scanned
        '''
        try:
            url=subdomain+"."+domain
            answers = dns.resolver.resolve(url, 'A')
            for rdata in answers:
                loguru.logger.info(f"Subdomain found: {url}  IP: {rdata.address}")
                if self.lock.acquire():
                    self.subdomains.append(url)
                    self.lock.release()
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN: # Non-Existent Domain
            pass
        except dns.resolver.NoNameservers: # No nameservers found
            pass
        except dns.resolver.Timeout: # Timeout
            pass
        except Exception as e:
            loguru.logger.error(f"{e}")

    def get_subdomains(self):
        pool=ThreadPoolExecutor(max_workers=self.threads)
        if self.mode == "file":
            try:
                with open(self.file_name, 'r') as f:
                    subdomains = f.readlines()
                for subdomain in subdomains:
                    pool.submit(self._run, self.domain,subdomain.strip())
                pool.shutdown(wait=True)
            except Exception as e:
                loguru.logger.error(f"Error: {e}")
                return None
        elif self.mode == "path":
            try:
                files=os.listdir(self.file_path)
                for file in files:
                    with open(self.file_path+"/"+file, 'r') as f:
                        subdomains = f.readlines()
                    for subdomain in subdomains:
                        pool.submit(self._run, self.domain,subdomain.strip())
                pool.shutdown(wait=True)
            except Exception as e:
                loguru.logger.error(f"Error: {e}")
                return None
        return list(set(self.subdomains))
            



