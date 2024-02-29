import info_gathering.web_path_scanner.scanner as web_path_scanner


# web_path_scanner.scanner(ip="192.168.79.128",file_path="db",threads=10)

file_list = web_path_scanner.get_dir("db")

for file_name in file_list:
    with open("db/"+file_name, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            print(line)




# web_path_scanner.scanner("test", "test",dir_path=dir_path)


# import tools.UseElasticSearch.UseElasticSearch as ES

# es=ES.MyElasticSearch("192.168.79.128",9200)
# es.connect()
# es.delete_index("info")
# es.delete_index("vuls")


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








