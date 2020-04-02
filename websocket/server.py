#!/usr/bin/env python

# WS server

import asyncio
import websockets
import json


#!/usr/bin/env python

from my_schema import *
from market import Market
from gather import Gather
from jsonwrapper import JsonWrapper
from player import *


# my imported modules
gatherObj = Gather()
marketObj = Market()


# create new tables that didn't previously exist(only needs to run once)
# Fortress.__table__.create(db.session.bind)

class Server:
    async def handle(self, websocket, path):
        data = await websocket.recv()
        print(f"Client < \t {data}")

        data = json.loads(data)
        action = data["Message"]

        if(action == "!join"):
            username = new_user(JsonWrapper(data))
            data_to_send = join_user(username)
        elif(action == "!gather"):
            data_to_send = gather(JsonWrapper(data))
        elif(action == "!inventory"):
            data_to_send = get_user_inventory(JsonWrapper(data))
        elif(action == "!ship"):
            data_to_send = buy_ship(JsonWrapper(data))
        elif(action == "!upgrade"):
            data_to_send = buy_upgrade(JsonWrapper(data))
        elif(action == "!deposit"):
            data_to_send = deposit(JsonWrapper(data))
        elif(action == "!login"):
            data_to_send = login(JsonWrapper(data))
        # elif(action == "!move"):
        #     data_to_send = move(JsonWrapper(data))
        else:
            await websocket.send("Failed, the server did not understand the Message content: " + json.dumps(data))
            return(False)
        print(f"Server > \t {data_to_send} \n")
        await websocket.send(json.dumps(data_to_send))
        return(True)


# def move(client_data):
#     username = client_data.get('Username')


def gather(client_data):
    username = client_data.get('Username')
    user = User.query.filter_by(username=username).first()
    all_user_items = Item.query.filter_by(userid=user.id).all()
    # if inventory is full, do not gather an item
    user.inventorysize = 100
    if(len(all_user_items) > user.inventorysize):
        return('"UserId": {}, "Result": False').format(username)
    item_gathered = gatherObj.gather_random()[0]
    # if the item is not in user.items and the number of items in user items is less than inventory size
    item = Item(name=item_gathered, count=1)
    user.inventory.append(item)
    db.session.add(user)
    db.session.add(item)
    db.session.commit()
    response = {
        "UserId": user.twitchuserid,
        "Name": user.username,
        "Result": True,
        "Items": item.name  # items that were gathered
    }
    return(response)


def buy_upgrade(client_data):
    username = client_data.get('Username')
    upgrade = client_data.get('Upgrade')
    ship = client_data.get('Ship')
    user = User.query.filter_by(username=username).first()
    currency = Currency.query.filter_by(userid=user.id).first()
    user_ship = Ship.query.filter_by(
        userid=user.id).filter_by(type=ship).first()
    result = False
    if(user_ship != None):
        upgrades = Upgrade.query.filter_by(
            shipid=user_ship.id, type=upgrade).first()
        if(upgrades == None):
            cost_of_upgrade = marketObj.get_cost(upgrade)
            if(cost_of_upgrade < currency.count):
                currency.count -= cost_of_upgrade
                purchased_upgrade = Upgrade(shipid=user_ship.id, type=upgrade)
                db.session.add(purchased_upgrade)
                db.session.add(currency)
                db.session.commit()
                result = True
        else:
            result = True
    response = {
        "UserId": user.twitchuserid,
        "Name": user.username,
        "Result": result,
        "Ship": ship,
        "Upgrade": upgrade
    }
    return(response)


def buy_ship(client_data):
    username = client_data.get('Username')
    ship = client_data.get('Ship')
    user = User.query.filter_by(username=username).first()
    currency = Currency.query.filter_by(userid=user.id).first()
    user_ship = Ship.query.filter_by(
        userid=user.id).filter_by(type=ship).first()
    result = False
    ship_type = ""
    msg = "Ship NOT purchased"

    if(user_ship == None):  # this user already owns this ship
        cost_of_ship = marketObj.get_cost(ship)
        if(currency.count > cost_of_ship):
            currency.count -= cost_of_ship
            purchased_ship = Ship(userid=user.id, type=ship)
            ship_type = purchased_ship.type
            db.session.add(purchased_ship)
            db.session.add(currency)
            db.session.commit()
            msg = "Ship purchased"
            result = True
    else:
        msg = "User already owns this ship"
        result = True
    response = {
        "UserId": user.twitchuserid,
        "Name": user.username,
        "Result": result,
        "Ship": ship,
        "Note": msg
    }
    return response


def get_user_inventory(client_data):
    username = client_data.get('Username')
    user = User.query.filter_by(username=username).first()
    item = Item.query.filter_by(userid=user.id).all()
    item_list = []
    if(len(item) != 0):
        for i in range(len(item)):
            item_list.append(item[i].name)
    response = {
        "UserId": user.twitchuserid,
        "Name": user.username,
        "Result": True,
        "Items": item_list
    }
    return(response)


def login(client_data):
    username = client_data.get('Username')
    fort_name = client_data.get('Fortress')
    alliance_name = client_data.get('Alliance')
    print("ALLIANCE NAME:", alliance_name)
    fort = Fortress.query.filter_by(name=fort_name).first()
    alliance = Fortress.query.filter_by(name=alliance_name).first()
    if(alliance is None):
        alliance = Alliance(name=username)
        db.session.add(alliance)
        db.session.commit()
        alliance = Alliance.query.filter_by(name=alliance_name).first()
    if(fort is None):
        alliance = Alliance.query.filter_by(name=alliance_name).first()
        fort = Fortress(name=username, allianceid=alliance.id)
    item_list = Item.query.filter_by(fortressid=fort.id).all()
    item_list_str = []
    for item in item_list:
        item_list_str.append(item.name)
    db.session.add(fort)
    db.session.commit()
    response = {
        "Name": username,
        "Fortress": fort.name,
        "Alliance": alliance.name,
        "Result": True,
        "Items": item_list_str
    }
    return(response)


'''
Sell items to the fortress
'''


def deposit(json):
    username = json.get('Username')
    fortress = json.get('Fortress')
    user = User.query.filter_by(username=username).first()
    fort = Fortress.query.filter_by(name=fortress).first()
    print("FORTRESS:", fortress, fort)
    items = Item.query.filter_by(userid=user.id).all()
    sold_items_arr = []

    for item in items:
        for i in range(item.count):
            sold_items_arr.append(item.name)
        fort_item = Item.query.filter_by(
            fortressid=fort.id).filter(Item.count >= 1).first()
        if(fort_item == None):
            item.fortressid = fort.id
            item.userid = None
        else:
            fort_item.count += item.count
            item.count = 0

        db.session.add(item)
        db.session.add(fort)

    sell_value = gatherObj.get_sell_value(sold_items_arr)
    currency = Currency.query.filter_by(userid=user.id).first()

    if(currency == None):
        currency = Currency(userid=user.id, count=sell_value)
    else:
        currency.count += sell_value

    db.session.add(currency)
    db.session.commit()
    response = {
        "Result": True,
        "Fortress": fort.name,
        "Items": sold_items_arr,
        "Value": sell_value
    }
    return(response)


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


'''
Create a new user by supplying json in a post request with username and password key value pairs.
Example: `curl -i -X POST -H "Content-Type: application/json" -d '{"username":"kicksent","password":"python"}' http://127.0.0.1:5000/api/users`
'''


def new_user(json):

    username = json.get('Username')
    # check db for this username
    user = User.query.filter_by(username=username).first()
    if user is not None:
        # existing user
        return(username)
    twitchuserid = json.get('UserId')
    email = json.get('Email')
    color = json.get('Color')
    isModerator = json.get('IsModerator')
    isSubscriber = json.get('IsSubscriber')

    print(f"{username} {twitchuserid} {email} {color} {isModerator} {isSubscriber}")

    # new users will have this automatically generated
    user = User(username=username, twitchuserid=int(twitchuserid), email=email,
                color=color, isModerator=bool(isModerator), isSubscriber=bool(isSubscriber))
    db.session.add(user)
    db.session.commit()
    currency = Currency(userid=user.id, count=0)
    db.session.add(currency)
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    if(user == None):
        return("NO USER CREATED")
    return (username)


def get_users():
    user = User.query.all()
    if not user:
        abort(400, "No users found.")
    data = {'users': []}
    for item in user:
        data['users'].append(item.username)
    return jsonify(data, 201, {'Location': url_for('get_users',  _external=True)})


def join_user(username):
    user = User.query.filter_by(username=username).first()
    playerList["user"] = Player(user.username, [user.x, user.y])
    show_logged_in()
    return {
        'UserId': user.twitchuserid,
        'Name': user.username,
        'Skills': {
            'Melee': user.meleeAtkXp,
            'Mage': user.magicAtkXp,
            'Range': user.rangeAtkXp,

            'Size': user.sizeXp,
            'Health': user.healthXp,
            'Shield': user.healthXp,
            'Evasion': user.evasionXp,
            'Block': user.blockXp,
            'Resist': user.ResistXp,

            'Speed': user.speedXp,
        }
    }


def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({
        'username': 'Hello, %s!' % user.username,
        'stats': {
            'meleeAtkXp': user.meleeAtkXp,
            'mageAtkXp': user.magicAtkXp,
            'rangeAtkXp': user.rangeAtkXp,

            'sizeXp': user.sizeXp,
            'healthXp': user.healthXp,
            'shieldXp': user.healthXp,
            'evasionXp': user.evasionXp,
            'blockXp': user.blockXp,
            'ResistXp': user.ResistXp,

            'speedXp': user.speedXp,
        }
    }, 201, {'Location': url_for('get_user_by_id', id=user.id, _external=True)})


@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


'''
Login with your user credentials to see your stats, email, and user id.
'''


@auth.login_required
def get_resource():
    return jsonify({
        'username': 'Hello, %s!' % g.user.username,
        'id': g.user.id,
        'stats': {
            'email': g.user.email,
            'meleeAtkXp': g.user.meleeAtkXp,
            'mageAtkXp': g.user.magicAtkXp,
            'rangeAtkXp': g.user.rangeAtkXp,
            'sizeXp': g.user.sizeXp,
            'healthXp': g.user.healthXp,
            'shieldXp': g.user.healthXp,
            'evasionXp': g.user.evasionXp,
            'blockXp': g.user.blockXp,
            'ResistXp': g.user.ResistXp,

            'speedXp': g.user.speedXp,
        }
    }, 201, {'Location': url_for('get_resource', _external=True)})


def run_server():
    if not os.path.exists('database/db.sqlite'):
        print("Creating database")
        db.create_all()

    s = Server()

    start_server = websockets.serve(s.handle, "localhost", 5555)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    run_server()
