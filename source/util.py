import json

def load_api_keys () :
	return open('./source/api_keys.txt', 'r').read().split('\n')[1:]

def load_stock_api () :
	return open('./source/api_keys.txt', 'r').read().split('\n')[0]

def load_channel_names ():
	return open('./source/channels.txt', 'r').read().split('\n')

def load_json (path):
	with open(path) as f:
		return json.load(f)