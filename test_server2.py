import socket
import select
import sys
import threading

class Client:

    def __init__(self, host, port):
        self.user = raw_input("Please enter your username: ")
        self.incoming = socket.socket()
        self.outgoing = socket.socket()
        self.bothsockets = [self.incoming, self.outgoing]
        for s in self.bothsockets:
            s.connect((host, port))
        meta = 'user:{0},incoming:{1},outgoing:{2}'.format \
                            (self.user, self.incoming.getsockname()[1], self.outgoing.getsockname()[1])
        self.outgoing.send(meta)

    def receive_message(self, sock):
        "Receives messages from the server on the incoming socket"

        while True:
            reply = self.incoming.recv(1024)
            print reply

    def send_message(self, sock):
        "Sends messages to the server on the outgoing socket"

        while True:
            message = raw_input('> ')
            self.outgoing.send(message)
            if message == 'exit':
                self.outgoing.shutdown(socket.SHUT_WR)
                self.incoming.shutdown(socket.SHUT_RD)
                break

class Server:

    def __init__(self, host, port):
        self.passive = socket.socket()
        self.passive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # What do these options mean?
        self.passive.bind((host, port))
        self.passive.listen(5)
        print "Listening on port", port

        self.read_list = [self.passive]
        self.write_list = []
        self.errored = []
        self.readable, self.writeable, self.errored = select.select(self.read_list, self.write_list, self.errored)

        self.users = {} # {bec: {'incoming': sock1, 'outgoing': sock2}}

    def get_client_meta(self, sock):
        """ Adds username, socket type, and socket to self.users
            e.g. {username: {'incoming': socket1, 'outgoing': socket2 """

        raw_info = sock.recv(100)
        print 'we have received', raw_info
        if raw_info:
            info = raw_info.split(',')
            userpair = info[0].split(',')[0]
            user = userpair.split(':')[1]
            self.users[user] = {}
            for portpairs in info[1:]:
                port_type = portpairs.split(':')[0]
                self.users[user][port_type] = sock

    def type_of_port(self, sock):
        "Returns either 'outgoing' or 'incoming'"

        sock_port = int(sock.getpeername()[1])
        for user, dict in self.users.iteritems():
            for type, sock in dict.iteritems():
                print type, sock.getpeername()[1]
                # if sock_port == port and type == 'incoming':
                #     print sock, 'is an incoming socket'
                #     return 'incoming'
                # if sock_port == port and type == 'outgoing':
                #     print sock, 'is an outgoing socket'
                #     return 'outgoing'

    def sibling_sock(self, sock):
        "Returns the counterpart (outgoing) socket to a user's incoming socket, and visa versa"

        for user, dict in self.users.iteritems():
            for type, s in dict.iteritems():
                if s == sock and type == 'incoming':
                    return dict['outgoing']
                elif s == sock and type == 'outgoing':
                    return dict['incoming']

    def monitor(self):
        "Performs the main server function of checking for new connections and sending out messages"

        while True:
            for sock in self.readable:
                if sock is self.passive:
                    conn, addr = self.passive.accept()
                    print "Connection from :", addr # Do we need to setblocking(0) for client?
                    self.get_client_meta(conn)
                    print 'user dict', self.users

                    print self.type_of_port(conn)
                    # if self.type_of_port(conn) == 'incoming':
                    #     print 'socket is an incoming socket'
                    #     self.write_list.append(conn)
                    # elif self.type_of_port(conn) == 'outgoing':
                    #     print 'socket is an outgoing socket'
                    #     self.read_list.append(conn)

                else:
                    message = sock.recv(1024) 
                    if message:
                        print sock.getpeername(), "says", message
                        #Should we add writeable.append(sock)?? then remove from writeable before closing?
                        if message == 'exit':
                            print "About to close the sockets on port", sock.getpeername(), "and port", sibling_sock(sock).getpeername()
                            for s in [sock, sibling_sock(sock)]:
                                s.close() # what's the difference between switching the ordering between this and 
                                if s in read_list:
                                    print 'removed from read_list'
                                    read_list.remove(s) # this?
                                else:
                                    print 'removed from write_list'
                                    write_list.remove(s)

                        for incoming in write_list:
                            incoming.send(message)

host = '127.0.0.1'
port = 1060
if sys.argv[1] == 'server':
    server = Server(host, port)
    server.monitor()
if sys.argv[1] == 'client':
    client = Client(host, port)
    outbox = threading.Thread(target=client.send_message, args=(client.outgoing,))
    inbox = threading.Thread(target=client.receive_message, args=(client.incoming,))
    #outbox.start()
    #inbox.start()




# server = socket.socket()
# host = '127.0.0.1'
# port = 1060
# user_dict = {}

# if sys.argv[1] == 'server':
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # What do these options mean?
#     server.bind((host, port))
#     server.listen(5)

#     print "Listening on port", port

#     read_list = [server] # for the server and sockets carrying information FROM the client (outgoing)
#     write_list = [] # for sockets carrying information TO the client (incoming)
#     while True: # should we do while read_list and set a way to remove server from read_list when done?
#         readable, writeable, errored = select.select(read_list, write_list, []) 
#         for sock in readable:
#             if sock is server: # The server has a new client waiting
#                 client, addr = server.accept() 
#                 print "Connection from :", addr # Do we need to setblocking(0) for client?

#                 raw_info = client.recv(100)
#                 if raw_info:
#                     info = raw_info.split(',')
#                     userpair = info[0].split(',')[0]
#                     user = userpair.split(':')[1]
#                     user_dict[user] = {}
#                     for portpairs in info[1:]:
#                         key = portpairs.split(':')[0]
#                         value = int(portpairs.split(':')[1])
#                         user_dict[user][key] = value
#                     print user_dict


#                 # if msg == 'incoming':
#                 #     print client.getpeername(), "is an incoming socket and says", msg
#                 #     read_list.append(client) 
#                 # if msg == 'outgoing':
#                 #     print client.getpeername(), "is an outgoing socket and says", msg
#                 #     write_list.append(client)
#             else: # One of the readable sockets has data to transmit
#                 print 'we are getting here?'
#                 message = sock.recv(1024) 
#                 if message:
#                     print sock.getpeername(), "says", message
#                     #Should we add writeable.append(sock)?? then remove from writeable before closing?
#                     if message == 'exit':
#                         print "About to close the socket on port", sock.getpeername()
#                         sock.close() # what's the difference between switching the ordering between this and 
#                         read_list.remove(sock) # this?
#                     for client_sock in read_list[1:]:
#                         client_sock.send(message)






# if sys.argv[1] == 'client':
#     client = Client(host, port)




    # incoming, outgoing = socket.socket(), socket.socket()
    # incoming.connect((host, port))
    # outgoing.connect((host, port))
    # username = raw_input("Please enter your username: ")
    # username_dict[incoming] = username 
    # username_dict[outgoing] = username 
    # print "Your username is", username, "your incoming socket address is", incoming.getsockname(), \
    #     "and your outgoing socket address is", outgoing.getsockname()

    # def send_message(sock):
    #     while True:
    #         message = raw_input('> ')
    #         sock.send(message)
    #         if message == 'exit':
    #             sock.shutdown(socket.SHUT_WR)
    #             break

    # def receive_message(sock):
    #     while True:
    #         reply = sock.recv(1024)
    #         print reply

    # outbox = threading.Thread(target=send_message, args=(outgoing,))
    # outbox.start()
    # inbox = threading.Thread(target=receive_message, args=(incoming,))
    # inbox.start()