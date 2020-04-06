from socket import *
import sys
import json
import re

from queue import Queue
from copy import copy

from _thread import *
import threading

# '127.0.0.1'
MAX_VALID_PORTS = (2**16)-1
IPV4_REGEX = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
USERNAME_REGEX = re.compile("^[a-zA-Z0-9]+$")
# HASHTAG BUG, need to be 2 or more characters
HASHTAG_REGEX = re.compile("^(#[a-zA-Z0-9]{1,14})((#[a-zA-Z0-9]{1,14}){0,4})$")

class ClientListener:

    def __init__(self, ip, port, timeline_queue, hashtags):
        self.server_addr = (ip, port)
        self.hashtags = hashtags
        self.timeline_queue=timeline_queue


    def subscribe(self,hashtag):

        try:
            start_new_thread(start_connection, (hashtag))
        except Exception as e:
            print(str(e))

    def is_subscribe(self, hashtag):
        return self.hashtags and hashtag in self.hashtags

    def start_connection(self):

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(self.server_addr)

        while self.is_subscribe(hashtag):
            data = sock.recv(1024)
            if data and hashtag in self.hashtags:
                timeline_queue.put(data)
                print(data)

        sock.close()


    def exit(self):
        self.server_addr,self.hashtags,self.timeline_queue = None,None,None




class Client:

    def __init__(self):

        # Initialize client state
        self.server_ip = None
        self.server_port = None
        self.client_socket = None
        self.client_listener = None

        self.is_connected=False

        self.username = None
        self.hashtags = set()
        self.timeline_queue = Queue()


    def run(self):
        """
        Main function to run and take commands
        """

        # Validate provided arguments
        if self.is_valid_arguments(sys.argv[1:]):
            self.server_ip,self.server_port,self.username = sys.argv[1:]
            self.server_port=int(self.server_port)

            self.connect_socket()
            self.client_listener=ClientListener(*sys.argv[1:3],self.hashtags,self.timeline_queue)

            while self.is_running():
                command_input = input()
                client.process_command(command_input)

        self.clean_up()


    def clean_up(self):
        """
        Clean up client's data
        """

        if self.client_socket:
            self.client_socket.close()

        if self.timeline_queue:
            self.timeline_queue.empty()

        if self.client_listener:
            self.client_listener.exit()

        self.server_ip = None
        self.server_port = None

        self.client_socket = None
        self.is_connected=False

        self.username = None
        self.hashtags = None

        self.timeline_queue = None


    def is_running(self):
        return self.is_connected

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def receive_message(self):
        message=self.client_socket.recv(1024)
        return message.decode('utf-8')

    def is_valid_server_ip(self, ip):
        return ip and IPV4_REGEX.match(ip)

    def is_valid_port(self, port):
        return port and (port.isdigit()) and (0<=int(port)<=MAX_VALID_PORTS)

    def is_valid_username(self, username):
        return username and USERNAME_REGEX.match(username)

    def is_valid_hashtag(self, hashtag):
        return hashtag and HASHTAG_REGEX.match(hashtag)


    def is_valid_arguments(self, argv):
        # Check for correct number of arguments
        if len(argv) != 3:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            return False

        # Check for server_ip argument
        elif not self.is_valid_server_ip(argv[0]):
            print("error: server ip invalid, connection refused.")
            return False

        # Check for server_port argument

        elif not self.is_valid_port(argv[1]):
            print("error: server port invalid, connection refused.")
            return False

        # Check for username
        elif not self.is_valid_username(argv[2]):
            print("error: username has wrong format, connection refused.")
            return False

        return True


    def connect_socket(self):
        """
        Create socket connects to server
        """

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            if self.is_user_logged_in():
                print("username illegal, connection refused.")

            else:
                self.is_connected=True
                print("username legal, connection established.")

        except Exception as e:
            # IF PORT DOESN'T EXISTS, IT GOES HERE TOO
            print("error: server ip invalid, connection refused.")


    def disconnect(self):
        """
        Disconnect socket connect to server
        Clean up client state
        """

        self.send_message("exit " + self.username)
        received_message = self.receive_message()
        if received_message:
            print("bye bye")

        else:
            print(f'server error: cannot exit {self.username}')

    # Check which command to execute
    def process_command(self, command_input):
        # print("Process command")

        command,args=None,None
        if command_input and len(command_input)>3:
            command, *args = command_input.split(" ")

        if command == "tweet" and len(args) > 0:
            # print("Command is tweet")
            # message: hashtags message
            args = command_input.split("\"")
            message=args[1]
            self.tweet(message, args[-1].strip())
        elif command == "subscribe" and len(args)==1:
            self.subscribe(args[0])
        elif command == "unsubscribe" and len(args)==1:
            self.unsubscribe(args[0])
        elif command == "timeline" and not args:
            self.timeline()
        elif command == "getusers" and not args:
            self.get_users()
        elif command == "gettweets" and len(args)==1:
            self.get_tweets(args[1])
        elif command == "exit" and not args:
            self.disconnect()
        else:
            print('Command not found. Here is list of valid command:'\
                ' tweet, subscribe, unsubscribe, timeline, getusers,'\
                ' gettweets, exit')


    def is_user_logged_in(self):
        """
        Check if user is not online
        $checkusername <username>

        response:
            0 : user is logged in
            1 : user is not logged in
        """

        self.send_message(f'$checkusername {self.username}')
        received_message = self.receive_message()
        return int(received_message)


    def tweet(self, message, hashtag):
        """
        Send tweet to server
        $tweet <username> <hashtag> <message>

        Response:
            0: Failed to upload tweet
            1: Uploaded tweet successfully
        """

        # check message format
        if not message:
            print("message format illegal.")
            return
        elif len(message) > 150:
            print("message length illegal, connection refused.")
            return

        # check hashtag format
        if not self.is_valid_hashtag(hashtag) and hashtag != '#ALL':
            print("hashtag illegal format, connection refused.")
            return

        # tweet to server
        self.send_message(f"$tweet {self.username} {hashtag} {message}")
        print("Tweeted")


    def subscribe(self, hashtag):
        """
        Subscribe username to hashtag
        $subscribe <username> <hashtag>

        Response:
            0: Failed to subscribe
            1: Subscribe successfully
        """

        # check hashtag format
        if not self.is_valid_hashtag(hashtag):
            print("hashtag illegal format, connection refused.")
            return

        # Check if subscribed hashtags is not over limit (3)
        if len(self.hashtags) >= 3:
            print(f'operation failed: sub {hashtag} failed,' \
                   ' already exists or exceeds 3 limitation')
            return

        # subscribe to server
        self.send_message(f"$subscribe {self.username} {hashtag}")
        received_message = self.receive_message()

        if received_message:
            self.hashtags.add(hashtag)
            self.client_listener.subscribe(hashtag)
            print("operation success")

        else:
            print(f'operation failed: server failed')


    def unsubscribe(self, hashtag):
        """
        Unsubscribe userhame with hashtag
        $unsubscribe <username> <hashtag>

        Response:
            0: Failed to unsubscribe
            1: Unsubscribed successfully
        """

        # Check if hashtag is not subscribed yet
        if hashtag not in self.hashtags and \
            (len(self.hashtags) and hashtag!='#ALL'):
            return

        self.send_message(f"$unsubscribe {self.username} {hashtag}")
        received_message = self.receive_message()

        if received_message:
            if hashtag == '#ALL':
                self.hashtags.clear()
            else:
                self.hashtags.remove(hashtag)

            print("operation success")

        else:
            print('operation failed: server failed')


    def timeline(self):
        """
        Print out timeline which is multiline of received
        messages from server.
        """

        timeline_queue = list(self.timeline_queue.queue)
        for message in timeline_queue:
            print(message)


    def get_users(self):
        """
        Get list of users from server and print out to console
        $getusers

        Response:
          [username1, username2,...]
        """

        self.send_message("$getusers")
        received_message = self.receive_message()
        users = json.loads(received_message)
        for user in users:
            print(user)


    def get_tweets(self, username):
        """
        Get all tweets of an username from server
        $gettweets <username>

        Response:
            [ <sender_username>: "<tweet message>" <origin hashtag> ]
            or
            "no user <Username> in the system"
        """

        self.send_message("$gettweets " + username)
        is_done=False
        messages=''

        while not is_done:
            received_message = self.client_socket.recv(1024)

            if received_message:
                if received_message == 'Done':
                    is_done=True
                else:
                    messages+=received_message

        tweets = json.loads(messages)
        print(tweet for tweet in tweets)



if __name__=="__main__":
    client = Client()
    client.run()
