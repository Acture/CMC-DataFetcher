import csv
import requests
import re
import pandas as pd
import time

api_key = '95059a1d-ad06-4dcd-895a-6e9827078c09'
test_api_key = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"

server = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&CMC_PRO_API_KEY={key}'
test_server = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&CMC_PRO_API_KEY={key}'


proxies = {
    'https': 'socks5h://127.0.0.1:1080',
    'http': 'socks5h://127.0.0.1:1080'
}

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


def get_data(symbol_list:str,target:str,key:str)-> list:
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

def get_ids(symbol_list:str,target:str,key:str)-> list:
	link = target.format(symbol = symbol_list, key = key)

def test() :
	r = requests.get("http://www.google.com",timeout=10,proxies=proxies)
	print(r.text)

if __name__ == '__main__':
	file = "CMC.csv"
	cmc_list = load_csv("CMC.csv")
	print(cmc_list)
	df = get_data(cmc_list,server,api_key)
	print(df)
	df.to_excel("{file}_data.xlsx".format(file = file.split('.')[0]),index = False)