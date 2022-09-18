# Bring your packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'Blockbooks_BE', 'app')))
from scripts import covalent_tx

def test_get_tx():
    address = "0x03d15Ec11110DdA27dF907e12e7ac996841D95E4"
    tx = covalent_tx.get_tx('1', address, page_size=1)
    expected_tx_hash = '0xa3f3bbabe9cb45194939bd635a2f704217d35676353f11efe3ea2eb4fcd5d9d5'
    tx_hash = list(tx.keys())[0]
    assert tx_hash == expected_tx_hash

def test_get_latest_block():
    block_height = covalent_tx.get_latest_block('1')
    assert block_height is not None