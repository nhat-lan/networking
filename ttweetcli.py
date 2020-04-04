from socket import *
import sys
import json

# '127.0.0.1'

class Client:
    def __init__(self):
        self.server_ip = None
        self.server_port = None
        self.username = None
        self.client_socket = None

    def check_arguments(self):
        # Check for correct number of arguments
        if len(sys.argv) != 4:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            exit()

        # Check for serverIP argument
        try:
            self.server_ip = sys.argv[1]
        except:
            print("error: server ip invalid, connection refused.")
            exit()

        # Check for serverPort argument
        try: 
            self.server_port = int(sys.argv[2])
        except:
            print("error: server port invalid, connection refused.")
            exit()

        # Check for username
        try: 
            self.username = sys.argv[3]

            # TODO check username format



        except:
            print("error: username has wrong format, connection refused.")
            exit()

    # Function to connect to the server
    def connect_socket(self):
        self.check_arguments()
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
        except:
            print('Error Message: Server Not Found')
            exit()
        
        if self.is_user_logged_in():
            print("username illegal, connection refused.")
            # TODO disconnect
        else:
            print("username legal, connection established.")

    # TODO
    # Function to end the connection
    # exit <username>
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
        command = commandList[1]
        if command == "tweet":
            # message: hashtags message
            message = commandline.split("\"")[1]
            self.tweet(message,commandList[-1])
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
        if (received_message == "Username is valid"):
            return True
        else:
            return False

    # tweet <username> <hashtag> <message>
    # 	Response:
    # 		Uploaded tweet successfully
    # 		Failed to tweet
    def tweet(self, hashtag, message):

        # check message format
        if message == None or len(message) < 1:
            print("message format illegal.")
            return
        elif len(message) > 150:
            print("message length illegal, connection refused.")
            return

        
        # check hashtag format

        if hashtag[0] != '#' or len(hashtag) > 15 or hashtag.contain(" "):
            print("hashtag illegal format, connection refused.")
            return

        
        hashtags = hashtag.split("#")
        if len(hashtags) > 5:
            print("hashtag illegal format, connection refused.")
            return
        
        for hash in hashtags:
            if len(hash) < 2:
                print("hashtag illegal format, connection refused.")
                return
        
        # TODO ? hashtag only has alphabet characters(lower case + upper case) and numbers


        # tweet to server
        self.client_socket.send("tweet " + self.username + " " + hashtag + " " + message)
        received_message = self.client_socket.recv(1024)
        
    # subscribe <username> <hashtag>
	# Response:
	# Subscribe to <hashtag> successfully
	# Failed to subscribe
    def subscribe(self, hashtag):
        # subscribe to server
        self.client_socket.send("subscribe " + self.username + " " + hashtag)
        received_message = self.client_socket.recv(1024)

        if received_message == "Subscribe to " + hashtag + " succesfully":
            print("operation success")
        else:
            print("operation failed: sub " + hashtag + " failed, already exists or exceeds 3 limitation")

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