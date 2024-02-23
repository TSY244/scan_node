import json

def read_json(filename):
    with open(filename, 'r',encoding="utf-8") as f:
        load_dict = json.load(f)
        return load_dict
    
if __name__ == "__main__":
    json_data=read_json("ret\\vuls.json")