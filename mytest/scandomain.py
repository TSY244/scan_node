import info_gathering.subdomain.subdomain as subdomain


def test():
    scanenr=subdomain.subdomain_scanner("baidu.com",threads=10,file_name="data/subdomain/dict.txt")
    return scanenr.get_subdomains()