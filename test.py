import unittest
from test_server2 import Client, Server

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


if __name__ == '__main__':
    unittest.main()