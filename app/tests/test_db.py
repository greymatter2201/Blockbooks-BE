# Bring your packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'Blockbooks_BE', 'app')))
from app.models import (
    Transaction,
    transaction_detail,
    User,
    Wallet,
    Contact,
    label_schema,
    Label
)

from unittest import TestCase
from config import TestConfig
from app import db, app

# Tests whether model can be created, populated and looked up
class TestModelLookup(TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        db.session.remove()
        db.drop_all()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def commit_user(self):
        user = User(address="james@address.com")
        db.session.add(user)
        db.session.commit()
        return user
    
    def commit_tx(self):
        tx = Transaction(
            tx_hash = "0xaa45b4858ba44230a5fce5a29570a5dec2bf1f0ba95bacdec4fe8f2c4fa99338",
            chain_id = '1',
            block_number = 14923692,
            from_addr = "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
            to_addr = "0xc5102fe9359fd9a28f877a67e36b0f050d81a3cc",
            tx_timestamp = 1654646570,
            tx_value = 0,
            tx_gas = 6000000,
            tx_gas_price = 125521409858,
            tx_actions = "Swap",
            rate = 1800.2
        )
        db.session.add(tx)
        db.session.commit()
        return tx
    
    def commit_label(self):
        self.commit_user()
        user = User.query.first()
        label = Label(
            label = "This is a label",
            is_active = True,
            label_user = user
        )
        db.session.add(label)
        db.session.commit()
        return label

    def test_user(self):
        user = self.commit_user()
        users = User.query.all()
        assert user in users
    
    def test_user_auth_token(self):
        user = self.commit_user()
        token = user.generate_auth_token()
        verify = User.verify_auth_token(token)
        assert verify == user
    
    def test_Transaction(self):
        tx = self.commit_tx()
        txs = Transaction.query.all()
        assert tx in txs
    
    def test_wallet(self):
        user = self.commit_user()
        user = User.query.get(1)

        wallet = Wallet(
            address = "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
            chain_id = 1,
            last_block_height = 15533388,
            is_active = True,
            wallet_user = user
        )
        db.session.add(wallet)
        db.session.commit()

        wallets = Wallet.query.all()
        assert wallet in wallets
    
    def test_contact(self):
        user = self.commit_user()
        user = User.query.get(1)

        contact = Contact(
            name = "James",
            address = "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
            contact_user = user
        )
        db.session.add(contact)
        db.session.commit()

        contacts = Contact.query.all()
        assert contact in contacts
    
    def test_Label(self):
        label = self.commit_label()
        Labels = Label.query.all()
        assert label in Labels
    
    def test_label_schema(self):
        label = self.commit_label()
        label = Label.query.get(1)

        user = User.query.get(1)

        label_scheme = label_schema(
            label_type = "Monthly",
            from_addr = "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
            to_addr = "0xc5102fe9359fd9a28f877a67e36b0f050d81a3cc",
            amount = 5,
            memo = "Monthly Salary",
            schema_user = user,
            label = label
        )

        db.session.add(label_scheme)
        db.session.commit()

        label_schemes = label_schema.query.all()
        assert label_scheme in label_schemes

    def test_transaction_detail(self):
        label = self.commit_label()
        label = Label.query.get(1)

        user = User.query.get(1)
        
        tx = self.commit_tx()
        tx = Transaction.query.first()

        tx_detail = transaction_detail(
            tx_hash = "0x12345",
            memo = "Sent ETH for Food",
            details = tx,
            detail_user = user,
            detail_label = label
        )

        db.session.add(tx_detail)
        db.session.commit()

        tx_details = transaction_detail.query.all()
        assert tx_detail in tx_details