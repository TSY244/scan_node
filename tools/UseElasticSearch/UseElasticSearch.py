from elasticsearch import Elasticsearch
import json

class MyElasticSearch:
    def __init__(self, host, port):
        self.url="http://"+host+":"+str(port)
        self.es=None

    def connect(self):
        self.es = Elasticsearch([self.url])
        if self.es.ping():
            return True
        else:
            return False
        
    def create_index(self,index_name):
        if self.es.indices.exists(index=index_name):
            return False
        else:
            self.es.indices.create(index=index_name)
            return True
        
    def delete_index(self,index_name):
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
            return True
        else:
            raise Exception("index not exists")
        
    def insert_data(self,index_name,data):
        self.es.index(index=index_name,document=data)
    
    def delete_data_by_id(self,index_name,id):
        self.es.delete(index=index_name,id=id)

    def delete_data_by_name(self,index_name,name):
        query = {"match": {"name": name}}
        result = self.es.search(index=index_name, body=query)
        for i in result['hits']['hits']:
            self.es.delete(index=index_name,id=i['_id'])

    def search_data_by_query(self,index_name,query):
        result = self.es.search(index=index_name, body=query)
        return result
    
    def search_data(self,index_name,size:int=10):
        result = self.es.search(index=index_name,size=size)
        return result


