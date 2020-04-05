from socket import *
import sys
import json
import re

# '127.0.0.1'
MAX_VALID_PORTS = (2**16)-1
IPV4_REGEX = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
USERNAME_REGEX = re.compile("^[a-zA-Z0-9]+$")
HASHTAG_REGEX = re.compile("^(#[a-zA-Z0-9]{1,14})((#[a-zA-Z0-9]{1,14}){0,4})$")

class Client:

    def __init__(self):

        # Initialize client state
        self.server_ip = None
        self.server_port = None
        self.client_socket = None
        self.is_connected=False

        self.username = None
        self.hashtags = set()
        self.timeline = []


    def run(self):
        """
        Main function to run and take commands
        """

        # Validate provided arguments
        if not self.is_valid_arguments(sys.argv[1:]):
            return

        self.server_ip,self.server_port,self.username = sys.argv[1:]
        self.server_port=int(self.server_port)

        self.connect_socket()

        while self.is_running():
            print('get new command')
            command_input = input()
            client.process_command(command_input)


    def clean_up(self):
        """
        Clean up data
        """

        self.server_ip = None
        self.server_port = None
        self.client_socket = None
        self.is_connected=False

        self.username = None
        self.hashtags = set()
        self.timeline = []


    def is_running(self):
        return self.is_connected

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

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
                self.client_socket.close()

            else:
                self.is_connected=True
                print("username legal, connection established.")

        except Exception as e:
            print("error: server ip invalid, connection refused.")
            self.client_socket.close()


    def disconnect(self):
        """
        Disconnect socket connect to server
        Clean up client state
        """

        self.send_message("exit " + self.username)
        received_message = self.client_socket.recv(1024)
        if received_message:
            self.client_socket.close()
            self.clean_up()
            print("bye bye")

        else:
            print(f'server error: cannot exit {self.username}')

    # Check which command to execute
    def process_command(self, command_input):

        command,args=None,None

        if command_input and len(command_input)>4:
            command, *args = command_input.split(" ")
            print('command', command)
            print(args)

        if command == "tweet" and len(args) > 0:
            # message: hashtags message
            args = command_input.split("\"")
            message=args[1]
            print('message', message)
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
        received_message = self.client_socket.recv(1024)
        return received_message


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
        received_message = self.client_socket.recv(1024)
        print('received_message ', received_message)


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
        received_message = self.client_socket.recv(1024)

        if received_message:
            self.hashtags.add(hashtag)
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
        received_message = self.client_socket.recv(1024)

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
        print(self.timeline)


    def get_users(self):
        """
        Get list of users from server and print out to console
        $getusers

        Response:
          [username1, username2,...]
        """

        self.send_message("$getusers")
        received_message = json.loads(self.client_socket.recv(1024))
        for user in received_message:
            print(user)


    def get_tweets(self, user):
        """
        Get all tweets of an user from server
        $gettweets <username>

        Response:
            [ <sender_username>: <tweet message> <origin hashtag> ]
            or
            "no user <Username> in the system"
        """

        self.send_message("$gettweets " + user)
        received_message = json.loads(self.client_socket.recv(1024))
        if received_message == "no user " + user + " in the system":
            print(received_message)
        else:
            received_message = json.loads(received_message)
            for tweet in received_message:
                print(tweet)

    def exit(self):
        print('exit')


if __name__=="__main__":
    client = Client()
    client.run()
