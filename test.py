import tools.UseElasticSearch.UseElasticSearch as ES

es=ES.MyElasticSearch("192.168.79.128",9200)
es.connect()
es.delete_index("info")
es.delete_index("vuls")


# data["sdaf"]="sadfsadf"

# print(data)

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








