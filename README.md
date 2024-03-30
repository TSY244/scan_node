# 说明
1. 请添加扫描web path 目录添加至db目录，本项目使用dirsearch的扫描目录
    [dirsearch](https://github.com/maurosoria/dirsearch/tree/master)

2. 关于子域名爆破指定文件路径

   


# es设置

es 主要是有两个索引组成，info  和vuls ，分别记载info 和vuls

info

| code_name | 名称     | 属性 | 描述                                                         | example                                                    | 状态 |
| --------- | -------- | ---- | ------------------------------------------------------------ | ---------------------------------------------------------- | ---- |
| site      | url      | str  | 主要的站点                                                   | http://ip                                                  | 实现 |
| port      | 端口     | str  | 主站点对应的端口信息                                         | 8080,7001                                                  | 实现 |
| area      | 地区     | str  | url,ip 对应的地点                                            | 如果是局域网是：局域网 局域网<br />如果是真实的url：省  市 | 实现 |
| subdomain | 子域名   | str  | 主站点的其他域名                                             | http://xxx.ip                                              | 实现 |
| webpath   | web路径  | list | 每一个元素是一个str，每一个站点可能对应一个webfile<br />如果是有多个子域名的话，将会有对应的情况 | \a\b\c                                                     | 实现 |
| vuls      | 漏洞目录 | list | 一个列表，每一个成员都是一个str，对应一个prt_name            | []                                                         | 实现 |
| tide      | 指纹     | list | 该站点使用到的技术                                           | spring boot                                                | 实现 |



vuls

| 键名     | 值类型 | 名称        | 描述              | example                                                   |
| -------- | ------ | ----------- | ----------------- | --------------------------------------------------------- |
| site     | str    | 主站点      | 主站点的ip        | site:"ip"                                                 |
| prt_name | str    | 漏洞名称    | 漏洞的完整名称    | prt_name:"RedHat JBoss1: CVE-2017-12149"                  |
| vul_name | str    | 漏洞名称    | 漏洞的名称        | vul_name:"JBoss 反序列化远程命令执行漏洞"                 |
| vul_numb | str    | 漏洞        | 使用cve等判断漏洞 | vul_numb:"CVE-2017-12149"                                 |
| vul_type | str    | 漏洞类型    | 漏洞的类型        | vul_type:"vul_type远程命令执行"                           |
| vul_urls | str    | 漏洞站点    | 漏洞存在的站点    | vul_urls:"http://192.168.79.128:8080"                     |
| vul_payd | str    | 漏洞payload | 漏洞的利用方式    | "vul_payd": "http://192.168.79.128:8080/invoker/readonly" |



# 所使用的工具

- [zhzyker/vulmap: Vulmap 是一款 web 漏洞扫描和验证工具, 可对 webapps 进行漏洞扫描, 并且具备漏洞验证功能 (github.com)](https://github.com/zhzyker/vulmap)
- [TideSec/TideFinger: TideFinger——指纹识别小工具，汲取整合了多个web指纹库，结合了多种指纹检测方法，让指纹检测更快捷、准确。 (github.com)](https://github.com/TideSec/TideFinger)



# 版本说明
例如1.2.3
1更新的大版本，如果遇到重构等情况
2为添加了新的模块
3为修改了bug
每一个数字都没有具体的作用，只为了记录