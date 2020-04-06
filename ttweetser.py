import sys
import json
from socket import *
import _thread

class Server:
    def __init__(self):
        self.hashtags = {}
        self.clients = {}
        self.tweets = {}
        self.message = None
        self.server_socket = None
        self.connection_socket = None

    def create_connection(self, server_port):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(('127.0.0.1', server_port))
            self.server_socket.listen(5)
            print("The server is ready to receive at {}".format(server_port))
        except (error, OverflowError) as e:
            print("Caught exception {}".format(e))
            sys.exit(1)

    def is_port_valid(self, server_port):
        if server_port < 13000 or server_port > 14000:
            print("The port number is invalid, the range of port numbers is 13000 to 14000")
            sys.exit()

    def execute_request(self, command_input, conn):
        try:
            if command_input:
                command_input = command_input.decode("utf-8")
                command, *args = command_input.split(' ')
                print(command)
                print(args)
                if command == '$getusers':
                    self.get_users(conn)
                elif command == '$checkusername' and len(args) == 1:
                    self.is_user_logged_in(args[0], conn)
                elif command == '$gettweets' and len(args) == 1:
                    self.get_tweets(args[0], conn)
                elif command == '$exit' and len(args) == 1:
                    self.exit(args[0])
                elif command == '$subscribe' and len(args) == 2:
                    self.subscribe(args[0], args[1], conn)
                elif command == '$unsubscribe':
                    self.unsubscribe(args[0], args[1], conn)
                elif command == '$tweet':
                    message = " ".join(args[2:])
                    print(message)
                    self.tweet([args[0], args[1], message])
        except Exception as e:
            print('Errors executing request {}'.format(e))

    def is_user_logged_in(self, username, connection):
        try:
            if not self.clients.get(username): #username is not in the system
                # add the new client to the client list
                self.clients.update({username: connection})
                not_logged_in = 0
                connection.send(bytes(str(not_logged_in), 'utf8'))
                print(f'Connected to {username}')
            else:
                logged_in = 1
                connection.send(bytes(str(logged_in), 'utf8'))
        except Exception as e:
            print(f"Errors trying to check username in the system: {e}")

    def get_users(self, connection):
        try:
            all_clients = {'clients': list(self.clients.keys())}
            all_client_json = json.dumps(all_clients)
            connection.send(all_client_json.encode('utf-8'))
            print("Sent all users to client successully")
        except Exception as e:
            print(f"Errors trying to send all users: {e}")

    def get_tweets(self, username, connection):
        tweets = self.tweet.get(username)
        formated_tweets = []
        if not tweets:
            formated_tweets.append(f'no user {username} in the system')
        else:
            for tweet in tweets:
                formated_tweets.append(f'{username}: \"{tweet[0]}\" {tweet[1]}')
        try:
            connection.send(json.dumps(formated_tweets).encode('utf-8'))
            message = 'Done'
            connection.send(message.encode('utf-8'))
            print(f"Sent all tweets from {username} successfully")
        except Exception as e:
            print(f'Error getting tweets: {e}')

    def exit(self, username):
        print('exit')


    # broadcast to all users that subscribe to the hashtag
    def broadcast_message(self, message, hashtags):
        hashtag_list = ['#' + hashtag for hashtag in hashtags.split('#') if hashtag]

        '''
        Broadcast the message to all subscriber that subscribes to #ALL
        and deduplication on the subscribed messages.
        Ex: a client A subscribes to #ALL and #1.
        Another client B run 'tweet "message" #1'
        => A should only output this message once
        '''

        for hashtag in hashtag_list:
            # get all subscriber that subscribed to #ALL
            subscribers_to_ALL = self.hashtags.get('#ALL') if self.hashtags.get('#ALL') else set()
            # get all subscribers that subscribed to the hashtag
            cur_hashtag_subs = self.hashtags.get(hashtag) if self.hashtags.get(hashtag) else set()
            subscribers = cur_hashtag_subs.union(x for x in subscribers_to_ALL if x not in cur_hashtag_subs)
            if subscribers:
                for subscriber_username in subscribers:
                    client_connection = self.clients.get(subscriber_username)
                    if client_connection:
                        try:
                            client_connection.send(message.encode('utf-8'))
                            print('Message is sent to ' + subscriber_username)
                        except Exception as e:
                            print(f'Errors trying to broadcast message to subscribers {e}')


    def tweet(self, command):
        print("tweet")
        username = command[0]
        hashtags = command[1]
        message = command[2]
        try:
            prev_tweets = self.tweets.get(username)
            if prev_tweets:
                # if user has tweeted before, append to the list
                prev_tweets.append([message, hashtags])
                self.tweets.update({username: prev_tweets})
            else:
                self.tweets.update({username: [[message, hashtags]]})
            print('before broadcasting')
            self.broadcast_message(message, hashtags)
            print('{} tweeted successfully'.format(username))
        except Exception as e:
            print('Errors trying to tweet {}: {}'.format(message, e))

    def subscribe(self, username, hashtag, connection):
        subscribers = self.hashtags.get(hashtag)
        if subscribers:
            subscribers.add(username)
            self.hashtags.update({hashtag: subscribers})
        else:
            self.hashtags.update({hashtag: {username}})
        try:
            success = "1"
            connection.send(success.encode('utf-8'))
            print('{} subscribed to {} successfully'.format(username, hashtag))
        except Exception as e:
            print(f'{username} failed to subscribe to {hashtag}')
            

    def unsubscribe(self, username, hashtag, connection):
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
                print('Got errors starting new client: {}'.format(err))

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
            print("Caught exception {}".format(er))
            sys.exit()

        while 1:
            try:
                self.connection_socket, addr = self.server_socket.accept()
                print("Connection from port#: " + str(addr[1]))

                # connect to a new client
                _thread.start_new_thread(self.start_new_client, (self.connection_socket,))
            except (Exception) as e:
                print("Error receiving new client ".format(e))
                break
        self.connection_socket.close()

server = Server()
server.run_server()