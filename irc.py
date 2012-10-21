"""
To do:
  - Improve message printing so that partially-typed messages don't get cut off -- NOT DONE
  - Add usernames to messages to indicate who is talking -- PARTIALLY DONE
  - Make sure that exit command works (and threads don't continue to run) -- DONE
  - Exit the server loop when there are no more connected sockets  -- DONE
  - Add 'user exited' message when self/other clients disconnect  -- DONE
  - Implement a receive_all function so that server and client can receive more than 1024 byes of data -- NOT DONE
"""


import socket
import select
import sys
import threading

class Client:

    def __init__(self, host='127.0.0.1', port=1060):
        self.host = host
        self.port = port
        self.threads = True

    def setup(self):
        self.user = raw_input("Please enter your username: ")
        for type in ['incoming', 'outgoing']:
            setattr(self, type, socket.socket())
            getattr(self, type).connect((self.host, self.port))
            getattr(self, type).send('user:{0},type:{1}'.format(self.user, type))

    def receive_message(self):
        "Receives messages from the server on the incoming socket"

        return self.incoming.recv(1024)

    def get_message_from_user(self):
        "Returns raw input message from user"

        return raw_input('{0}: '.format(self.user))

    def send_message(self, message):
        "Sends messages to the server on the outgoing socket"

        self.outgoing.send(message)
        if message == 'exit':
            self.outgoing.shutdown(socket.SHUT_WR)
            self.threads = False

    def start_sending(self):
        "Starts main loop of sending messages"

        while self.threads:
            self.send_message(self.get_message_from_user())

    def start_receiving(self):
        "Starts main loop of receiving messages"

        while self.threads:
            print self.receive_message()

class Server:

    def __init__(self, host='127.0.0.1', port=1060):
        self.host = host
        self.port = port
        # {bec: {'incoming': sock1, 'outgoing': sock2}}
        self.users = {}

    def setup(self):
        self.passive = socket.socket()
        self.passive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.passive.bind((host, port))
        self.passive.listen(5)
        print "Listening on port", port

        self.read_list = [self.passive]
        self.write_list = []
        self.errored = []

    def get_client_meta(self, sock):
        "Returns the socket and user metadata received from the initial socket connection"

        raw_info = sock.recv(100)
        assert raw_info, "No message received"
        return raw_info

    def parse_client_meta(self, user_info, sock):
        """ Adds username, socket type, and socket to self.users
        e.g. {username: {'incoming': socket1, 'outgoing': socket2 """

        info = user_info.split(',')
        user = info[0].split(':')[1]
        type = info[1].split(':')[1]
        if user not in self.users:
            self.users[user] = {type: sock}
        else:
            self.users[user][type] = sock

    def type_of_port(self, sock):
        "Returns either 'outgoing' or 'incoming'"

        for user, dic in self.users.iteritems():
            for type, socket in dic.iteritems():
                if sock == socket:
                    return type
                assert "The socket was not found in the dictionary"


    def sibling_sock(self, sock):
        "Returns the counterpart (outgoing) socket to a user's incoming socket, and visa versa"

        for user, dict in self.users.iteritems():
            for type, s in dict.iteritems():
                if s == sock and type == 'incoming':
                    return dict['outgoing']
                elif s == sock and type == 'outgoing':
                    return dict['incoming']

    def get_user(self, sock):
        "Returns the user associated with the socket"

        for user, dic in self.users.iteritems():
            for type, socket in dic.iteritems():
                if sock == socket:
                    return user


    def send_to_others(self, socks_to_write_to, sock, message):
        "Sends a message to all other connected clients except for the originating client"

        user = self.get_user(sock)
        incoming = self.sibling_sock(sock)
        assert incoming in socks_to_write_to, "The socket is not in the list of sockets sending data to the client"
        socks_to_write_to.remove(incoming)
        for s in socks_to_write_to:
            if message == 'exit':
                s.send("{0} has exited".format(user))
            else:
                s.send("{0}: {1}".format(self.get_user(sock), message))

    def monitor(self):
        "Performs the main server functions of checking for new connections and sending out messages to clients"

        while True:
            readable, writeable, errored = select.select(self.read_list, self.write_list, self.errored, 120)   
            for sock in readable:
                if sock is self.passive: # A new connection is waiting to be made
                    conn, addr = self.passive.accept()
                    print "Connection from :", addr 
                    user_info = self.get_client_meta(conn)
                    self.parse_client_meta(user_info, conn)
                    print 'user dict', self.users

                    if self.type_of_port(conn) == 'incoming':
                        self.write_list.append(conn)
                    elif self.type_of_port(conn) == 'outgoing':
                        self.read_list.append(conn)

                else:
                    message = sock.recv(1024) 
                    if message:
                        print sock.getpeername(), "says", message
                        if message == 'exit':
                            print "About to close the sockets on port", sock.getpeername(), "and port", self.sibling_sock(sock).getpeername()
                            for s in [sock, self.sibling_sock(sock)]:
                                s.close() 
                                if s in self.read_list:
                                    print s, 'removed from read_list'
                                    self.read_list.remove(s) 
                                else:
                                    print s, 'removed from write_list'
                                    self.write_list.remove(s)
                            if len(self.read_list) == 1 or len(self.write_list) == 0:
                                sys.exit()
                        self.send_to_others(writeable, sock, message)
                        if len(self.read_list) == 1 or len(self.write_list) == 0:
                            sys.exit()


### Run the program!
if __name__ == '__main__':
    host = '127.0.0.1'
    port = 1060
    if sys.argv[1] == 'server':
        server = Server(host, port)
        server.setup()
        server.monitor()
    if sys.argv[1] == 'client':
        client = Client(host, port)
        client.setup()
        outbox = threading.Thread(target=client.start_sending)
        inbox = threading.Thread(target=client.start_receiving)
        outbox.start()
        inbox.start()