import requests

usrs=["https://www.dnsgrep.cn/subdomain/hetianlab.com",
      "https://rapiddns.io/s/hetianlab.com#result"]

ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
cookie={"gid":"GA1.2.1922052658.1709523029"}

def get_subdomain(url):
    try:
        headers = {
            "User-Agent": ua,
            "Cookie": str(cookie)
        }
        response = requests.get(url, headers=headers)
        print(response.text)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    get_subdomain(usrs[0])