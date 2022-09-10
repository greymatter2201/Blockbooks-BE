from app import app, socketio, db
from app.models import Transactions, Wallet, User, transaction_details, Contact, Labels, label_schema

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Transactions': Transactions,
        'transaction_details' : transaction_details,
        'Contact': Contact,
        'Wallet': Wallet,
        'User': User,
        'Labels': Labels,
        'label_schema': label_schema
    }

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)