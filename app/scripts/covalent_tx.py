import requests, os, time, sys
from dotenv import load_dotenv
# Bring your packages onto the path
sys.path.append(os.path.abspath(os.path.join('..', 'Blockbooks_BE', 'app')))
from scripts.etherscan_tx import get_tx_action
from pprint import pprint

load_dotenv()

base_url = 'https://api.covalenthq.com/v1'

COVALENT_API_KEY = os.environ['COVALENT_API_KEY']

#Datetime returned by covalent -> "2022-09-10T09:16:41Z"
def get_candle_rate(chain_id, datetime):
    id_to_chain = {
        '1': 'ETH',
        '137': 'MATIC',
        '43114': 'AVAX'
    }

    try:
        ticker = id_to_chain[chain_id]
    except KeyError:
        return None

    date_str, time = datetime.split("T")
    time = time.replace("Z","")
    hour, minute, second = time.split(":")
    url = f"https://api.exchange.coinbase.com/products/{ticker}-USD/candles?granularity=60&start={date_str}%20{hour}%3A{minute}%3A00&end={date_str}%20{hour}%3A{minute}%3A59"
    response = requests.get(url)
    try:
        result = response.json()[0][4]
    except IndexError:
        return None
    else:
        return response.json()[0][4]

#Convert date string into timestamp
def convert_datetime(datetime):
    d = datetime
    d = d.replace("T", " ")
    d = d.replace("Z", "")
    timestamp = time.mktime(time.strptime(d, '%Y-%m-%d %H:%M:%S'))
    return int(timestamp)

def get_latest_block(chain_id):
    endpoint = f'/{chain_id}/block_v2/latest/?key={COVALENT_API_KEY}'
    url = base_url + endpoint
    try:
        results = requests.get(url).json()
        block_height = results['data']['items'][0]['height']
    except TypeError:
        return None
    else:
        return block_height

def get_tx(chain_id, address, page_size=10):
    endpoint = f'/{chain_id}/address/{address}/transactions_v2/?page-size={page_size}&key={COVALENT_API_KEY}'
    url = base_url + endpoint
    result = requests.get(url).json()

    tx_array = result['data']['items']

    if not bool(tx_array):
        return None

    transactions = {}
    # The transactions are in a dictionary in the array
    for tx in tx_array:
        timestamp = convert_datetime(tx.get('block_signed_at'))

        #Get ETH rate from get_candle_rate (coinbase API)
        #If that doesnt return anything,
        #Uses gas_quote_price from covalent API
        rate = get_candle_rate(chain_id, tx.get('block_signed_at'))
        a_rate = lambda rate : rate if rate else tx.get('gas_quote_price')
        format_a_rate = float("{:.2f}".format(a_rate(rate)))

        #Gets TX actions from scraping Etherscan
        actions = get_tx_action(tx.get('tx_hash'))
        if actions:
            action = actions[0][0]
        else:
            action = None
        
        
        transactions[tx.get('tx_hash')] = {
            'chain_id': tx.get('chain_id'),
            'block_number': tx.get('block_height'),
            'from_addr': tx.get('from_address'),
            'to_addr': tx.get('to_address'),
            'tx_timestamp': timestamp,
            'tx_value': tx.get('value'),
            'tx_gas': tx.get('gas_spent'),
            'tx_gas_price': tx.get('gas_price'),
            'tx_actions': action,
            'rate': format_a_rate,
        }
    return transactions

def get_all_chains():
    endpoint = f"/chains/?quote-currency=USD&format=JSON&key={COVALENT_API_KEY}"
    url = base_url + endpoint
    results = requests.get(url).json()
    chains = results['data']['items']
    return chains