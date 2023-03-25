from aiohttp import web
from aiohttp.web_request import Request
from app.config import Config, WITHDRAW, DEPOSIT
from app.models import User, Transaction
from datetime import datetime
from random import random


log = Config.LOG


async def create_user(request: Request) -> web.Response:
    """
    Method: POST
    REST API добавление пользователя

    Example:
    $ curl -X POST -H "Content-Type: application/json" -d '{"name": "petya"}' http://localhost:8000/v1/user
    :param request: aiohttp.web_request.Request
    :return: success json-message with new user id, error text otherwise
    """
    try:
        data = await request.json()
        name = data.get('name')
        user_id = int(random() * 1e5)

        balance = '0.00'
        new_user = User(id=user_id, name=name, balance=balance)
        try:
            await new_user.create()

            response = {"id": user_id, "name": name, "balance": balance}
            status = 201
            log.info(f"New user added: {response}")
        except Exception as err:
            response = {"error": str(err)}
            status = 400
            log.error(response)
    except Exception as err:
        status = 400
        response = {"error": f"There is no data in request body via POST-request. It says: {err}"}
        log.exception(response)

    return web.json_response(response, status=status)


async def get_user_balance(request: Request) -> web.Response:
    """
    REST API получить текущий баланс пользователя (без селекта всех транзакций)
    или баланс за дату (например, запрос "сколько у Васи было денег 5.05.2022 00:00")

    Examples:
    $ curl http://localhost:8000/v1/user/200
    $ curl http://localhost:8000/v1/user/200?date=2023-01-05T00:00:00.00000000
    :param request: aiohttp.web_request.Request
    :return: json with balance
    """
    user_id = request.match_info['id']
    date = request.rel_url.query.get('date', '')
    if date:
        key = 'amount'
        date_parts = date.split(".")
        timestamp = datetime.strptime(date_parts[0], '%Y-%m-%dT%H:%M:%S')
        obj = await Transaction.query.where(
            (Transaction.user_id == int(user_id)) &
            (Transaction.timestamp == timestamp)
        ).gino.first()
    else:
        key = 'balance'
        obj = await User.query.where(User.id == int(user_id)).gino.first()

    if obj:
        data = obj.to_dict()
        response = {'balance': str(data[key])}
        status = 200
        log.info(response)
    else:
        response = {'error': f"There is no users in database with id: {user_id}"}
        status = 402
        log.exception(response)

    return web.json_response(response, status=status)


async def get_transaction(request: Request) -> web.Response:
    """
    REST API получить информацию о транзакции

    Example:
    $ curl http://localhost:8000/v1/transaction/410eb361-4955-4078-97c0-7a22d1ec8c10
    :param request: aiohttp.web_request.Request
    :return: info about transaction
    """
    transaction_id = request.match_info['uid']
    transaction = await Transaction.query.where(Transaction.uid == transaction_id).gino.first()
    if transaction:
        response = transaction.to_dict()
        response['uid'] = str(response['uid'])
        response['amount'] = str(response['amount'])
        response['timestamp'] = str(response['timestamp'])
        log.info(f'Get transaction: {response}')
        status = 200
        log.info(response)
    else:
        status = 402
        response = {"error": f"There is no transaction with uid: {transaction_id}"}
        log.exception(response)
    return web.json_response(response, status=status)


async def add_transaction(request: Request):
    """
    REST API добавление транзакции (DEPOSIT или WITHDRAW)

    Example:\n
    $ curl -X POST -H "Content-Type: application/json"
        -d '{"uid": "410eb361-4955-4078-97c0-7a22d1ec8c10", "type": "DEPOSIT",
        "amount": "100.0", "timestamp": "2023-01-04T00:00:00"}' http://localhost:8000/v1/transaction/transaction
    :param request: aiohttp.web_request.Request
    :return: some info about success transaction error text otherwise
    """
    try:
        data = await request.json()
        uid = data.get('uid')
        user_id = data.get('user_id')
        _type = data.get('type')
        amount = float(data.get('amount'))
        timestamp = data.get('timestamp')
    except Exception as no_data:
        response = {"error": f"There is no data in the body of POST-request. It says: {no_data}"}
        log.exception(response)
        return web.json_response(response, status=402)

    operation = _type.lower()

    if operation not in (DEPOSIT, WITHDRAW):
        response = {"error": f"The transactions have no type: {operation}. ({DEPOSIT}, {WITHDRAW} implemented only)"}
        log.exception(response)
        return web.json_response(response)
    else:

        user_object = await User.get(int(user_id))
        try:
            balance = float(user_object.balance)
        except KeyError:
            err_msg = f"There is no user with id: {user_id}"
            response = {"error": err_msg}
            log.error(response)
            return web.json_response(response)

        if balance - amount < 0 and operation == WITHDRAW:
            response = {'error': f"There is not enough balance ({balance}) to {operation} with {amount}"}
            log.exception(response)
            status = 402
        else:

            date_format = '%Y-%m-%dT%H:%M:%S'
            timestamp = datetime.strptime(timestamp, date_format)
            new_transaction = Transaction(
                uid=uid, user_id=int(user_id), type=operation.upper(), amount=amount, timestamp=timestamp
            )
            try:
                await new_transaction.create()
                response = {
                    "uid": str(uid), "user_id": user_id, "type": operation,
                    "amount": amount, "timestamp": str(timestamp)
                }
                log.info(f"New transaction added: {response}")
            except Exception as err:
                status = 200
                response = {"message": str(err)}
                log.info(response)
            else:
                if operation == DEPOSIT:
                    new_balance = balance + amount
                else:
                    new_balance = balance - amount

                await User.update.values(balance=new_balance).where(User.id == int(user_id)).gino.status()
                status = 200
                response = {'text': "Success. Update user balance via new transaction"}
                log.info(response)

        return web.json_response(response, status=status)


def add_routes(app):
    app.router.add_route('POST', r'/v1/user', create_user, name='create_user')
    app.router.add_route('GET', r'/v1/user/{id}', get_user_balance, name='get_user')
    app.router.add_route('POST', r'/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{uid}', get_transaction, name='incoming_transaction')
