import sys
import json
from socket import *
import thread
    
class Server:
    def __init__(self):
        self.hashtags = {}
        self.clients = {}
        
        self.message = None
        self.server_socket = None
        self.connection_socket = None

    def create_connection(self, server_port):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(('127.0.0.1', server_port))
            self.server_socket.listen(5)
            print("The server is ready to receive at {0}".format(server_port))
        except (error, OverflowError) as e:
            print("Caught exception {0}".format(e))
            sys.exit(1)

    def is_port_valid(self, server_port):
        if server_port < 13000 or server_port > 14000:
            print("The port number is invalid, the range of port numbers is 13000 to 14000")
            sys.exit()

    def execute_request(self, command, conn):
        if command:
            command = command.split(' ')
            if len(command) == 2:
                username = command[1]
                if command[0] == 'check_username':
                    self.is_username_valid(username, conn)
                elif command[0] == 'gettweets':
                    self.get_tweets(username)
                elif command[0] == 'exit':
                    self.exit(username)
                elif command[0] == 'getusers':
                    self.get_users(conn) 
            elif len(command) == 3:
                username = command[1]
                hashtag = command[2]
                if command[0] == 'subscribe':
                    self.subscribe(username, hashtag)
                else:
                    self.unsubscribe(username, hashtag)
            elif len(command) == 4:
                if command[0] == 'tweet':
                    self.tweet(command)
        else:
            print(command, 'Command is invalid')

    def is_username_valid(self, username, client_connection):
        if not self.clients.get(username): #username is not in the system
            # add the new client to the client list
            self.clients.update({username: client_connection})
            connection.send('Username is valid')
        else:
            connection.send('Username is taken')

    def get_users(self, connection):
        connection = self.clients.get(username)
        try:
            all_clients = self.clients.keys()
            all_client_json = json.dumps(all_clients)
            connection.send(all_client_json) 
            print("Sent all users to {username} successully".format(username))
        except:
            print("Errors trying to send all users to {username}".format(username))
 
    def get_tweets(self, username):
        print('get_tweets')

    def exit(self, username):
        print('exit')
    

    # broadcast to all users that subscribe to the hashtag
    def broadcast_message(self, message, hashtags):
        hashtag_list = ['#' + hashtag for hashtag in hashtags.split('#') if hashtag] 
        for hashtag in hashtag_list:
            '''
            Broadcast the message to all subscriber that subscribes to #ALL
            and deduplication on the subscribed messages.
            Ex: a client A subscribes to #ALL and #1. 
            Another client B run 'tweet "message" #1'
            => A should only output this message once
            '''
            # get all subscriber that subscribed to #ALL
            subscribers_to_ALL = self.hashtags.get('#ALL')
            
            # get all subscribers that subscribed to the hashtag
            cur_hashtag_subs = self.hashtags.get(hashtag)
            
            subscribers = list(subscribers_to_ALL | cur_hashtag_subs)
            
            if subscribers:
                for subscriber_username in subscribers:
                    client_connection = self.clients.get(subscriber_username)
                    if client_connection:
                        client_connection.send(message)
                        print('Message is sent to ' + subscriber_username)


    def tweet(self, command):
        username = command[1]
        hashtags = command[2]
        message = command[3]
        self.broadcast_message(message, hashtags)
        print(username + ' tweeted successfully')


    def subscribe(self, username, hashtag):
        subscribers = self.hashtags.get(hashtag)
        if subscribers:
            subscribers.add(username)
            self.hashtags.update({hashtag: subscribers})
        else:
            self.hashtags.update({hashtag: {username}})

        print('{} subscribed to {} successfully'.format(username, hashtag))

    def unsubscribe(self, username, hashtag):
        subscribers = self.hashtags.get(hashtag)
        if subscribers:
            subscribers.remove(username) if username in subscribers else None
        print('{} unsubscribed from {} successfully'.format(username, hashtag))

    def start_new_client(self, conn):
        while 1:
            try: 
                command = conn.recv(1024)
                self.execute_request(command, conn)
                if not command:
                    break
            except (Exception) as err:
                print('Got errors starting new client', err)

        conn.close()

    def run_server(self):

        # check if input from comand line is valid
        args = sys.argv
        if len(args) < 2:
            print("Server: there are argument problems, please try to input the arguments as following:")
            print("python ttweetser.py <ServerPort>")
            sys.exit()
        try:
            # create the server connection
            server_port = int(args[1])
            self.is_port_valid(server_port)
            self.create_connection(server_port)
        except (ValueError, OverflowError) as er:
            print("Caught exception {0}".format(er))
            sys.exit()

        while 1:
            try:
                self.connection_socket, addr = self.server_socket.accept()
                print("Connection from port#: " + str(addr[1]))

                # connect to a new client
                thread.start_new_thread(self.start_new_client, (self.connection_socket,))
            except (Exception) as e:
                print("Error receiving new client", e)
                break
        self.connection_socket.close()

server = Server()
server.run_server()