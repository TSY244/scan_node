with open("ret/vuls.txt",'r',encoding="utf-8") as f:
    rets=f.readlines()

data=eval(rets[0])
print(data)
print(type(data))

data["sdaf"]="sadfsadf"

print(data)

# import tools.vulmap.run as vulmap_run
# import tools.read_scan_vuls_ret as read_vuls
# import tools.UseElasticSearch.UseElasticSearch as ES
# import configparser 

# es=ES.MyElasticSearch("192.168.79.128",9200)
# try:
#     es.connect()
# except Exception as e:
#     print(e)

# ret=es.search_data_by_query("vuls","{\"query\":{\"match\": {\"prt_name\": \"JBoss1\"}}}")

# for i in ret['hits']['hits']:
#     print(i['_source'])








