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
        self.server_ip = None
        self.server_port = None
        self.username = None
        self.client_socket = None


    def is_valid_serverIP(self, ip):
        return ip and IPV4_REGEX.match(ip)

    def is_valid_port(self, port):
        return port and (port.isdigit()) and (0<=int(port)<=MAX_VALID_PORTS)

    def is_valid_username(self, username):
        return username and USERNAME_REGEX.match(username)

    def is_valid_hashtag(self, hashtag):
        return hashtag and HASHTAG_REGEX.match(hashtag)


    def check_arguments(self, argv):
        # Check for correct number of arguments
        if len(argv) != 4:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            exit()

        # Check for serverIP argument
        if not self.is_valid_serverIP(argv[1]):
            print("error: server ip invalid, connection refused.")
            exit()

        # Check for serverPort argument

        if not self.is_valid_port(argv[2]):
            print("error: server port invalid, connection refused.")
            exit()

        # Check for username
        if not self.is_valid_username(argv[3]):
            print("error: username has wrong format, connection refused.")
            exit()

        _, self.server_ip, self.server_port, self.username = argv
        self.server_port = int(self.server_port)


    # Function to connect to the server
    def connect_socket(self):
        self.check_arguments(sys.argv)
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            if self.is_user_logged_in():
                print("username illegal, connection refused.")
                self.client_socket.close()
                exit()
            else:
                print("username legal, connection established.")
        except:
            exit()

    # TODO
    # Function to end the connection
	# Response:
	# 	Exit out of the system successfully
    def disconnect(self):
        self.client_socket.send("exit " + self.username)
        received_message = self.client_socket.recv(1024)
        if received_message:
            self.client_socket.close()
            print("bye bye")
            exit()

    # Check which command to execute
    def check_command(self, commandline):
        commandList = commandline.split(" ")
        command = commandList[0]
        print(commandList)
        print('command', command)
        if command == "tweet":
            # message: hashtags message
            message = commandline.split("\"")[1]
            print('message', message)
            self.tweet(message, commandList[-1])
        elif command == "subscribe":
            self.subscribe(commandList[1])
        elif command == "unsubscribe":
            self.unsubscribe(commandList[1])
        elif command == "timeline":
            self.timeline()
        elif command == "getusers":
            self.get_users()
        elif command == "gettweets":
            self.get_tweets(commandList[1])
        elif command == "exit":
            self.disconnect()


    # call sever and check if the user is already logged in
    # check_user_name <username>
    # 	response:
    # 	valid_username
    # 	invalid_username

    def is_user_logged_in(self):
        self.client_socket.send('check_username ' + self.username)
        received_message = self.client_socket.recv(1024)
        if received_message == "Username is valid\n":
            return True
        else:
            return False

    # tweet <username> <hashtag> <message>
    # 	Response:
    # 		Uploaded tweet successfully
    # 		Failed to tweet
    def tweet(self, message, hashtag):

        # check message format
        if not message:
            print("message format illegal.")
            return
        elif len(message) > 150:
            print("message length illegal, connection refused.")
            return


        # check hashtag format
        if not self.is_valid_hashtag(hashtag):
            print("hashtag illegal format, connection refused.")
            return


        # tweet to server
        self.client_socket.send("tweet " + self.username + " " + hashtag + " " + message)
        received_message = self.client_socket.recv(1024)
        print('received_message ', received_message)

    # subscribe <username> <hashtag>
	# Response:
	# Subscribe to <hashtag> successfully
	# Failed to subscribe
    def subscribe(self, hashtag):
        # subscribe to server
        self.client_socket.send("subscribe " + self.username + " " + hashtag)
        received_message = self.client_socket.recv(1024)
        print('operation success ', received_message)
        
        # if received_message == "Subscribe to " + hashtag + " succesfully":
        #     print("operation success")
        # else:
        #     print("operation failed: sub " + hashtag + " failed, already exists or exceeds 3 limitation")

    # unsubscribe <username> <hashtag>
	# Response:
	# 	Unsubscribed successfully
    def unsubscribe(self, hashtag):
        self.client_socket.send("unsubscribe " + self.username + " " + hashtag)
        received_message = self.client_socket.recv(1024)
        if received_message == "Unsubscribed successfully":
            print("operation success")

        # TODO NOT SURE HOW TO HANDLE Unsubscribe command should have no effect if it refers to a # that has not been subscribed to previously.


    # timeline <username>
	# Response:
	# 	[ <sender_username>: <tweet message> <origin hashtag> ]
    def timeline(self):
        self.client_socket.send("timeline " + self.username)
        received_message = json.loads(self.client_socket.recv(1024))
        for tweet in received_message:
            print(tweet)

    # getusers
	# Response:
	# 	[username1, username2,...]
    def get_users(self):
        self.client_socket.send("getusers")
        received_message = json.loads(self.client_socket.recv(1024))
        for user in received_message:
            print(user)

    # gettweets <another person username>
	# Response:
	# 	[ <sender_username>: <tweet message> <origin hashtag> ]
	# 	or
	# 	"no user <Username> in the system"
    def get_tweets(self, user):
        self.client_socket.send("gettweets " + user)
        received_message = self.client_socket.recv(1024)
        if received_message == "no user " + user + " in the system":
            print(received_message)
        else:
            received_message = json.loads(received_message)
            for tweet in received_message:
                print(tweet)


client = Client()
client.connect_socket()
while True:
    command = raw_input()
    client.check_command(command)