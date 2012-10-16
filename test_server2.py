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


import socket
import select
import sys

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
    while True:
        readable, writeable, errored = select.select(read_list, [], [])
        for sock in readable:
            if sock is server: # The server has a new client waiting
                client, addr = server.accept() # Accept the new client
                read_list.append(client) # And add it to the list of clients
                print "Connection from :", addr
            else: # One of the sockets has data to transmit
                message = sock.recv(1024) # Says the problem is here - i.e. connection reset by peer
                if message:
                    print sock.getpeername(), "says", message
                    if message == 'exit':
                        print "About to close the socket on port", sock.getpeername()
                        sock.close()
                        read_list.remove(sock)
                    for client_sock in read_list[1:]:
                        client_sock.send(message)
#Note: has the same error if connecting manually and then disconnect; doesn't after this bugfix
elif sys.argv[1] == 'client':
    user = socket.socket()
    user.connect((host, port))
    username = raw_input("Please enter your username: ")
    user.send("Hey, I'm here")
    username_dict[username] = user.getsockname() # Like this statement, gives the user a clear view of what's going on
    print username, user.getsockname()
    message = raw_input("Please send your first message: ")
    user.send(message) # This allows for multiple messages to happen, but they don't get sent out across everything - probably because there's no sock.recv

#Error no 54: Connection reset by peer





