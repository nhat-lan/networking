import sys
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

    def check_port_validation(self, server_port):
        if server_port < 13000 or server_port > 14000:
            print("The port number is invalid, the range of port numbers is 13000 to 14000")
            sys.exit()

    def execute_command(self, command, conn):
        if command:
            command = command.split(' ')
            if len(command) == 1 and command[0] == 'getusers':
                self.get_users()
            elif len(command) == 2:
                username = command[1]
                if command[0] == 'check_username':
                    self.check_username(username, conn)
                elif command[0] == 'timeline':
                    self.get_timeline(username)
                elif command[0] == 'gettweets':
                    self.get_tweets(username)
                elif command[0] == 'exit':
                    self.exit(username)
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

    def check_username(self, username, conn):
        if not self.clients.get(username): #username is not in the system
            # add the new client to the client list
            self.clients.update(
                {
                    username: {
                        'connection': conn,
                        'message_received': [],
                        'subscribed_to': set()
                    }
                }
            )
            conn.send('Username is valid')
        else:
            conn.send('Username is taken')

    def get_timeline(self, username):
        print('get_timeline')

    def get_users(self):
        self.connection_socket.send("ALL USERS GO IN HERE")

    def get_tweets(self, username):
        print('get_tweets')

    def exit(self, username):
        print('exit')


    # broadcast to all users that subscribe to the hashtag
    def broadcast_message(self, message, hashtag):
        # get all subscribers that subscribed to the hashtag
        subscribers = self.hashtags.get(hashtag)
        print('hash', self.hashtags)
        if subscribers:
            print('sub', subscribers)
            for subscriber_username in subscribers:
                client = users.get(subscriber_username)
                print('client', client)
                if client:
                    # obtain the client's connection to send message to them
                    subcriber_connection = client.get('connection')
                    subcriber_connection.send(message)
                    print('Broadcast message ', message)

    '''
    tweet <username> <hashtag> <message>
    Response:
        Uploaded tweet successfully
        Failed to tweet
    '''
    def tweet(self, command):
        username = command[1]
        hashtags = command[2]
        message = command[3]
        self.broadcast_message(message, hashtags)

        print('User ', username, 'tweeted successfully')


    def subscribe(self, username, hashtag):
        try:
            user_data = self.clients.get(username)
            if (user_data): # if username existed in the system
                subscribed_to = user_data.get('subscribed_to')
                subscribed_to.update(hashtag)
                print(username + " subcribed to " + hashtags + " succesfully")
                print(self.clients)

            if self.hashtags.get(hashtag): #
                self.hashtags.update({'hashtag': [username]})
        except:
            print('Errors trying to subscribe to ', hashtags)



    def unsubscribe(self, username, hashtag):
        print('unsubcribe')

    def start_new_client(self, conn):
        while 1:
            try:
                command = conn.recv(1024)
                self.execute_command(command, conn)
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
            self.check_port_validation(server_port)
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