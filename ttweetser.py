import sys
import json
from socket import *
import threading


class Server:
    def __init__(self):
        self.hashtags = {}
        self.clients = {}
        self.tweets = {}
        self.server_socket = None

    def add_new_user(self, username, connection):
        self.clients.update({username: connection})
        self.tweets.update({username: []})

    def send_message(self, message, connection):
        connection.sendall(message.encode('utf-8'))

    def create_connection(self, server_port):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(('127.0.0.1', server_port))
            self.server_socket.listen(5)
            print("The server is ready to receive at {}".format(server_port))
        except (error, OverflowError) as e:
            print("Caught exception {}".format(e))
            sys.exit(1)

    def execute_request(self, command_input, conn):
        try:
            if command_input:
                command_input = command_input.decode("utf-8")
                command, *args = command_input.split(' ')
                if command == '$getusers':
                    self.get_users(conn)
                elif command == '$signin' and len(args) == 1:
                    self.sign_in(args[0], conn)
                elif command == '$gettweets' and len(args) == 1:
                    self.get_tweets(args[0], conn)
                elif command == '$exit' and len(args) == 1:
                    self.client_exit(args[0])
                elif command == '$subscribe' and len(args) == 2:
                    self.subscribe(args[0], args[1], conn)
                elif command == '$unsubscribe':
                    self.unsubscribe(args[0], args[1], conn)
                elif command == '$tweet':
                    message = " ".join(args[2:])
                    self.tweet([args[0], args[1], message])
        except Exception as e:
            print('Errors executing request {}'.format(e))

    def sign_in(self, username, connection):
        is_signed_in = 0
        try:
            if not self.clients.get(username):  # username is not in the system
                # add the new client to the client list
                self.add_new_user(username, connection)
                is_signed_in = 1
                print(f'Connected to {username}')

            self.send_message(f'{is_signed_in}', connection)
        except Exception as e:
            print(f"Errors trying to check username in the system: {e}")

    def get_users(self, connection):
        try:
            all_clients = list(self.clients.keys())
            all_client_json = json.dumps(all_clients)
            self.send_message(all_client_json, connection)
            print("Sent all users to client successfully")
        except Exception as e:
            print(f"Errors trying to send all users: {e}")

    def get_tweets(self, username, connection):

        formated_tweets = []
        if username not in self.clients:
            formated_tweets.append(f'no user {username} in the system')
        else:
            tweets = self.tweets.get(username)
            for tweet in tweets:
                formated_tweets.append(
                    f'{username}: \"{tweet[0]}\" {tweet[1]}')
        try:
            self.send_message(json.dumps(formated_tweets), connection)
            self.send_message('Done', connection)
            print(f"Sent all tweets from {username} successfully")
        except Exception as e:
            print(f'Error getting tweets: {e}')

    def client_exit(self, username):
        print(f'{username} exit')
        if self.clients and username in self.clients:
            del self.clients[username]
        if self.tweets and username in self.tweets:
            del self.tweets[username]
        if self.hashtags:
            for hashtag, subscribers in self.hashtags.items():
                if username in subscribers:
                    subscribers.remove(username)

    def broadcast_message(self, message, hashtags):
        hashtag_set = set([
            '#' + hashtag for hashtag in hashtags.split('#') if ('#'+hashtag) in self.hashtags])

        '''
        Broadcast the message to all subscriber that subscribes to #ALL
        and deduplication on the subscribed messages.
        Ex: a client A subscribes to #ALL and #1.
        Another client B run 'tweet "message" #1'
        => A should only output this message once
        '''

        # get all subscriber that subscribed to #ALL
        if '#ALL' in self.hashtags:
            hashtag_set.add('#ALL')

        subscribers = set()
        for hashtag in hashtag_set:
            if hashtag in self.hashtags:
                subscribers = subscribers.union(self.hashtags.get(hashtag))

        for subscriber in subscribers:
            connection = self.clients.get(subscriber)
            if connection:
                try:
                    self.send_message(message, connection)
                    print(f'Message {message} is sent to {subscriber}')
                except Exception as e:
                    print(
                        f'Errors trying to broadcast message to subscribers {e}')

    def tweet(self, command):
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

            self.broadcast_message(
                f'{username}: \"{message}\" {hashtags}', hashtags)
            print('{} tweeted successfully'.format(username))
        except Exception as e:
            print('Errors trying to tweet {}: {}'.format(message, e))

    def subscribe(self, username, hashtag, connection):
        subscribers = self.hashtags.get(
            hashtag) if hashtag in self.hashtags else set()
        subscribers.add(username)
        self.hashtags.update({hashtag: subscribers})

        print('{} subscribed to {} successfully'.format(username, hashtag))

    def unsubscribe(self, username, hashtag, connection):
        hashtags_set = self.hashtags.keys(
        ) if hashtag == '#ALL' else set([hashtag])

        for _hashtag in hashtags_set:
            subscribers = self.hashtags.get(_hashtag)

            if subscribers and username in subscribers:
                subscribers.remove(username)

        print('{} unsubscribed from {} successfully'.format(username, hashtag))

    def start_new_client(self, conn):
        while 1:
            try:
                command = conn.recv(1024)
                if not command:
                    break
                self.execute_request(command, conn)

            except (Exception) as err:
                print('Got errors starting new client: {}'.format(err))

        conn.close()

    def run_server(self):

        # check if input from comand line is valid
        args = sys.argv
        if len(args) < 2:
            print(
                "Server: there are argument problems, please try to input the arguments as following:")
            print("python ttweetser.py <ServerPort>")
            sys.exit()
        try:
            # create the server connection
            server_port = int(args[1])
            self.create_connection(server_port)
        except (ValueError, OverflowError) as er:
            print("Caught exception {}".format(er))
            sys.exit()

        while 1:
            try:
                connection_socket, addr = self.server_socket.accept()
                print("Connection from port#: " + str(addr[1]))
                # connect to a new client
                x = threading.Thread(
                    target=self.start_new_client, args=(connection_socket,), daemon=True)
                x.start()
            except (Exception) as e:
                print("Error receiving new client ".format(e))
                break

        self.clean_up()

    def clean_up(self):
        if self.server_socket:
            self.server_socket.close()
        if self.hashtags:
            self.hashtags.clear()
        if self.clients:
            self.clients.clear()
        if self.tweets:
            self.tweets.clear()

        self.hashtags = self.clients = self.tweets, self.server_socket = None


server = Server()
server.run_server()
