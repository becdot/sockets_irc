# Things to worry about eventually
### 0. Need to be able to send multiple messages - like the client server needs to include a portion that runs code as 
### 1. How to implement usernames
### 2. How to deal with messages bigger than 1024 bytes?
### 3. How does select.select actually work?
### 4. Why do we have to check whether a message exists -- shouldn't it exist by default?
### 5. Implement checking whether a socket is writeable before we send it data
### 6. What happens when the timeout is set on socket.socket
### 7. Error handling
### 8. Making sure that messages get sent/received in order and in a timely fashion
### 9. Add usernames onto messages
### 10. Create client program for user use
### 11. Find a way to associate usernames with sockets
### 12. Error handling and/or default for no 3rd argument
### 13. Could add a dictionary call so that teh server does print username, user.getosockname() in the ' So & So says part'
### 14. Should we add a sys.exit("Some error messsage") for error cases

import socket
import select
import sys
import threading

server = socket.socket()
host = '127.0.0.1'
port = 1060
username_dict = {}

if sys.argv[1] == 'server':
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # What do these options mean?
    server.bind((host, port))
    server.listen(5)

    print "Listening on port", port

    read_list = [server]
    while True: # should we do while read_list and set a way to remove server from read_list when done?
        readable, writeable, errored = select.select(read_list, [], []) # Select takes in 3 communication channels: those checked for data to be read, those that will receive outgoing data when there is room in the buffer & those that may have an error (both input&output objects)
        for sock in readable:
            if sock is server: # The server has a new client waiting
                client, addr = server.accept() # Accept the new client
                read_list.append(client) # And add it to the list of clients
                print "Connection from :", addr # Do we need to setblocking(0) for client?
            else: # One of the readable sockets has data to transmit
                message = sock.recv(1024) # Says the problem is here - i.e. connection reset by peer
                if message:
                    print sock.getpeername(), "says", message
                    #Should we add writeable.append(sock)?? then remove from writeable before closing?
                    if message == 'exit':
                        print "About to close the socket on port", sock.getpeername()
                        sock.close() # what's the difference between switching the ordering between this and 
                        read_list.remove(sock) # this?
                    for client_sock in read_list[1:]:
                        client_sock.send(message)
# All sockets in readable have incoming data buffered & available to read. Errored has had an error (during execution of select.select())
""""
readable represents three possible cases: 
1. sock = server, server (which is being listened to for incoming connections) is ready to accept an incoming connection
2. established connection with a client who has sent data
3. A readable socket without data available (i.e. a client has disconnected (?) & stream is ready to be closed

writeable represents two cases:
1. there is data in the queue for a connection & the msg is sente
2. else, the connection is removed so that the next loop does not indicate the socket is ready to send data"""

# All sockets in writeable have free space in their buffer and can be written to

#Note: has the same error if connecting manually and then disconnect; doesn't after this bugfix
if sys.argv[1] == 'client':
    incoming = socket.socket()
    outgoing = socket.socket()
    incoming.connect((host, port))
    outgoing.connect((host, port))
    username = raw_input("Please enter your username: ")
    username_dict[username] = (incoming.getsockname(), outgoing.getsockname()) # Like this statement, gives the user a clear view of what's going on
    print "Your username is", username, "your incoming socket address is", incoming.getsockname(), \
        "and your outgoing socket address is", outgoing.getsockname()

    def send_message(sock):
        while True:
            message = raw_input('> ')
            sock.send(message)
            if message == 'exit':
                sock.shutdown(socket.SHUT_WR)
                break

    def receive_message(sock):
        while True:
            reply = sock.recv(1024)
            print reply

    outbox = threading.Thread(target=send_message, args=(outgoing,))
    outbox.start()
    inbox = threading.Thread(target=receive_message, args=(incoming,))
    inbox.start()



    # while True:
    #     message = raw_input('> ')   
    #     user.send(message) # This allows for multiple messages to happen, but they don't get sent out across everything - probably because there's no sock.recv
    #     if message == 'exit':
    #         user.shutdown(socket.SHUT_WR)
    #         break
    #     reply = user.recv(1024)
    #     print reply

        # """reading, writing, erroring = select.select([server], [],[])
        # print "Done selecting!"
        # for msg in reading: 
        #     ping = msg.recv(1024)
        #     if ping: 
        #         print ping"""

        



#Error no 54: Connection reset by peer





