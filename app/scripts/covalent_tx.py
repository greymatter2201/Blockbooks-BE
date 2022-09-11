import requests, os, time
from dotenv import load_dotenv
from etherscan_tx import get_tx_action
from pprint import pprint

load_dotenv()

base_url = 'https://api.covalenthq.com/v1'

#Ethereum is chain_id 1 
chain_id = '1'
COVALENT_API_KEY = os.environ['COVALENT_API_KEY']

#Datetime returned by covalent -> "2022-09-10T09:16:41Z"
def get_eth_candle_rate(datetime):
    date_str, time = datetime.split("T")
    time = time.replace("Z","")
    hour, minute, second = time.split(":")
    url = f"https://api.exchange.coinbase.com/products/ETH-USD/candles?granularity=60&start={date_str}%20{hour}%3A{minute}%3A00&end={date_str}%20{hour}%3A{minute}%3A59"
    response = requests.get(url)
    try:
        result = response.json()[0][4]
    except IndexError:
        return 0
    else:
        return response.json()[0][4]

def convert_datetime(datetime):
    d = "2022-09-11T10:08:16Z"
    d = d.replace("T", " ")
    d = d.replace("Z", "")
    timestamp = time.mktime(time.strptime(d, '%Y-%m-%d %H:%M:%S'))
    return int(timestamp)

def get_tx(address, page_size=10):
    endpoint = f'/{chain_id}/address/{address}/transactions_v2/?page-size={page_size}&key={COVALENT_API_KEY}'
    url = base_url + endpoint
    result = requests.get(url).json()

    transactions = {}

    tx_array = result['data']['items']
    # The transactions are in a dictionary in the array
    for tx in tx_array:
        timestamp = convert_datetime(tx.get('block_signed_at'))
        rate = get_eth_candle_rate(tx.get('block_signed_at'))
        eth_rate = lambda rate : rate if rate else tx.get('gas_quote_price')
        f_eth_rate = float("{:.2f}".format(eth_rate(rate)))

        transactions[tx.get('tx_hash')] = {
            'block_number': tx.get('block_height'),
            'from_addr': tx.get('from_address'),
            'to_addr': tx.get('to_address'),
            'timestamp': timestamp,
            'value': tx.get('value'),
            'gas': tx.get('gas_spent'),
            'gas_price': tx.get('gas_price'),
            'action': None,
            'rate': f_eth_rate,
        }
    return transactions
