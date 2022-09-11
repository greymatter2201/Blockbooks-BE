# Bring your packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'Blockbooks_BE', 'app')))
from scripts import covalent_tx

def test_get_tx():
    address = "0x03d15Ec11110DdA27dF907e12e7ac996841D95E4"
    tx = covalent_tx.get_tx(address, page_size=1)
    assert tx != None