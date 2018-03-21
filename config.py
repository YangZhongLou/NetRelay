import json

config_data = {}

def get_config():
    global config_data
    if 'server_ip' in config_data.keys():
        return config_data

    with open('net_relay_config.json', 'r') as f:
        config_data = json.load(f)
    return config_data