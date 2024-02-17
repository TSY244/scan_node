import requests  
from urllib.parse import urlparse  
import sys  
import re  
from config import *  


def bing_search(site, page):  
    Subdomain = []  
    headers = {  
        'User-Agent': User_Agent,  
        'Cookie': bing_cookie  
    }  
    for p in range(int(page)):  
        try:  
            url = "https://cn.bing.com/search?q=site%3A{0}&qs=n&form=QBRE&sp=-1&pq=site%3A{0}"+\
            "&sc=2-11&sk=&cvid=C1A7FC61462345B1A71F431E60467C43&toHttps=1"+\
            "&redig=3FEC4F2BE86247E8AE3BB965A62CD454&pn=2&first={1}1&FROM=PERE".format(site, p)  
          
            html = requests.get(url, headers=headers, timeout=3).content.decode()  
        except Exception as e:
            print(e)  
            pass  
        job_bt = re.findall('<a target="_blank" href="*" h="(.*?)"', html)  
        for h in job_bt:  
            domain = urlparse(h).netloc  
            Subdomain.append(domain)  
    Subdomain = list(set(Subdomain))  # 去重  
    return Subdomain  


def baidu_search(site, page):  
    Subdomain = []  
    headers = {  
        'Accept': Accept,  
        'User-Agent': User_Agent,  
        'Accept - Encoding': "gzip, deflate, br",  
        'Cookie': baidu_cookie  
    }  
    for p in range(int(page)):  
        try:  
            url = "https://www.baidu.com/s?wd=site%3A{0}&pn={1}0&oq=site%3A{0}"+\
            "&tn=baiduhome_pg&ie=utf-8&rsv_idx=2&rsv_pq=d59fc7380000344c"+\
            "rsv_t=38efmxGEvInEMk2hU6IhokqHGzr3WTIIPSDy2Kx%2FsmGphjpX6JSRFpfdGfHMYJkw3le%2B".format(site, p)  
            html = requests.get(url, headers=headers, timeout=3).content.decode()  
        except Exception:  
            pass  
        # job_bt = re.findall('style="text-decoration:none;position:relative;">(.*?)/', html)  
        job_bt = re.findall('<span class="c-color-gray" aria-hidden="true">(.*?)/</span>', html)  
        Subdomain.extend(job_bt)  
        Subdomain = list(set(Subdomain))  # 去重  
    return Subdomain  

def google_search(site, page):  
    Subdomain = []  
    headers = {'User-Agent': User_Agent}  
    proxies = proxy  
    for p in range(int(page)):  
        try:  
            url = "https://www.google.com/search?q=site:{0}"+\
            "&newwindow=1&ei=lC4TYuqRB4ed0wT0q6-oBg&start={1}0&sa=N"+\
            "&ved=2ahUKEwjqq-6Lk5D2AhWHzpQKHfTVC2U4ChDy0wN6BAgBEDs&biw=1872&bih=929&dpr=1".format(site, p)  

            html = requests.get(url, headers=headers, proxies=proxies, timeout=3).content.decode()  
        except Exception:  
            pass  
        job_bt = re.findall('<cite class="iUh30 qLRx3b tjvcx" role="text">(.*?)<span', html)  
        for h in job_bt:  
            domain = urlparse(h).netloc  
            Subdomain.append(domain)  
    Subdomain = list(set(Subdomain))  # 去重  
    return Subdomain  


if __name__ == '__main__':  
    if len(sys.argv) == 3:  
        site = sys.argv[1]  
        page = sys.argv[2]  
    else:  
        print(f"usage: {sys.argv[0]} baidu.com 10")  
        sys.exit(-1)  

    bing_subdomain = bing_search(site, page)  
    print(f"bing 搜索引擎获取子域名: {len(bing_subdomain)} 个")  
    # print("bing 搜索引擎获取子域名: ")  
    # print(bing_subdomain)  
    baidu_subdomain = baidu_search(site, page)  
    print(f"baidu 搜索引擎获取子域名: {len(baidu_subdomain)} 个")  
    # print("baidu 搜索引擎获取子域名: ")  
    # print(baidu_subdomain)  
    google_subdomain = google_search(site, page)  
    print(f"google 搜索引擎获取子域名: {len(google_subdomain)} 个")  
    # print("google 搜索引擎获取子域名: ")  
    # print(google_subdomain)  
    domain = baidu_subdomain + bing_subdomain + google_subdomain  
    Subdomain = list(set(domain))  
    print(f"--- 去重后总共获取子域名： {len(Subdomain)} 个 ---")  
    print("=== 子域名 ===")  
    filename = f"{site}.txt"  
    for i in Subdomain:  
        print(i)  
        with open(filename, "a+") as f:  
            f.write(i + "\n")  
            f.close()  

    print("子域名搜索完毕...")