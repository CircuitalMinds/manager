import yaml
import requests

    
def data_files(path):
    
    dict_data = {}
    print(path)
    for name in list(path.keys()):
        data = yaml.load(requests.get(path[name]).content, Loader=yaml.FullLoader)
        for key in list(data.keys()):
            dict_data[key] = data[key]
            
    return dict_data
