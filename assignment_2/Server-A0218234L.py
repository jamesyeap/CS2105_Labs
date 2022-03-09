import sys
from socket import *
import hashlib

# numbers indicating the mode of the simulators
RELIABLE_CHANNEL_MODE = 0;
ERROR_CHANNEL_MODE = 1;
REORDERING_CHANNEL_MODE = 2;

# port numbers of the 3 channels
RELIABLE_CHANNEL_PORT_NUMBER = 4445;
ERROR_CHANNEL_PORT_NUMBER = 4446;
REORDERING_CHANNEL_PORT_NUMBER = 4447;

# request method codes
REQUEST_CONNECTION = 'STID_';

""" ---- HELPER FUNCTIONS -------------------------------------------------- """

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

def get_response_message(socket):
	return socket.recv(64);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print(queue_len); # TO REMOVE

	while (True):
		if (queue_len == b'0_'):
			break;

		print(queue_len); # TO REMOVE
		queue_len = get_response_message(socket);

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = int(sys.argv[4]); 	# get the port number of the TCP socket of the simulator on the machine
input_file_name = sys.argv[5];  # get the name of the file to write the hash to

""" create client TCP socket
	connect to the remote TCP socket
	request connection
	wait for our turn 
"""
clientSocket = socket(AF_INET, SOCK_STREAM);
clientSocket.connect((ip_address, port_num));
clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key + '_S'));
wait_for_turn(clientSocket);


""" open the file to be sent
"""
filetosend = open(input_file_name, 'rb');
dataToSend = filetosend.read(5);

clientSocket.send("hello".encode());

print("sent data");

""" my own notes
- my student-key is 651723

- to test the code,
	python3 Server-A0218234L.py 651723 0 137.132.92.111 4445 hello.txt
"""