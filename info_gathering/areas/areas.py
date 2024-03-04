import requests

urls=["https://searchplugin.csdn.net/api/v1/ip/get?ip={}",
      "https://whois.pconline.com.cn/ipJson.jsp?ip={}&json=true",
      "https://searchplugin.csdn.net/api/v1/ip/get?ip={}",
      ]


def get_areas(ip):
    try:
        resp = requests.get(urls[0].format(ip))
        if resp.status_code == 200:
            text=eval(resp.text)
            address=text['data']['address'].split(" ")[:-1] # 中国 湖南 长沙 电信 to ['中国', '湖南', '长沙']
            return address
        
            
        resp = requests.get(urls[1].format(ip))
        if resp.status_code == 200:
            text=eval(resp.text)
            pro=text['pro'] 
            city=text['city']
            return [pro,city]

        resp = requests.get(urls[2].format(ip))
        if resp.status_code == 200:
            text=eval(resp.text)
            address=text['data']['address'].split(" ")[:3]
            return address
        
        raise Exception("No data")
    except Exception as e:
        print(e)
        return None
    
def run(ip):
    areas=get_areas(ip)
    if areas is None:
        return ""
    area=""
    for a in areas:
        area+=(a+" ")
    return area


if __name__ == '__main__':
    resp = requests.get(urls[2].format("8.130.123.25"))
    if resp.status_code == 200:
        text=eval(resp.text)
        address=text['data']['address'].split(" ")[:3]
        print( address)