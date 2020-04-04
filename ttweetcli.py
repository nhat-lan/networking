from socket import *
import sys
import json
import re

# '127.0.0.1'
MAX_VALID_PORTS = (2**16)-1
IPV4_REGEX = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
USERNAME_REGEX = re.compile("^[a-zA-Z0-9]+$")

class Client:
    def __init__(self):
        self.serverIP = None
        self.serverPort = None
        self.username = None
        self.clientSocket = None

    def isValidServerIP(self, ip):
        return ip and IPV4_REGEX.match(ip)

    def isValidPort(self, port):
        return port and (port.isDigit()) and (0<=int(port)<=MAX_VALID_PORTS)

    def isValidUsername(self, username):
        return username and USERNAME_REGEX.match(username)

    def isValidMessage(self, message):
        return message and len(message)

    def checkArguments(self, argv):
        # Check for correct number of arguments
        if len(argv) != 4:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            exit()

        # Check for serverIP argument
        if not isValidServerIP(argv[1]):
            print("error: server ip invalid, connection refused.")
            exit()

        # Check for serverPort argument
        if not isValidPort(argv[2]):
            print("error: server port invalid, connection refused.")
            exit()

        # Check for username
        if not isValidUsername(argv[3]):
            print("error: username has wrong format, connection refused.")
            exit()

        _,serverIP,serverPort,username = argv
        serverPort=int(serverPort)


    # Function to connect to the server
    def connectSocket(self):
        self.checkArguments()
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverIP, serverPort))
        except:
            print('Error Message: Server Not Found')
            exit()

        if isUserLoggedIn():
            print("username illegal, connection refused.")
            exit()
        else:
            print("username legal, connection established.")

    # TODO
    # Function to end the connection
    # exit <username>
	# Response:
	# 	Exit out of the system successfully
    def disconnect(self):
        clientSocket.send("exit " + username)
        receivedMessage = clientSocket.recv(1024)
        if receivedMessage:
            clientSocket.close()
            print("bye bye")
            exit()

    # Check which command to execute
    def checkCommand(self, commandline):
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
            self.getUsers()
        elif command == "gettweets":
            self.getTweets(commandList[1])
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
        if not message:
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

    # gettweets <another person username>
	# Response:
	# 	[ <sender_username>: “<tweet message>” <origin hashtag> ]
	# 	or
	# 	“no user <Username> in the system”
    def getTweets(self, user):
        clientSocket.send("gettweets " + user)
        receivedMessage = clientSocket.recv(1024)
        if receivedMessage == "no user " + user + " in the system":
            print(receivedMessage)
        else:
            receivedMessage = json.loads(receivedMessage)
            for tweet in receivedMessage:
                print(tweet)


client = Client()
client.connectSocket()
while True:
    command = input()
    client.checkCommand(command)