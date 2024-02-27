
import os
import sys



def read_data(file_name):
    if not os.path.exists(file_name):
        raise Exception("file not exists")
    with open(file_name,"r",encoding="utf-8") as f:
        data = f.readlines()
    return data
