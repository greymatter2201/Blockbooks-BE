# Bring your packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'Blockbooks_BE', 'app')))
from scripts import etherscan_tx

def test_get_tx():
    address = "0x03d15Ec11110DdA27dF907e12e7ac996841D95E4"
    results = etherscan_tx.get_tx(address, offset=1)
    assert results != None

def test_get_tx_action():
    # tx hash with TX Actions
    tx_hash = "0x46e028ae2a4f9abdc7ec9e099f5fec09e2e1b121ddd399ec7164f56bccea54e3"

    # tx hash without TX actions
    tx_hash_none = "0x3fe1eba9d2869542699414774d46a402ca6ffa0ebf8ef07e3b3c584a023f3d8d"

    res1 = etherscan_tx.get_tx_action(tx_hash)
    res2 = etherscan_tx.get_tx_action(tx_hash_none)
    assert len(res1) != 0
    assert len(res2) == 0
    
