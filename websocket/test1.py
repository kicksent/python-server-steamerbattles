import unittest
from unittest.mock import MagicMock, Mock, AsyncMock, patch
import json


import asyncio
import websockets
from websockets.server import WebSocketServerProtocol

# causing circular dependency when loading
from server import Server, Item, Alliance, Fortress, User
from player import *
'''
Current list of test users andd their uses:
    test: This user is rich and can buy anything, sell his items
    poor: poor user, don't let him sell items, he is poor, and will stay that way. Thus he also has a full inventory
    minimalist: this user has an empty inventory
    riches: already has every item in the game, but ironically no money
    
Note with naming tests:
    New tests MUST start with test to be called automatically by the testing tools
    By convention, I have been naming the tests using this template: test_<username>_<action> for example the method test_poor_join is testing the "!join" action with user "poor"
'''


class TestServerAction_join(unittest.IsolatedAsyncioTestCase):
    async def test_test_join(self):
        json_request = json.dumps({"Message": "!join", "Username": "test", "UserId": "123",
                                   "Email": "test@sad.com", "Color": "FireBurn", "IsModerator": "False", "IsSubscriber": "False"})
        expected = json.dumps({"UserId": 123, "Name": "test", "Skills": {"Melee": 0, "Mage": 0, "Range": 0,
                                                                         "Size": 0, "Health": 0, "Shield": 0, "Evasion": 0, "Block": 0, "Resist": 0, "Speed": 0}})
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        await s.handle(mocked_socket, mock_path)
        mocked_socket.send.assert_called_with(expected)

    async def test_poor_join(self):
        json_request = json.dumps({"Message": "!join", "Username": "poor", "UserId": "100",
                                   "Email": "poor@sad.com", "Color": "FireBurn", "IsModerator": "False", "IsSubscriber": "False"})
        expected = json.dumps({"UserId": 100, "Name": "poor", "Skills": {"Melee": 0, "Mage": 0, "Range": 0,
                                                                         "Size": 0, "Health": 0, "Shield": 0, "Evasion": 0, "Block": 0, "Resist": 0, "Speed": 0}})
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        await s.handle(mocked_socket, mock_path)
        mocked_socket.send.assert_called_with(expected)

    async def test_minimalist_join(self):
        json_request = json.dumps({"Message": "!join", "Username": "minimalist", "UserId": "101",
                                   "Email": "minimalist@sad.com", "Color": "FireBurn", "IsModerator": "False", "IsSubscriber": "False"})
        expected = json.dumps({"UserId": 101, "Name": "minimalist", "Skills": {"Melee": 0, "Mage": 0, "Range": 0,
                                                                               "Size": 0, "Health": 0, "Shield": 0, "Evasion": 0, "Block": 0, "Resist": 0, "Speed": 0}})
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        await s.handle(mocked_socket, mock_path)
        mocked_socket.send.assert_called_with(expected)

    async def test_riches_join(self):
        json_request = json.dumps({"Message": "!join", "Username": "riches", "UserId": "999",
                                   "Email": "riches@sad.com", "Color": "Gold", "IsModerator": "False", "IsSubscriber": "False"})
        expected = json.dumps({"UserId": 999, "Name": "riches", "Skills": {"Melee": 0, "Mage": 0, "Range": 0,
                                                                           "Size": 0, "Health": 0, "Shield": 0, "Evasion": 0, "Block": 0, "Resist": 0, "Speed": 0}})
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        await s.handle(mocked_socket, mock_path)
        mocked_socket.send.assert_called_with(expected)


class TestServerAction_gather(unittest.IsolatedAsyncioTestCase):
    # mock the user.inventorysize
    async def test_test_gather(self):
        mock_inventorysize = 100
        client_json = json.dumps({
            "Message": "!gather",
            "Username": "test"
        })
        for i in range(5):
            mocked_socket = AsyncMock(WebSocketServerProtocol)
            mock_path = MagicMock()
            s = Server()
            mocked_socket.recv.return_value = client_json
            await s.handle(mocked_socket, mock_path)
            expected_args = json.loads(mocked_socket.send.await_args.args[0])
            assert(True if ("UserId" in expected_args) else False)
            assert(True if ("Name" in expected_args) else False)
            assert(True if expected_args["Result"] else False)
            assert(True if ("Items" in expected_args) else False)


class TestServerAction_get_user_inventory(unittest.IsolatedAsyncioTestCase):
    async def test_test_inventory(self):
        json_request = json.dumps({
            "Message": "!inventory",
            "Username": "test"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)

        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        # even if inventory is empty, check for items key
        assert(True if ("Items" in expected_args) else False)


class TestServerAction_login(unittest.IsolatedAsyncioTestCase):
    async def test_test_login(self):
        json_request = json.dumps({
            "Message": "!login",
            "Username": "test",
            "Fortress": "test",
            "Alliance": "test"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["Result"] else False)
        assert(True if ("Name" in expected_args) else False)
        assert(True if ("Fortress" in expected_args) else False)
        assert(True if ("Alliance" in expected_args) else False)
        assert(True if ("Items" in expected_args) else False)


class TestServerAction_deposit(unittest.IsolatedAsyncioTestCase):
    async def test_test_deposit(self):
        json_request = json.dumps({
            "Message": "!deposit",
            "Username": "test",
            "Fortress": "test"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        print("ARGS : {}".format(mocked_socket.send.await_args.args[0]))
        print("ARGS : {}".format(mocked_socket.send.await_args.args[0]))
        print("ARGS : {}".format(mocked_socket.send.await_args.args[0]))
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["Result"] else False)
        assert(True if ("Fortress" in expected_args) else False)
        assert(True if ("Items" in expected_args) else False)
        assert(True if ("Value" in expected_args) else False)


'''
Three tests:
    1. User has enough money to buy the upgrade -> Result = True
    2. User does NOT have enough money to buy the upgrade -> Result = False
    3. User already owns the ship -> Result = True
'''


class TestServerAction_buy_ship(unittest.IsolatedAsyncioTestCase):
    async def test_test_ship(self):
        json_request = json.dumps({
            "Message": "!ship",
            "Username": "test",
            "Ship": "miner"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        assert(True if expected_args["Result"] else False)
        assert(True if expected_args["Ship"] else False)

    async def test_poor_ship(self):
        json_request = json.dumps({
            "Message": "!ship",
            "Username": "poor",
            "Ship": "miner"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        assert(True if expected_args["Result"] == False else False)
        assert(True if expected_args["Ship"] else False)

    async def test_riches_ship(self):
        json_request = json.dumps({
            "Message": "!ship",
            "Username": "riches",
            "Ship": "miner"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        # should be true, because riches already owns the ship
        assert(True if expected_args["Result"] else False)
        assert(True if expected_args["Ship"] else False)


'''
Two tests:
    1. User has enough money to buy the upgrade -> Result = True
    2. User does NOT have enough money to buy the upgrade -> Result = False
    3. User already owns the upgrade for that ship -> Result = True
'''


class TestServerAction_buy_upgrade(unittest.IsolatedAsyncioTestCase):
    async def test_test_upgrade(self):
        json_request = json.dumps({
            "Message": "!upgrade",
            "Username": "test",
            "Upgrade": "cargo",
            "Ship": "miner"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        assert(True if expected_args["Result"] else False)
        assert(True if expected_args["Ship"] else False)
        assert(True if expected_args["Upgrade"] else False)

    async def test_poor_upgrade(self):
        json_request = json.dumps({
            "Message": "!upgrade",
            "Username": "poor",
            "Upgrade": "cargo",
            "Ship": "miner"
        })
        mocked_socket = AsyncMock(WebSocketServerProtocol)
        mock_path = MagicMock()
        s = Server()
        mocked_socket.recv.return_value = json_request
        res = await s.handle(mocked_socket, mock_path)
        expected_args = json.loads(mocked_socket.send.await_args.args[0])
        assert(True if expected_args["UserId"] else False)
        assert(True if expected_args["Name"] else False)
        assert(True if expected_args["Result"] == False else False)
        assert(True if expected_args["Ship"] else False)
        assert(True if expected_args["Upgrade"] else False)


if __name__ == '__main__':
    unittest.main()
