from socket import *
import sys
import json

# '127.0.0.1'

class Client:
    def __init__(self):
        self.serverIP = None
        self.serverPort = None
        self.username = None
        self.clientSocket = None

    def checkArguments(self):
        # Check for correct number of arguments
        if len(sys.argv) != 4:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            exit()

        # Check for serverIP argument
        try:
            serverIP = sys.argv[1]
        except:
            print("error: server ip invalid, connection refused.")
            exit()

        # Check for serverPort argument
        try: 
            serverPort = int(sys.argv[2])
        except:
            print("error: server port invalid, connection refused.")
            exit()

        # Check for username
        try: 
            username = sys.argv[3]

            # TODO check username format



        except:
            print("error: username has wrong format, connection refused.")
            exit()

    # Function to connect to the server
    def connectSocket(self):
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverIP, serverPort))
        except:
            print('Error Message: Server Not Found')
            exit()
        
        if isUserLoggedIn():
            print("username illegal, connection refused.")
            # TODO disconnect
        else:
            print("username legal, connection established.")

    # TODO
    # Function to end the connection
    def disconnect(self):
        clientSocket.close()
        print("bye bye")
        
    # Check which command to execute
    def checkCommand(self, command, message):
        if command == "tweet":
            # message: hashtags message
            self.tweet(message[0], message[1])
        elif command == "subscribe":
            self.subscribe(message)
        elif command == "unsubscribe":
            self.unsubscribe(message)
        elif command == "timeline":
            self.timeline()
        elif command == "getusers":
            self.getUsers()
        elif command == "gettweets":
            self.getTweets(message)
        elif command == "exit":
            self.disconnect()
        

    # call sever and check if the user is already logged in
    # check_user_name <username>
    # 	response:
    # 	valid_username
    # 	invalid_username

    def isUserLoggedIn(self):
        clientSocket.send('check_user_name ' + username)
        receivedMessage = clientSocket.recv(1024)
        if (receivedMessage == "Username is valid"):
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
        clientSocket.send("tweet " + username + " " + hashtag + " " + message)
        receivedMessage = clientSocket.recv(1024)
        
    # subscribe <username> <hashtag>
	# Response:
	# Subscribe to <hashtag> successfully
	# Failed to subscribe
    def subscribe(self, hashtag):
        # subscribe to server
        clientSocket.send("subscribe " + username + " " + hashtag)
        receivedMessage = clientSocket.recv(1024)

        if receivedMessage == "Subscribe to " + hashtag + " succesfully":
            print("operation success")
        else:
            print("operation failed: sub " + hashtag + " failed, already exists or exceeds 3 limitation")

    # unsubscribe <username> <hashtag>
	# Response:
	# 	Unsubscribed successfully
    def unsubscribe(self, hashtag):
        clientSocket.send("unsubscribe " + username + " " + hashtag)
        receivedMessage = clientSocket.recv(1024)
        if receivedMessage == "Unsubscribed successfully":
            print("operation success")
        
        # TODO NOT SURE HOW TO HANDLE Unsubscribe command should have no effect if it refers to a # that has not been subscribed to previously.


    # timeline <username>
	# Response:
	# 	[ <sender_username>: “<tweet message>” <origin hashtag> ]
    def timeline(self):
        clientSocket.send("timeline " + username)
        receivedMessage = json.loads(clientSocket.recv(1024))
        for tweet in receivedMessage:
            print(tweet)

    # getusers
	# Response:
	# 	[username1, username2,...]
    def getUsers(self):
        clientSocket.send("getusers")
        receivedMessage = json.loads(clientSocket.recv(1024))
        for user in receivedMessage:
            print(user)

    # TODO
    def getTweets(self):
        return
