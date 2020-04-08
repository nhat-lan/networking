import sys
import json
import re

from socket import *
from queue import Queue
import threading

# '127.0.0.1'
MAX_VALID_PORTS = (2**16)-1
IPV4_REGEX = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
USERNAME_REGEX = re.compile("^[a-zA-Z0-9]+$")
HASHTAG_REGEX = re.compile("^(#[a-zA-Z0-9]{1,14})((#[a-zA-Z0-9]{1,14}){0,4})$")


class ClientListener:

    def __init__(self, addr, timeline_queue):
        self.server_addr = addr
        self.timeline_queue = timeline_queue
        self.connection_socket = socket(AF_INET, SOCK_STREAM)

    def sign_in(self, username):
        """
        Sign in username and establish listener connection.
        $signin <username>

        response:
            0 : failure, user is already signed in
            1 : signed in successfully
        """

        is_signed_in = 0
        try:
            self.connection_socket.connect((self.server_addr))
            self.connection_socket.sendall(
                f'$signin {username}'.encode('utf-8'))
            received_message = self.connection_socket.recv(
                1024).decode('utf-8')

            is_signed_in = int(received_message)
        except Exception as e:
            print(e)
            pass
        finally:
            return is_signed_in

    def start_listener(self):
        """
        Start listener thread running asynchronousely

        """

        try:
            x = threading.Thread(
                target=self.listen, daemon=True)
            x.start()
        except Exception as e:
            pass
            # print(str(e))

    def listen(self):
        """
        Client listener loop waiting for new messages from server
        """

        try:
            while 1:
                data = self.connection_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    self.timeline_queue.put(message)
                    print(message)
        except Exception as e:
            # print(e)
            pass

    def exit(self):
        """
        Exit the client listener and clean up data
        """

        if self.connection_socket:
            self.connection_socket.close()
        self.server_addr = self.timeline_queue = self.connection_socket = None


class Client:

    def __init__(self):

        # Initialize client state
        self.server_ip = self.server_port = self.client_socket = None
        self.client_listener = self.username = None
        self.is_connected = False
        self.hashtags = set()
        self.timeline_queue = Queue()

    def run(self):
        """
        Main function to run and take commands
        """

        try:
            # Validate provided arguments
            if self.is_valid_arguments(sys.argv[1:]):
                self.server_ip, self.server_port, self.username = sys.argv[1:]
                self.server_port = int(self.server_port)

                self.connect_socket()

                if self.is_running():
                    self.sign_in()

                while self.is_running():
                    command_input = input().strip()
                    client.process_command(command_input)
        except Exception as e:
            # print(e)
            pass
        finally:
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

        self.server_ip = self.server_port = self.client_socket = None
        self.client_listener = self.username = self.hashtags = self.timeline_queue = None
        self.is_connected = False

    def is_running(self):
        """
        Return running status of client connection to server
        """
        return self.is_connected

    def send_message(self, message):
        """
        Helper function to send encoded message to server
        """
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(e)
            pass

    def receive_message(self):
        """
        Helper function to receive and decode message to server
        """
        message = ''
        try:
            message = self.client_socket.recv(1024)
        except Exception as e:
            # print(e)
            pass
        return message.decode('utf-8')

    def is_valid_server_ip(self, ip):
        """
        Helper function to test regex matching for ip
        """
        return ip and IPV4_REGEX.match(ip)

    def is_valid_port(self, port):
        """
        Helper function to test regex matching for port
        """
        return port and (port.isdigit()) and (0 <= int(port) <= MAX_VALID_PORTS)

    def is_valid_username(self, username):
        """
        Helper function to test regex matching for username
        """
        return username and USERNAME_REGEX.match(username)

    def is_valid_hashtag(self, hashtag):
        """
        Helper function to test regex matching for hashtag
        """
        return hashtag and HASHTAG_REGEX.match(hashtag)

    def validate_server_ip(self, ip):
        """
        Helper function to validate server ip
        Print out error if exists
        """
        if not self.is_valid_server_ip(ip):
            print("error: server ip invalid, connection refused.")
            return False
        return True

    def validate_server_port(self, port):
        """
        Helper function to validate server port
        Print out error if exists
        """
        if not self.is_valid_port(port):
            print("error: server ip invalid, connection refused.")
            return False
        return True

    def validate_username(self, username):
        """
        Helper function to validate username
        Print out error if exists
        """
        if not self.is_valid_username(username):
            print("error: username has wrong format, connection refused.")
            return False
        return True

    def validate_hashtag(self, hashtag):
        """
        Helper function to validate hashtag
        Print out error if exists
        """
        if not self.is_valid_hashtag(hashtag):
            print("hashtag illegal format, connection refused.")
            return False
        return True

    def validate_message(self, message):
        """
        Helper function to validate message
        Print out error if exists
        """
        if not message:
            print("message format illegal.")
            return False
        elif len(message) > 150:
            print("message length illegal, connection refused.")
            return False
        return True

    def is_valid_arguments(self, argv):
        """
        Validate input arguments
        """
        # Check for correct number of arguments
        if len(argv) != 3:
            print("error: args should contain <ServerIP> <ServerPort> <Username>")
            return False

        ip, port, username = argv
        return self.validate_server_ip(ip) and self.validate_server_port(port)\
            and self.validate_username(username)

    def process_command(self, command_input):
        """
        Process the command
        """

        command = args = None
        if command_input and len(command_input) > 3:
            command, *args = command_input.split(" ")

        if command == "tweet":
            if len(args) == 0:
                print('invalid arguments')
            # message: hashtags message
            args = command_input.split("\"")
            message = args[1]
            self.tweet(message, args[-1].strip())
        elif command == "subscribe" and len(args) == 1:
            self.subscribe(args[0])
        elif command == "unsubscribe":
            hashtag = ' '.join(args)
            self.unsubscribe(hashtag)

        elif command == "timeline":
            if len(args):
                print('invalid arguments')
            else:
                self.timeline()

        elif command == "getusers":
            if len(args):
                print('invalid arguments')
            else:
                self.get_users()

        elif command == "gettweets":
            username = ' '.join(args)
            self.get_tweets(username)

        elif command == "exit":
            if len(args):
                print('invalid arguments')
            else:
                self.disconnect()
        else:
            print('Command not found. Here is list of valid command:'
                  ' tweet, subscribe, unsubscribe, timeline, getusers,'
                  ' gettweets, exit')

    def connect_socket(self):
        """
        Create socket connects to server
        """

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.is_connected = True

        except Exception as e:
            # IF PORT DOESN'T EXISTS, IT GOES HERE TOO
            print("error: server ip invalid, connection refused.")

    def disconnect(self):
        """
        Disconnect socket connect to server
        Clean up client state
        """

        self.send_message("$exit " + self.username)
        self.is_connected = False
        print("bye bye")

    def sign_in(self):
        """
        Sign user in
        $signin <username >

        response:
            0: failure, user is already signed in
            1: signed in successfully
        """

        # Create client_listener
        self.client_listener = ClientListener((self.server_ip,
                                               self.server_port), self.timeline_queue)
        if self.client_listener.sign_in(self.username):
            print('username legal, connection established.')
            self.client_listener.start_listener()
        else:
            print("username illegal, connection refused.")
            self.is_connected = False

    def tweet(self, message, hashtag):
        """
        Send tweet to server
        $tweet <username > <hashtag > <message>

        Response:
            0: Failed to upload tweet
            1: Uploaded tweet successfully
        """

        # check message and hashtag formats
        if self.validate_message(message) and self.validate_hashtag(hashtag):
            if hashtag == '#ALL':
                print("hashtag illegal format, connection refused.")
                return
            # tweet to server
            self.send_message(f"$tweet {self.username} {hashtag} {message}")

    def subscribe(self, hashtag):
        """
        Subscribe username to hashtag
        $subscribe <username> <hashtag>

        Response:
            0: Failed to subscribe
            1: Subscribe successfully
        """

        # Validate hashtag format`
        if not self.validate_hashtag(hashtag):
            return

        # Check if subscribed hashtags is not over limit (3)
        if hashtag in self.hashtags or len(self.hashtags) >= 3:
            print(f'operation failed: sub {hashtag} failed,'
                  ' already exists or exceeds 3 limitation')
            return

        # subscribe to server
        self.send_message(f"$subscribe {self.username} {hashtag}")
        self.hashtags.add(hashtag)
        print("operation success")

    def unsubscribe(self, hashtag):
        """
        Unsubscribe userhame with hashtag
        $unsubscribe <username> <hashtag>

        Response:
            0: Failed to unsubscribe
            1: Unsubscribed successfully
        """

        # Validate hashtag format
        if not self.validate_hashtag(hashtag):
            return

        # Check if hashtag is not subscribed yet
        if (hashtag == '#ALL' and len(self.hashtags) == 0) \
                or (hashtag != '#ALL' and hashtag not in self.hashtags):
            return

        self.send_message(f"$unsubscribe {self.username} {hashtag}")
        if hashtag == '#ALL':
            self.hashtags.clear()

        else:
            self.hashtags.remove(hashtag)

        print("operation success")

    def timeline(self):
        """
        Print out timeline which is multiline of received
        messages from server.
        """

        timeline_queue = list(self.timeline_queue.queue)
        if len(timeline_queue) > 0:
            print('\n'.join(timeline_queue))

    def get_users(self):
        """
        Get list of users from server and print out to console
        $getusers

        Response:
          [username1, username2, ...]
        """

        self.send_message("$getusers")
        received_message = self.receive_message()
        users = json.loads(received_message)
        print('\n'.join(users))

    def get_tweets(self, username):
        """
        Get all tweets of an username from server
        $gettweets <username>

        Response:
            [ <sender_username> : "<tweet message>" <origin hashtag> ]
            or
            "no user <Username> in the system"
        """

        if not self.validate_username(username):
            return

        self.send_message("$gettweets " + username)
        is_done = False
        messages = ''

        while not is_done:
            received_message = self.receive_message()

            if received_message:
                if received_message == 'Done':
                    is_done = True
                else:
                    messages += received_message

        if len(messages):
            tweets = json.loads(messages)
            # Print to console
            if len(tweets) > 0:
                print('\n'.join(tweets))


if __name__ == "__main__":
    client = Client()
    client.run()
