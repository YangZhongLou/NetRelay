import json

config_data = {}

def get_config():
    global config_data
    if config_data['server_ip'] != None:
        return config_data

    with open('NetRelayConfig.json', 'r') as f:
        config_data = json.load(f)
    return config_data