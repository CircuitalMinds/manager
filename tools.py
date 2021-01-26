import yaml
import requests

    
def data_files(path):
    
    dict_data = {}
    data = yaml.load(requests.get(path).content, Loader=yaml.FullLoader)
    for dirs in list(data.keys()):
        for key in list(data[dirs].keys()):
            dict_data[key] = data[dirs][key]
            
    return dict_data
