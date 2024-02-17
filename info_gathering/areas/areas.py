import requests

url="https://searchplugin.csdn.net/api/v1/ip/get?ip={}"


def get_areas(ip):
    try:
        resp = requests.get(url.format(ip))
        if resp.status_code == 200:
            text=eval(resp.text)
            address=text['data']['address'].split(" ")[:-1] # 中国 湖南 长沙 电信 to ['中国', '湖南', '长沙']
            return address
    except Exception as e:
        print(e)
        return None
    
def run(ip):
    areas=get_areas(ip)
    area=""
    for a in areas:
        area+=(a+" ")
    return area


if __name__ == '__main__':
   print(run('218.76.8.98'))