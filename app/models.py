from app import db
from sqlalchemy.dialects.postgresql import JSON

# Note: nullable is False by default when primary_key=True
# Wrapper for setting column nullable to False
def NullColumn(*args,**kwargs):
    kwargs["nullable"] = kwargs.get("nullable",False)
    return db.Column(*args,**kwargs)

# class Transactions(db.Model):
#     __tablename__='transactions'

# class Wallet(db.Model):
#     __tablename__='wallet'

class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))

    def __repr__(self):
        return f'<User {self.email}, ID {self.id}>'

# class Contact(db.Model):
#     __tablename__='contact'

# class label_schema(db.Model):
#     __tablename__='label_schema'

# class transaction_details(db.Model):
#     __tablename__='transaction_details'

# class Labels(db.Model):
#     __tablename__='labels'