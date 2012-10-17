import socket
import select
import sys
import threading

class Client:

    def __init__(self, host, port):
        self.user = raw_input("Please enter your username: ")
        self.incoming, self.outgoing = socket.socket(), socket.socket()
        self.allsockets = [self.incoming, self.outgoing]
        for s in self.allsockets:
            s.connect((host, port))
        self.outgoing.send('user:{0},incoming:{1},outgoing:{2}'.format
                            (self.user, self.incoming.getsockname()[1], self.outgoing.getsockname()[1]))


    def receive_message(self, sock):
        while True:
            reply = self.sock.recv(1024)
            print reply
    def send_message(self, sock):
        while True:
            message = raw_input('> ')
            self.sock.send(message)
            if message == 'exit':
                self.sock.shutdown(socket.SHUT_WR)
                break



server = socket.socket()
host = '127.0.0.1'
port = 1060
user_dict = {}

if sys.argv[1] == 'server':
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # What do these options mean?
    server.bind((host, port))
    server.listen(5)

    print "Listening on port", port

    read_list = [server] # for the server and sockets carrying information FROM the client (outgoing)
    write_list = [] # for sockets carrying information TO the client (incoming)
    while True: # should we do while read_list and set a way to remove server from read_list when done?
        readable, writeable, errored = select.select(read_list, write_list, []) 
        for sock in readable:
            if sock is server: # The server has a new client waiting
                client, addr = server.accept() 
                print "Connection from :", addr # Do we need to setblocking(0) for client?
                raw_info = client.recv(100)
                if raw_info:
                    info = raw_info.split(',')
                    userpair = info[0].split(',')[0]
                    user = userpair.split(':')[1]
                    user_dict[user] = {}
                    for portpairs in info[1:]:
                        key = portpairs.split(':')[0]
                        value = int(portpairs.split(':')[1])
                        user_dict[user][key] = value
                    print user_dict

                # print userpair[1]
                # user = userpair[1]
                # print user
                # print 'user', user
                # user_dict[user] = {}
                # for ports in info[1:].split(','):
                #     user_dict[key][ports[0].split(':')] = int(ports[1].split(':'))
                # print user_dict

                # if msg == 'incoming':
                #     print client.getpeername(), "is an incoming socket and says", msg
                #     read_list.append(client) 
                # if msg == 'outgoing':
                #     print client.getpeername(), "is an outgoing socket and says", msg
                #     write_list.append(client)
            else: # One of the readable sockets has data to transmit
                print 'we are getting here?'
                message = sock.recv(1024) 
                if message:
                    print sock.getpeername(), "says", message
                    #Should we add writeable.append(sock)?? then remove from writeable before closing?
                    if message == 'exit':
                        print "About to close the socket on port", sock.getpeername()
                        sock.close() # what's the difference between switching the ordering between this and 
                        read_list.remove(sock) # this?
                    for client_sock in read_list[1:]:
                        client_sock.send(message)






if sys.argv[1] == 'client':
    client = Client(host, port)




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