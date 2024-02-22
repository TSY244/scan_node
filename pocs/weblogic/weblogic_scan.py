import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cve_2014_4210
import cve_2016_0638
import cve_2016_3510
import cve_2017_10271
import cve_2018_2628
import cve_2018_2894
import cve_2019_2725
import cve_2019_2729
import cve_2019_2890

vulnerability=[]

pocs={"cve_2014_4210":cve_2014_4210.run,
      "cve_2016_0638":cve_2016_0638.run,
      "cve_2016_3510":cve_2016_3510.run,
      "cve_2017_10271":cve_2017_10271.run,
      "cve_2018_2628":cve_2018_2628.run,
      "cve_2018_2894":cve_2018_2894.run,
      "cve_2019_2725":cve_2019_2725.run,
      "cve_2019_2729":cve_2019_2729.run,
      "cve_2019_2890":cve_2019_2890.run
    }
        

# 获取当前模块的所有函数
def get_pocs():
    for name in dir(sys.modules[__name__]):
        if name.startswith('cve_'):
            vulnerability.append(name)
    return vulnerability

def result(ip,port):
    result = []
    for poc in pocs.values():
        ret = poc(ip,port)
        if ret:
            result.append(ret)
    return result

    # pocs=get_pocs()
    # for poc in pocs:
    #     ret = poc(ip,port)
    #     if ret:
    #         result.append(ret)
    # return result




