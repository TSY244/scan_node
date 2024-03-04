'''
delete elasticsearch index
'''

from tools.UseElasticSearch.UseElasticSearch import MyElasticSearch

def del_index():
    es = MyElasticSearch("192.168.79.128", "9200")
    es.connect()

    es.delete_index('info')
    es.delete_index('vuls')


if __name__ == '__main__':
    del_index()