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
	return socket.recv(1000);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print(queue_len); # TO REMOVE

	while (queue_len != b'0_' or queue_len != b'-1_'):
		if (queue_len != b''):
			print(queue_len); # TO REMOVE
		queue_len = get_response_message(socket);

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = sys.argv[4]; 		# get the port number of the TCP socket of the simulator on the machine
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
