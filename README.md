# json数据

| code_name | 名称     | 属性 | 描述                                                         | example                                                    | 状态   |
| --------- | -------- | ---- | ------------------------------------------------------------ | ---------------------------------------------------------- | ------ |
| site      | url      | str  | 主要的站点                                                   | http://ip                                                  | 实现   |
| port      | 端口     | str  | 主站点对应的端口信息                                         | 8080,7001                                                  | 实现   |
| area      | 地区     | str  | url,ip 对应的地点                                            | 如果是局域网是：局域网 局域网<br />如果是真实的url：省  市 | 实现   |
| subdomain | 子域名   | str  | 主站点的其他域名                                             | http://xxx.ip                                              | 未实现 |
| webfile   | web路径  | str  | 每一个站点可能对应一个webfile<br />如果是有多个子域名的话，将会有对应的情况 | \a\b\c                                                     | 未实现 |
| vuls      | 漏洞目录 | list | 一个列表，每一个成员都是一个str，对应一个vul 的描述，本身格式为json | {vul1}<br />{vul2}                                         | 实现   |

# 所使用的工具

- [zhzyker/vulmap: Vulmap 是一款 web 漏洞扫描和验证工具, 可对 webapps 进行漏洞扫描, 并且具备漏洞验证功能 (github.com)](https://github.com/zhzyker/vulmap)
- [TideSec/TideFinger: TideFinger——指纹识别小工具，汲取整合了多个web指纹库，结合了多种指纹检测方法，让指纹检测更快捷、准确。 (github.com)](https://github.com/TideSec/TideFinger)



