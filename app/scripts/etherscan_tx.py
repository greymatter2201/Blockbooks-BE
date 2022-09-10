import requests, os
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.environ['ETHERSCAN_API_KEY']

def get_tx_action(hash):
    URL = f"https://etherscan.io/tx/{hash}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        page = requests.get(URL, headers=headers)
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)
    

    soup = BeautifulSoup(page.content, "html.parser")

    tx_action_exist = soup.find("i", class_="fa-lightbulb-on")
    
    if tx_action_exist:
        try:
            elements = soup.find_all("div", class_="card-body py-4")
            grandparent = elements[0].find_all("div", class_="row mb-4")
            parent = grandparent[0].find_all("ul", class_="list-unstyled")
            child = parent[0].find_all("li", class_="media", recursive=False)
        except IndexError:
            return None
        tx_actions = []
        for i in range(len(child)):
            tx_action = child[i].find_all("div", class_="media-body")
            tx_actions.append(tx_action[0].getText(' '))
        
        return parse_tx_action(tx_actions)
    return None

def get_tx(address, offset=0, startblock=0, endblock=99999999):
    response = requests.get('https://api.etherscan.io/api'
   '?module=account'
   '&action=txlist'
   f'&address={address}'
   f'&startblock={startblock}'
   f'&endblock={endblock}'
   '&page=1'
   f'&offset={offset}'
   '&sort=desc'
   f'&apikey={ETHERSCAN_API_KEY}')

    result = response.json()['result']

    transactions = {}
    for r in result:
        timestamp = r['timeStamp']
        ethusd_rate = get_eth_candle_rate(timestamp)
        tx_fee = int(r['gasUsed']) * int(r['gasPrice'])

        tx_fee_in_eth = tx_fee / 10**18
        tx_fee_in_usd = tx_fee_in_eth * ethusd_rate 

        tx_value_usd = (int(r['value']) / 10**18)  * ethusd_rate
        tx_value_eth = (int(r['value']) / 10**18)

        transactions[r['hash']] = {
            'block_number': r['blockNumber'],
            'from_addr' : r['from'],
            'to_addr' : r['to'],
            'tx_value' : r['value'],
            'tx_value_eth': tx_value_eth,
            'tx_value_usd': tx_value_usd,
            'tx_fee' : tx_fee,
            'tx_fee_eth': tx_fee_in_eth,
            'tx_fee_usd': tx_fee_in_usd,
            'tx_timestamp' : r['timeStamp'],
            }
    
    return transactions

def parse_tx_action(tx_action):
    tx_actions = [action.split(' ') for action in tx_action]

    for action in tx_actions:
        try:
            action.remove('For')
            action.remove('On')
            action.remove('To')
        except ValueError:
            pass

    return tx_actions

def parse_timestamp(timestamp):
    timestamp = int(timestamp)
    date_time = datetime.fromtimestamp(timestamp)
    str_date = date_time.strftime("%Y %m %d")
    return str_date.replace(' ', '-')

def parse_timestamp_tup(timestamp):
    timestamp = int(timestamp)
    date_time = datetime.fromtimestamp(timestamp)
    date_str = date_time.strftime("%Y-%m-%d")
    time_str = date_time.strftime("%H:%M")
    time_tup = tuple(time_str.split(":"))
    return date_str, time_tup

def get_eth_rate(timestamp):
    date = parse_timestamp(timestamp)
    response = requests.get(f"https://api.exchangerate.host/{date}?base=USD&source=crypto&symbols=ETH")
    response = response.json()
    if response['success'] != True:
        return None
    return response['rates']['ETH']

def get_eth_candle_rate(timestamp):
    date_str, time_tup = parse_timestamp_tup(timestamp)
    hour, minute = time_tup
    url = f"https://api.exchange.coinbase.com/products/ETH-USD/candles?granularity=60&start={date_str}%20{hour}%3A{minute}%3A00&end={date_str}%20{hour}%3A{minute}%3A59"
    response = requests.get(url)
    try:
        result = response.json()[0][4]
    except IndexError:
        return 0
    else:
        return response.json()[0][4]
