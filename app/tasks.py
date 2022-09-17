from app import celery, db
from app.scripts import covalent_tx
from app.models import Transaction

@celery.task(name="Update Transactions")
def update_txModel(chain_id, address):
    transactions = covalent_tx.get_tx(chain_id, address)
    if transactions is not None:
        return True

    for tx_hash, tx_details in transactions.items():
        #Check if transaction already exists in DB
        check_txHash = Transaction.query.filter_by(tx_hash=tx_hash).first()
        if check_txHash is not None:
            continue

        tx = Transaction(
            tx_hash = tx_hash,
            chain_id = tx_details['chain_id'],
            block_number = tx_details['block_number'],
            from_addr = tx_details['from_addr'],
            to_addr = tx_details['to_addr'],
            tx_timestamp = tx_details['tx_timestamp'],
            tx_value = tx_details['tx_value'],
            tx_gas = tx_details['tx_gas'],
            tx_gas_price = tx_details['tx_gas_price'],
            tx_actions = tx_details['tx_actions'],
            rate = tx_details['rate']
        )
        print("I FUCKIN RAN")
        db.session.add(tx)
    db.session.commit()
    return True

@celery.task
def add(x, y):
    return x + y