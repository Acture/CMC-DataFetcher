import csv
import requests
import re
import pandas as pd
import time

api_key = '95059a1d-ad06-4dcd-895a-6e9827078c09'
test_api_key = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"

api_keys = {'95059a1d-ad06-4dcd-895a-6e9827078c09':{'daily_credits_left':0,'monthly_credits_left':0}}

server = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&CMC_PRO_API_KEY={key}'
test_server = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&CMC_PRO_API_KEY={key}'
names_api = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?symbol={symbol}&CMC_PRO_API_KEY={key}"

proxies = {
    'https': 'socks5h://127.0.0.1:1080',
    'http': 'socks5h://127.0.0.1:1080'
}

names = ['Anonverse','FreeRossDAO','APENFT','Pig Finance','Rai Finance','SafeMoon','OpenDAO']
ids = ['17100','16148','9816','8829','16552','8757','16463']

def load_csv(file):
	cmc_list = []
	with open(file) as f:
		reader  = csv.reader(f)
		t = list(reader)
		for code in t:
			cmc_list.append(code[0])
	cmc_list = ",".join(cmc_list)
	cmc_list = cmc_list.replace('_',"").replace('-',"")

	return cmc_list


def get_data_from_symbol(symbol_list:str,target:str,key:str):
	print("Fetching data for {symbol}".format(symbol=symbol_list))
	link = target.format(symbol = symbol_list, key = key)
	try:
		r = requests.get(link,timeout=10,proxies=proxies)
	except:
		print("Error fetching data for {symbol}".format(symbol_list))
		raise Exception
	d = r.text
	regdata = re.compile('"symbol":"(.+?)",.+?"(USD)".+?"price":([0-9.]+?),')
	regtime = re.compile('"timestamp":"(.+?)"')
	timestamp = regtime.findall(d)[0]
	data = regdata.findall(d)
	df = pd.DataFrame(data,columns=['Symbol',"Quote","Price"])
	df['Time'] = timestamp
	df['Time'] = pd.to_datetime(df['Time']).dt.tz_localize(None)
	df['Price'] = pd.to_numeric(df['Price'])
	return df

def get_data_from_id(id_list:list,key:str):
	id_list = ','.join(id_list)
	link = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={id}&CMC_PRO_API_KEY={key}'.format(id = id_list, key =key)
	try:
		r = requests.get(link,timeout=10,proxies=proxies)
	except:
		print("Error fetching data for {symbol}".format(symbol_list))
		raise Exception
	d = r.text
	regdata = re.compile('"symbol":"(.+?)",.+?"quote".+?"(USD)".+?"price":(.+?),')
	regtime = re.compile('"timestamp":"(.+?)"')
	regcredit = re.compile('"credit_count":([0-9]+),')
	timestamp = regtime.findall(d)[0]
	data = regdata.findall(d)
	credit_used = int(regcredit.findall(d)[0])
	api_keys[key]['daily_credits_left'] -= credit_used
	api_keys[key]['monthly_credits_left'] -= credit_used
	df = pd.DataFrame(data,columns=['Symbol',"Quote","Price"])
	df['Time'] = timestamp
	df['Time'] = pd.to_datetime(df['Time']).dt.tz_localize(None)
	df['Price'] = pd.to_numeric(df['Price'])

	return df

def get_ids(symbol_list:str):
	link = names_api.format(symbol= symbol_list,key = api_key)
	print(link)
	r = requests.get(link,timeout=10,proxies=proxies)
	reg = re.compile('{"id":([0-9]+),"name":"([^"]+)","symbol":"([^"]+)","slug":"([^"]+)","rank":([0-9]+|null),.+?,"platform":.+?}')
	r = reg.findall(r.text)
	df = pd.DataFrame(r,columns = ['ID',"Name","Symbol","Slug","Rank"])
	df['ID'] = pd.to_numeric(df['ID'])
	return df

def test() :
	r = requests.get("http://www.google.com",timeout=10,proxies=proxies)
	print(r.text)

def update_keys(api_keys: dict):
	for key in api_keys:
		link = 'https://pro-api.coinmarketcap.com/v1/key/info?CMC_PRO_API_KEY={key}'.format(key = key)
		try:
			r = requests.get(link,timeout=10,proxies=proxies)
		except:
			print("Error fetching data for {key}".format(key = api_key))
			raise Exception
		d = r.text
		reg = re.compile('"current_day":{"credits_used":[0-9]+,"credits_left":([0-9]+)},"current_month":{"credits_used":[0-9]+,"credits_left":([0-9]+)')
		credits_left = list(reg.findall(d)[0])

		api_keys[key]['daily_credits_left'] = int(credits_left[0])
		api_keys[key]['monthly_credits_left'] = int(credits_left[1])

def get_available_key():
	update_keys(api_keys)
	t_keys = [key if api_keys[key]['daily_credits_left'] >10 and api_keys[key]['monthly_credits_left']>10 else '' for key in api_keys]
	return t_keys[0]

def judge_time():
	_, _, _, _, minute = map(int, time.strftime("%Y %m %d %H %M").split())
	
	if minute%10 == 0:
		return True
	return False


def main():
	while True:
		if judge_time():
			t_key = get_available_key()
			df = get_data_from_id(ids,t_key)
			print(df)
			df.to_excel('CMC_DATA_{time}'.format(time = time.strftime("%Y_%m_%d_%H_%M")),index = False)

if __name__ == '__main__':
	main()