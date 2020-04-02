from socket import *
import sys

# '127.0.0.1'
# clientSocket.send('PUT ' + message.encode())
#     # Receive message from server
#     receivedMessage = clientSocket.recv(1024)

serverIP = ""
serverPort = None
username = ""
clientSocket = socket(AF_INET, SOCK_STREAM)


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
def connectSocket():
    try:
        clientSocket.connect((serverIP, serverPort))
    except:
        print('Error Message: Server Not Found')
        exit()
    
    if isUserLoggedIn():
        print("username illegal, connection refused.")
        # TODO disconnect
    else:
        print("username legal, connection established.")

# Function to end the connection
def disconnect():
    clientSocket.close()
    print("bye bye")
    

# call sever and check if the user is already logged in
# check_user_name <username>
# 	response:
# 	valid_username
# 	invalid_username

def isUserLoggedIn():
    clientSocket.send('check_user_name ' + username)
    receivedMessage = clientSocket.recv(1024)
    if (receivedMessage[1] == "True"):
        return True
    else:
        return False

# TODO
# tweet <username> <hashtag> <message>
# 	Response:
# 		Uploaded tweet successfully
# 		Failed to tweet
def tweet(hashtag, message):
    clientSocket.send('tweet ' + username + " " + hashtag + " " + message)
    receivedMessage = clientSocket.recv(1024)
    return

# TODO
def subscribe():
    return

# TODO
def unsubscribe():
    return

# TODO
def timeline():
    return

# TODO
def getUsers():
    return
