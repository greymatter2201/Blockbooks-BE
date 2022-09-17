from app import db, app
from sqlalchemy.orm import validates
import time, jwt

# Note: nullable is False by default when primary_key=True
# Wrapper for setting column nullable to False
def NotNull(*args,**kwargs):
    kwargs["nullable"] = kwargs.get("nullable",False)
    return db.Column(*args,**kwargs)

class Transaction(db.Model):
    tx_hash = db.Column(db.String(66), primary_key=True)
    chain_id = NotNull(db.Integer)
    block_number = NotNull(db.Integer)
    from_addr = NotNull(db.String(42))
    to_addr = NotNull(db.String(42))
    tx_timestamp = NotNull(db.BigInteger)
    tx_value = NotNull(db.Integer)
    tx_gas = NotNull(db.Integer)
    tx_gas_price = NotNull(db.BigInteger)
    tx_actions = db.Column(db.String(20))
    rate = db.Column(db.Float)

    details = db.relationship('transaction_detail', backref='details', lazy='dynamic')

    def __repr__(self):
        return f'<Tx {self.tx_hash}, Address {self.address}>'

class transaction_detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(66), db.ForeignKey('transaction.tx_hash'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    memo = db.Column(db.String(120))
    labels = db.Column(db.Integer, db.ForeignKey('label.id'))

    def __repr__(self):
        return f'<Tx {self.tx_hash}, Creator {self.created_by}>'

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42))
    chain_id = db.Column(db.Integer)
    last_block_height = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean)

    @validates('address')
    def convert_lower(self, key, value):
        return value.lower()

    def __repr__(self):
        return f'<Wallet {self.address}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), index=True, unique=True)

    wallets = db.relationship('Wallet', backref='wallet_user', lazy='dynamic')
    contacts = db.relationship('Contact', backref='contact_user', lazy='dynamic')
    labels = db.relationship('Label', backref='label_user', lazy='dynamic')
    tx_details = db.relationship('transaction_detail', backref='detail_user', lazy='dynamic')
    label_schemas = db.relationship('label_schema', backref='schema_user', lazy='dynamic')
    
    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])

    @validates('address')
    def convert_lower(self, key, value):
        return value.lower()

    def __repr__(self):
        return f'<User {self.address}, ID {self.id}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = NotNull(db.String(64), index=True)
    address = NotNull(db.String(42), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    @validates('address')
    def convert_lower(self, key, value):
        return value.lower()
        
    def __repr__(self):
        return f'<Contact {self.name}, Address {self.address}>'

class label_schema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_type = NotNull(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_addr = db.Column(db.String(42))
    to_addr = db.Column(db.String(42))
    amount = NotNull(db.Integer)
    memo = db.Column(db.String(120))
    labels = db.Column(db.Integer, db.ForeignKey('label.id'))

    def __repr__(self):
        return f'<Label Schema {self.id}>'

class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    label = db.Column(db.String(64))
    is_active = NotNull(db.Boolean)
    label_schemas = db.relationship('label_schema', backref='label', lazy='dynamic')
    tx_details = db.relationship('transaction_detail', backref='detail_label', lazy='dynamic')
    
    def __repr__(self):
        return f'<Label {self.id} Name {self.name}>'