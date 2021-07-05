# Crypto exchange

### Description:
I made a rest-api service that allows users to *buy* and *sell* some currencies.   
    
### Create venv:
```bash
make venv
```

### Run tests:
```bash
make test
```
    
### Run linters:
```bash
make lint
```
    
### Run formatters:
```bash
make format
```

### Run server:
```bash
make init_db # initialize the database 
make up
```

### Run bot:
```bash
make bot
```

## API Documentation

All methods return the pydantic `ResponseModel` object, which has these fields: `status`(can be `ok` or `error`), 
`error`(can be `null` or description of error) and `data`(can be `null` or data of method).

### /currency/add
#### Method: POST
#### Body: {"name": *name*} 
By this method you can add a new currency with the name *name* if it does not exist.

### /user/get_info
#### Method: GET
#### Body: {"id": *id*}

This method returns the information about user(if user exists) in such schema: 
```json
{
    "id": user_id,
    "name": user_name,
    "balance": user_balance,
    "registration_date":  user_registration_date,
    "wallet": [
        {
            "currency_id": user_wallet_currency_id,
            "currency_name": user_wallet_currency_name,
            "balance": balance_of_wallet,
            "history": [
                {
                    "id": operation_id,
                    "currency_id": user_wallet_currency_id,
                    "currency_history_id": user_wallet_currency_history_id,
                    "type": type_of_operation,
                    "amount": amount_of_currency,
                    "time": timestamp_of_operation,
                    "exchange_rate": currency_exchange_rate,
                },
                ...
            ]
        },
        ...
    ]
}
```
### /user/register
#### Method: POST
#### Body: {"name": *username*}
Adds user to database(if user does not exists yet) and returns `user_id` of added user.


### /currency/operation
#### Method: POST
#### Body: {"operation": *operation*, "user_id": *user_id*, "currency_name": *currency_name*, "count": *count*, "timestamp": *timestamp*}

This method do an *operation*(`sell` or `buy`) for user with id=*user_id* with currency name=*currency_name* and by an amount of *count*.
The *timestamp* should be the timestamp of requesting this method.

Returns `ok` or `error` with description.

### /currency/get_info
#### Method: GET
#### Body: {"name": *currency_name*}
This method returns information about currency with name=*currency_name*

Return data schema:
```json
{
    "id": currency_id,
    "name": currency_name,
    "exchange_rate": exchange_rate(in str)
}
```
Where `exchange_rate` is Decimal with accuracy up to 5 digits after the dot.

### /currency/all
#### Method: GET
#### Body: *no*

This method returns all ids of available currencies.

Return schema:
```json
[
    currency_id1,
    currency_id2,
    currency_id3,
    ...
]
```
