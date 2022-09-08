from app import db
from sqlalchemy.dialects.postgresql import JSON

# Note: nullable is False by default when primary_key=True
# Wrapper for setting column nullable to False
def NotNull(*args,**kwargs):
    kwargs["nullable"] = kwargs.get("nullable",False)
    return db.Column(*args,**kwargs)

class Transactions(db.Model):
    tx_hash = db.Column(db.String(66), primary_key=True)
    block_number = NotNull(db.Integer)
    address = db.Column(db.String(42), db.ForeignKey('wallet.address'))
    from_addr = NotNull(db.String(42))
    to_addr = NotNull(db.String(42))
    tx_timestamp = NotNull(db.Integer)
    tx_value = NotNull(db.Integer)
    tx_gas = NotNull(db.Integer)
    tx_gas_price = NotNull(db.Integer)
    tx_action = db.Column(db.String(20))
    eth_rate = db.Column(db.Float)

    def __repr__(self):
        return f'<Tx {self.tx_hash}, Address {self.address}>'

class transaction_details(db.Model):
    tx_hash = db.Column(db.String(66), db.ForeignKey('transactions.tx_hash'), primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    memo = db.Column(db.String(120))
    labels = db.Column(db.Integer, db.ForeignKey('labels.id'))

class Wallet(db.Model):
    address = db.Column(db.String(42), primary_key=True)
    is_active = NotNull(db.Boolean)
    latest_block = NotNull(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transactions = db.relationship('Transactions', backref='wallet_address', lazy='dynamic')

    def __repr__(self):
        return f'<Wallet {self.address}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    wallets = db.relationship('Wallet', backref='wallet_user', lazy='dynamic')
    contacts = db.relationship('Contact', backref='created_by', lazy='dynamic')
    labels = db.relationship('label_schema', backref='label_user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}, ID {self.id}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = NotNull(db.String(64), index=True)
    address = NotNull(db.String(42), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Contact {self.name}, Address {self.address}>'

class label_schema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_type = NotNull(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    address = db.Column(db.String(42), db.ForeignKey('wallet.address'))
    from_addr = db.Column(db.String(42))
    to_addr = db.Column(db.String(42))
    amount = NotNull(db.Integer)
    memo = db.Column(db.String(120))
    labels = db.Column(db.Integer, db.ForeignKey('labels.id'))

    def __repr__(self):
        return f'<Label Schema {self.id}>'

class Labels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    label = db.Column(db.String(64))
    is_active = NotNull(db.Boolean)
    label_schemas = db.relationship('label_schema', backref='label', lazy='dynamic')
    transaction_details = db.relationship('transaction_details', backref='tx_detail_label', lazy='dynamic')
    

    def __repr__(self):
        return f'<Label {self.id} {self.name}'