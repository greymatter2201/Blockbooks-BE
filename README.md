# Blockbooks

# Docker
```sh
cd into project

#Build
docker-compose up -d --build

#Create DB
docker exec -it <container name> psql -U username -d postgres -c "CREATE DATABASE blockbooks;"

#Delete DB
docker exec -it <container name> psql -U username -d postgres -c "DROP DATABASE <dbname>;"

#Apply DB migrations
docker-compose exec web python manage.py create_db

#Update DB migrations
docker-compose exec web python manage.py update_db
```




# API
Any API that requires AUTH
```
headers={'Authorization': "Bearer <token>"}
```

# Login
```
POST/login
{
    "message": "msg", 
    "signature": "sign"
}

data = {"token": token, 'duration': 600}
return {"results": "success", "data": data}, 200

```
# Token (Auth)
```
GET/token

data = {"token": token, 'duration': 600}
return {"results": "success", "data": data}, 200
```
# Nonce
```
GET/nonce
return {"results": "success", "data": nonce}, 200
```
# Wallets (Auth)
```
POST/wallets
{
    'address' = address,
    'chain_id' =  chain_id,
    'name' =  name
}

data = {"User": user.address, "Wallet": address}
return {"results": "success", "data": data}, 200
```
```
GET/wallets
return {"data": {}}, 200
```
# Contacts (Auth)
```
POST/contacts
{
    'name' = name,
    'address' =  address,
}

data = {"user": user.address, "contact": name, "address": address}
return {"results":"success", "data": data}, 200
```
```
GET/wallets
return {"data": {}}, 200
```
# Transactions
```
POST/transactions (Update tx)
{
    'chain_id' = chain_id,
    'address' =  address,
}

data = {"task_id": address}
return {"results": "success", "data": data}, 200
```
```
GET/transactions (AUTH)
return {"data": {}}, 200
```
# Transaction Results
Check whether tx has been updated after POST/tx
```
GET/transactions/results/<address>
results = {
            "address": address,
            "task_status": task_result.status,
            "task_result": task_result.result
        }
return {"results": "success", "data": results}, 200
```
# Labels
```
POST/labels
{
    'label' = label
}
data = {"label": label, "user": user.address}
return {"results": "success", "data": data }, 200
```
```
GET/labels

return {'data': {}}, 200
```
# Label Schema
For automated labeling
```
POST/labelschemas
{
    'label_type': label_type,
    'from_addr': from_addr,
    'to_addr': to_addr,
    'amount': amount,
    'memo': memo,
    'label_ids': label_ids
}

return {"results" : "success", "data": {}}, 200
```
```
GET/labelschemas
return {'data': {}}, 200
```
# Transaction Details
```
POST/transactions/details
{
    'tx_hash': tx_hash,
    'memo': memo,
    'label_ids': labels,
}

return {"results" : "success", "data": {}}, 200
```
```
GET/transaction/details
return {'data': {}}, 200
```
