from unittest import TestCase
from app import app, db
from app.models import Transaction, Label, User
from config import TestConfig
from tasks import update_txModel
import pytest

@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
class TestAPI(TestCase):

    user_data = {"username": "james", "password": "123"}
    siwe_data = {
    'message': "localhost:8080 wants you to sign in with your Ethereum account:\n0x9D85ca56217D2bb651b00f15e694EB7E713637D4\n\nSign in with Ethereum to the app.\n\nURI: http://localhost:8080\nVersion: 1\nChain ID: 1\nNonce: spAsCWHwxsQzLcMzi\nIssued At: 2022-01-29T03:22:26.716Z",
    'signature': '0xe117ad63b517e7b6823e472bf42691c28a4663801c6ad37f7249a1fe56aa54b35bfce93b1e9fa82da7d55bbf0d75ca497843b0702b9dfb7ca9d9c6edb25574c51c',
    }
    eth_address = "0x03d15Ec11110DdA27dF907e12e7ac996841D95E4".lower()
    siwe_addr = "n0x9D85ca56217D2bb651b00f15e694EB7E713637D4".lower()
    headers = {"Content-Type": "application/json"}

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        app.config.from_object(TestConfig)
        db.session.remove()
        db.drop_all()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def get_token(self):
        response = self.client.post(
            '/login',
            json={"message": self.siwe_data['message'], "signature": self.siwe_data['signature']},
            headers=self.headers
        )
        token = response.json['data']['token']
        return token

    def commit_tx(self):
        tx = Transaction(
            tx_hash = "0xaa45b4858ba44230a5fce5a29570a5dec2bf1f0ba95bacdec4fe8f2c4fa99338",
            chain_id = '1',
            block_number = 14923692,
            from_addr = "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
            to_addr = "0x03d15Ec11110DdA27dF907e12e7ac996841D95E4",
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
    
    def commit_user(self):
        user = User(address="james@address.com")
        db.session.add(user)
        db.session.commit()
        return user

    def test_login_siwe(self):
        response = self.client.post(
            '/login',
            json={"message": self.siwe_data['message'], "signature": self.siwe_data['signature']},
            headers=self.headers
        )
        assert response.status_code == 200
    
    def test_login_siwe_fail(self):
        response = self.client.post(
            '/login',
            json={"message": self.siwe_data['message'], "signature": "willywanker"},
            headers=self.headers
        )
        assert response.status_code == 400
    
    def test_auth_token(self):
        token = self.get_token()
        response = self.client.get('/token', headers={'Authorization': f"Bearer {token}"})
        assert response.status_code == 200
    
    def test_post_wallet(self):
        token = self.get_token()
        post_wallet = self.client.post(
            '/wallets',
            json={"address": self.eth_address, "chain_id": "1"},
            headers={'Authorization': f"Bearer {token}"}
        )

        task_issued = self.client.get(f'/transactions/results/{self.eth_address}', headers=self.headers)

        assert post_wallet.status_code == 200
        assert task_issued.json['data']['task_status'] == 'SUCCESS' or 'PENDING'
    
    def test_get_wallet(self):
       token = self.get_token()
       post_wallet = self.client.post(
        '/wallets',
        json={"address": self.eth_address, "chain_id": "1"},
        headers={'Authorization': f"Bearer {token}"}
        )

       get_wallet = self.client.get(
            '/wallets',
            headers={'Authorization': f"Bearer {token}"}
        )

       assert get_wallet.status_code == 200
       assert get_wallet.json['data']['1'] == self.eth_address
    
    def test_post_contacts(self):
        token = self.get_token()
        post_contact = self.client.post(
            '/contacts',
            json={'name': 'Henry', 'address': '0x123456'},
            headers={'Authorization': f"Bearer {token}"}
        )

        assert post_contact.status_code == 200
    
    def test_get_contacts(self):
        token = self.get_token()
        post_contact = self.client.post(
            '/contacts',
            json={'name': 'Henry', 'address': '0x123456'},
            headers={'Authorization': f"Bearer {token}"}
        )

        get_contact = self.client.get(
            '/contacts',
            headers={'Authorization': f"Bearer {token}"}
        )

        addr = get_contact.json['data']['1']['address']
        name = get_contact.json['data']['1']['name']

        assert get_contact.status_code == 200
        assert addr == '0x123456'
        assert name == 'Henry'
    
    def test_get_transactions(self):
        token = self.get_token()
        self.commit_tx()

        get_tx = self.client.get(
            f'/transactions/1/{self.eth_address}',
            headers = self.headers
        )

        assert get_tx.status_code == 200
    
    def test_post_label(self):
        token = self.get_token()
        post_label = self.client.post(
            '/labels',
            json={'label': 'Salary'},
            headers={'Authorization': f"Bearer {token}"}
        )

        assert post_label.status_code == 200
    
    def test_get_label(self):
        token = self.get_token()
        post_label = self.client.post(
            '/labels',
            json={'label': 'Salary'},
            headers={'Authorization': f"Bearer {token}"}
        )

        get_label = self.client.get(
            '/labels',
            headers={'Authorization': f"Bearer {token}"}
        )

        assert get_label.status_code == 200
        assert get_label.json['data']['1']['label'] == 'Salary'
    
    def test_post_labelSchema(self):
        token = self.get_token()
        json_schema = {
            'label_type': 'monthly',
            'from_addr': '0x123',
            'to_addr': '0x321',
            'amount': '100000000',
            'memo': 'Bonus',
            'labels': ['1']
        }
        post_labelSchema = self.client.post(
            '/labelschemas',
            json = json_schema,
            headers={'Authorization': f"Bearer {token}"}
        )
        assert post_labelSchema.status_code == 200
    
    def test_get_labelSchema(self):
        token = self.get_token()
        json_schema = {
            'label_type': 'monthly',
            'from_addr': '0x123',
            'to_addr': '0x321',
            'amount': '100000000',
            'memo': 'Bonus',
            'labels': ['1']
        }
        post_labelSchema = self.client.post(
            '/labelschemas',
            json = json_schema,
            headers={'Authorization': f"Bearer {token}"}
        )

        get_labelSchema = self.client.get(
            '/labelschemas',
            headers={'Authorization': f"Bearer {token}"}
        )
        assert get_labelSchema.status_code == 200
        assert get_labelSchema.json['data'] is not None

    def test_post_txDetails(self):
        token = self.get_token()
        self.commit_tx()
        self.commit_label()
        post_detail = self.client.post(
            'transactions/details',
            json={'tx_hash': '0xaa45b4858ba44230a5fce5a29570a5dec2bf1f0ba95bacdec4fe8f2c4fa99338', 'memo': 'Yeet', 'labels': ['1']},
            headers={'Authorization': f"Bearer {token}"}
        )
        assert post_detail.status_code == 200
    
    def test_get_txDetails(self):
        token = self.get_token()
        self.commit_tx()
        self.commit_label()
        post_detail = self.client.post(
            'transactions/details',
            json={'tx_hash': '0xaa45b4858ba44230a5fce5a29570a5dec2bf1f0ba95bacdec4fe8f2c4fa99338', 'memo': 'Yeet', 'labels': ['1']},
            headers={'Authorization': f"Bearer {token}"}
        )

        get_detail = self.client.get(
            'transactions/details',
            headers={'Authorization': f"Bearer {token}"}
        )

        assert get_detail.status_code == 200

    



        
