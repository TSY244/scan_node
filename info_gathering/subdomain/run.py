if __name__ == '__main__':
    import OneForAll.oneforall
else:
    import OneForAll.oneforall
    
def run(domain):
    oneforall = OneForAll.oneforall.OneForAll(domain)
    oneforall.run()
    print(oneforall.datas)
    return oneforall.datas

if __name__ == '__main__':
    run('hetianlab.com')
