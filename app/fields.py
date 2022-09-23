from flask_restful import fields

tx_field = {
    'owner': fields.String,
    'tx_hash': fields.String,
    'chain_id': fields.Integer,
    'block_number': fields.String,
    'from_addr': fields.String,
    'to_addr': fields.String,
    'tx_timestamp': fields.Integer,
    'tx_value': fields.Integer,
    'tx_gas': fields.Integer,
    'tx_gas_price': fields.Integer,
    'tx_actions': fields.String,
    'rate': fields.Float,
    'memo': fields.String,
    'labels': fields.List(fields.String, default=[]),
    'contact_name': fields.String
}

tx_field2 = {
    'tx_hash': fields.String,
    'chain_id': fields.Integer,
    'block_number': fields.String,
    'from_addr': fields.String,
    'to_addr': fields.String,
    'tx_timestamp': fields.Integer,
    'tx_value': fields.Integer,
    'tx_gas': fields.Integer,
    'tx_gas_price': fields.Integer,
    'tx_actions': fields.String,
    'rate': fields.Float,
    'name': fields.String
}


wallets_field = {
    'id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'chain_id': fields.Integer,
    'last_block_height': fields.Integer,
    'user_id': fields.Integer,
    'is_active': fields.Boolean
}

contacts_field = {
    'id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'created_by': fields.Integer
}


labelSchema_fields = {
    'id': fields.Integer,
    'label_type': fields.String,
    'created_by': fields.Integer,
    'from_addr': fields.String,
    'to_addr': fields.String,
    'amount': fields.Integer,
    'memo': fields.String,
    'labels': fields.Integer
}

txDetail_fields = {
    'id': fields.Integer,
    'tx_hash': fields.String,
    'created_by': fields.Integer,
    'memo': fields.String,
    'labels': fields.Integer
}

labels_field = {
    'id': fields.Integer,
    'created_by': fields.Integer,
    'label': fields.String,
    'is_active': fields.Boolean
}




