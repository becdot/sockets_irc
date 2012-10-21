import unittest
from test_server2 import Client, Server

class FakeSocket():
    did_message_send = False
    def send(self, message):
        self.did_message_send = True

    message = ""
    def recv(self, bytes):
        if len(self.message[:bytes]) == len(self.message):
            return True
        return False

    shut = False
    def shutdown(self, type):
        self.shut = True




class TestSequenceFunctions(unittest.TestCase):

    def test_client_with_defaults(self):
        "When host and port aren't provided for the Client class, defaults are used instead"
        client = Client()
        self.assertEquals(client.host, '127.0.0.1')
        self.assertEquals(client.port, 1060)

    def test_server_with_defaults(self):
        "When host and port aren't provided form the Server class, defaults are used instead"
        server = Server()
        self.assertEquals(server.host, '127.0.0.1')
        self.assertEquals(server.port, 1060)

    def test_client_with_entries(self):
        "When host and port are provided for the Client class, correct values are used"
        client = Client(host='0.0.0.1', port=1061)
        self.assertEquals(client.host, '0.0.0.1')
        self.assertEquals(client.port, 1061)

    def test_server_with_entries(self):
        "When host and port are provided for the Server class, correct values are used"
        server = Server(host='0.0.0.1', port=1061)
        self.assertEquals(server.host, '0.0.0.1')
        self.assertEquals(server.port, 1061)

    def test_send_to_others(self):
        "Message is sent to all connected clients except the original sender through the incoming sockets"
        fakesock1 = FakeSocket()
        fakesock2 = FakeSocket()
        fakesock3 = FakeSocket()
        fakesock4 = FakeSocket()
        fakedict = {'bec': {'incoming': fakesock1, 'outgoing': fakesock2}, 'jess': {'incoming': fakesock3, 'outgoing': fakesock4}}
        server = Server()
        server.users = fakedict
        server.send_to_others([fakesock1, fakesock3], fakesock2, 'hello!')
        self.assertFalse(fakesock1.did_message_send)
        self.assertTrue(fakesock3.did_message_send)

    def test_receive_message(self):
        "Message received is the same length as the message sent"
        client = Client()
        fakeincoming = FakeSocket()
        fakeincoming.message = "hello!"
        client.incoming = fakeincoming
        self.assertTrue(client.receive_message())

    def test_send_message(self):
        "Message is sent from the client to the server and sets threads = True"
        client = Client()
        fakesock = FakeSocket()
        client.outgoing = fakesock
        client.send_message('hello!')
        self.assertTrue(fakesock.did_message_send)
        self.assertTrue(client.threads)

    def test_send_exit(self):
        "An exit message sent from the client shuts down the socket and sets threads = False"
        client = Client()
        fakesock = FakeSocket()
        client.outgoing = fakesock
        client.send_message('exit')
        self.assertTrue(fakesock.shut)
        self.assertFalse(client.threads)

    def test_get_client_meta_not_in_dict(self):
        "Client metadata is processed appropriately when the user is not already in the users dictionary"
        fakesock = FakeSocket()
        user_meta = 'user:bec,type:incoming'
        server = Server()
        server.users = {}
        server.parse_client_meta(user_meta, fakesock)
        self.assertEquals(str(server.users), "{'bec': {'incoming': %s}}" % (fakesock))

    def test_get_client_meta_in_dict(self):
        "Client metadata is processed appropriately when the user is already in the users dictionary"
        fakeincoming = FakeSocket()
        fakeoutgoing = FakeSocket()
        user_meta = 'user:bec,type:outgoing'
        server = Server()
        server.users = {'bec': {'incoming': fakeincoming}}
        server.parse_client_meta(user_meta, fakeoutgoing)
        self.assertEquals(str(server.users), "{'bec': {'outgoing': %s, 'incoming': %s}}" % (fakeoutgoing, fakeincoming))

    def test_type_of_port(self):
        "Type of port returns correctly"
        fakeincoming = FakeSocket()
        fakeoutgoing = FakeSocket()
        server = Server()
        server.users = {'bec': {'incoming': fakeincoming, 'outgoing': fakeoutgoing}}
        sock_type_in = server.type_of_port(fakeincoming)
        sock_type_out = server.type_of_port(fakeoutgoing)
        self.assertEquals(sock_type_in, 'incoming')
        self.assertEquals(sock_type_out, 'outgoing')

    def test_sibling_sock(self):
        "Returns the correct sibling socket"
        fakeincoming = FakeSocket()
        fakeoutgoing = FakeSocket()
        server = Server()
        server.users = {'bec': {'incoming': fakeincoming, 'outgoing': fakeoutgoing}}
        sibling_in = server.sibling_sock(fakeincoming)
        sibling_out = server.sibling_sock(fakeoutgoing)
        self.assertEquals(sibling_in, fakeoutgoing)
        self.assertEquals(sibling_out, fakeincoming)

    def test_get_user(self):
        "Returns the correct user for a given socket"
        fakesock1 = FakeSocket()
        fakesock2 = FakeSocket()
        fakesock3 = FakeSocket()
        fakesock4 = FakeSocket()
        server = Server()
        server.users = {'bec': {'incoming': fakesock1, 'outgoing': fakesock2}, 'jess': {'incoming': fakesock3, 'outgoing': fakesock4}}
        user1 = server.get_user(fakesock1)
        user2 = server.get_user(fakesock4)
        self.assertEquals(user1, 'bec')
        self.assertEquals(user2, 'jess')







if __name__ == '__main__':
    unittest.main()