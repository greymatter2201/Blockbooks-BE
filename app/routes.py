from flask_restful import Resource, abort, marshal_with, fields
from flask import abort, request, g, jsonify
from app import db, api, celery
from app.models import (
    Transaction,
    transaction_detail,
    User,
    Wallet,
    Contact,
    Label,
    label_schema
)
from app.tasks import update_txModel, add
from app.fields import *
from siwe import generate_nonce, siwe, SiweMessage
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import or_
import re, os
from pprint import pprint


auth = HTTPTokenAuth(scheme="Bearer")

@auth.verify_token
def verify_token(token):
    user = User.verify_auth_token(token)

    if user is None:
        return False
    
    g.user = user
    return True

def verify_signature(message, signature):
        try:
            msg = SiweMessage(message)
            msg.verify(signature=signature)
        except ValueError:
            return False
        except siwe.ExpiredMessage:
            return False
        except siwe.DomainMismatch:
            return False
        except siwe.NonceMismatch:
            return False
        except siwe.MalformedSession as e:
            return False
        except siwe.InvalidSignature:
            return False
        else:
            return True

class Login(Resource):
    def post(self):
        message = request.json.get('message')
        signature = request.json.get('signature')


        if not verify_signature(message, signature):
            abort(400, "Failed Signature Verification")
 
        parse_addr = re.search(r'\n(.*?)\n', message)
        address = parse_addr.group(1)
        address = address.lower()

        user = User.query.filter_by(address=address).first()

        if user is None:
            user = User(address=address)
            db.session.add(user)
            db.session.commit()

            wallet = Wallet(
            address = address,
            chain_id = 1,
            is_active = True,
            wallet_user = user,
            )
            db.session.add(wallet)
            db.session.commit()
            
            token = user.generate_auth_token(10000)
            data = {"token": token, 'duration': 10000}
            return {"results": "success", "data": data}, 200
        else:
            token = user.generate_auth_token(10000)
            data = {"token": token, 'duration': 10000}
            return {"results": "success", "data": data}, 200
            
class Token(Resource):
    @auth.login_required
    def get(self):
        token = g.user.generate_auth_token(10000)
        data = {"token": token, 'duration': 10000}
        return {"results": "success", "data": data}, 200

class Nonce(Resource):
    def get(self):
        nonce = generate_nonce()
        return {"results": "success", "data": nonce}, 200

class Wallets(Resource):
    @auth.login_required
    def post(self):
        address = request.json.get('address')
        chain_id = request.json.get('chain_id')
        name = request.json.get('name')
        user = g.user
        address = address.lower()

        if address is None:
            abort(400, "Wallet Address needed")
        
        if Wallet.query.filter_by(address=address, user_id=user.id).first() is not None:
            abort(400, "User already registered with this Wallet Addr")
        
        wallet = Wallet(
            address = address,
            chain_id = chain_id,
            is_active = True,
            wallet_user = user,
            name = name
        )
        db.session.add(wallet)
        db.session.commit()

        update_txModel.apply_async(
            kwargs={'chain_id': chain_id, 'address': address},
            task_id = address
            )

        data = {"User": user.address, "Wallet": address}
        return {"results": "success", "data": data}, 200

    @marshal_with(wallets_field, envelope='data')
    @auth.login_required
    def get(self):
        user = g.user
        wallets = user.wallets.all()
        if wallets is None:
            abort(400, "User has not registered any wallet")
        
        return wallets, 200

class Contacts(Resource):
    @auth.login_required
    def post(self):
        name = request.json.get('name')
        address = request.json.get('address')
        user = g.user

        exist = Contact.query.filter_by(name=name, address=address, created_by=user.id).first() 
        if exist is not None:
            abort(400, "Contact already exists for this User")
        
        contact = Contact(
            name = name,
            address = address,
            contact_user = user
        )
        db.session.add(contact)
        db.session.commit()

        data = {"user": user.address, "contact": name, "address": address}
        return {"results":"success", "data": data}, 200
    
    @marshal_with(contacts_field, envelope='data')
    @auth.login_required
    def get(self):
        user = g.user
        contacts = user.contacts.all()

        if contacts is None:
            abort(400, "User has not registered any contacts")

        return contacts, 200

class Transactions(Resource):
    def post(self):
        chain_id = request.json.get('chain_id')
        address = request.json.get('address')
        update_txModel.apply_async(
            kwargs={'chain_id': chain_id, 'address': address},
            task_id = address
            )
        data = {"task_id": address}
        return {"results": "success", "data": data}, 200
    
    @auth.login_required
    @marshal_with(tx_field, envelope='data')
    def get(self):
        user = g.user
        user_id = user.id
        query_str = f'''
            select a.name as owner, t.*, td.memo, td.labels, c."name" as contact_name  from
            (select w.address, w.name, u.id as userId from blockbooks.public."user" u
            inner join blockbooks.public.wallet w on u.id = w.user_id
            where u.id = {user_id}) a
            inner join blockbooks.public."transaction" t on t.from_addr = a.address or t.to_addr = a.address
            left join blockbooks.public.transaction_detail td on td.tx_hash = t.tx_hash and td.created_by = a.userId
            left join blockbooks.public.contact c on c.created_by = a.userId and (c.address = t.from_addr or c.address = t.to_addr);
            '''

        results = db.engine.execute(query_str)
        results = [r for r in results]

        for result in results:
            if result[13] is None:
                continue
            label_ids = result[13]
            label_array = [Label.query.get(id).label for id in label_ids]
            for i in range(len(label_ids)):
                result[13][i] = label_array[i]

        if results is None:
            abort(400, "No transactions for this address on this chain")

        return results, 200



class TransactionResult(Resource):
    def get(self, address):
        address = address
        task_result = celery.AsyncResult(address)
        results = {
            "address": address,
            "task_status": task_result.status,
            "task_result": task_result.result
        }
        return {"results": "success", "data": results}, 200

class Labels(Resource):
    @auth.login_required
    def post(self):
        user = g.user
        label = request.json.get('label')

        label_exist = Label.query.filter_by(label=label, created_by=user.id).first()
        if label_exist is not None:
            abort(400, "Label already registered by User")

        l = Label(
            label = label,
            is_active = True,
            label_user = user
        )
        db.session.add(l)
        db.session.commit()

        return {"results": "success", "data": {"label": label, "user": user.address}}, 200
    
    @marshal_with(labels_field, envelope='data')
    @auth.login_required
    def get(self):
        user = g.user

        labels = user.labels.all()

        if labels is None:
            abort(400, "No labels for this user")
         
        return labels, 200


class LabelSchemas(Resource):
    @auth.login_required
    def post(self):
        # Yearly +365 days
        # Quarterly +121 days
        # Monthly +30 days
        # Weekly +7 days
        # Daily +1 days
        # label_types -> ['yearly', 'quarterly', 'monthly', 'weekly', 'daily']
        label_type = request.json.get('label_type')
        from_addr = request.json.get('from_addr')
        to_addr = request.json.get('to_addr')
        amount = request.json.get('amount')
        memo = request.json.get('memo')
        label_ids = request.json.get('labels') # -> Array of label IDs
        user = g.user

        for id in label_ids:
            label = Label.query.get(id)

            if label is None:
                continue

            l_schema = label_schema(
                label_type = label_type,
                from_addr = from_addr,
                to_addr = to_addr,
                amount = amount,
                memo = memo,
                schema_user = user,
                labels = label
            )
            db.session.add(l_schema)
        db.session.commit()

        return {"results" : "success", "data": {}}, 200

    @marshal_with(labelSchema_fields, envelope='data')
    @auth.login_required
    def get(self):
        user = g.user
        schemas = user.label_schemas.all()

        if schemas is None:
            abort(400, "User does not have any label schemas")
        
        return schemas, 200

class TransactionDetails(Resource):
    @auth.login_required
    def post(self):
        tx_hash = request.json.get('tx_hash')
        memo = request.json.get('memo')
        label_ids = request.json.get('labels')
        user = g.user

        tx = Transaction.query.filter_by(tx_hash=tx_hash).first()
        if tx is None:
            abort(400, "Tx hash does not exist")

        tx_detail = transaction_detail.query.filter_by(tx_hash=tx_hash, created_by=user.id).first()
        if tx_detail is not None:
            abort(400, "Tx detail for this user already exists")
    
        tx_detail = transaction_detail(
            details = tx,
            detail_user = user,
            memo = memo,
            labels = label_ids
        )
        db.session.add(tx_detail)
        db.session.commit()

        return {"results": "success", "data": {}}, 200
    
    @marshal_with(labelSchema_fields, envelope='data')
    @auth.login_required
    def get(self):
        user = g.user
        tx_details = user.tx_details.all()

        if tx_details is None:
            abort(400, "No transaction details for this User")
        
        return tx_details, 200

class Shutdown(Resource):
    def get(self):
        os.system('systemctl poweroff')
        return 200

api.add_resource(Shutdown, "/shutdownthispcplease")    
api.add_resource(Token, "/token")
api.add_resource(Login, "/login")
api.add_resource(Nonce, "/nonce")
api.add_resource(Wallets, "/wallets")
api.add_resource(Contacts, "/contacts")
api.add_resource(Transactions, "/transactions")
api.add_resource(TransactionResult, "/transactions/results/<address>")
api.add_resource(TransactionDetails, "/transactions/details")
api.add_resource(Labels, "/labels")
api.add_resource(LabelSchemas, "/labelschemas")



        


        

