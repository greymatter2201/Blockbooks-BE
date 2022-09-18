from app import app, socketio, db
from app.models import Transaction, Wallet, User, transaction_detail, Contact, Label, label_schema

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Transaction': Transaction,
        'transaction_detail' : transaction_detail,
        'Contact': Contact,
        'Wallet': Wallet,
        'User': User,
        'Label': Label,
        'label_schema': label_schema
    }

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)