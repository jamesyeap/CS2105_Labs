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

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = int(sys.argv[4]); 		# get the port number of the TCP socket of the simulator on the machine
output_file_name = sys.argv[5]; # get the name of the file to write the hash to

""" create client TCP socket
	connect to the remote TCP socket
	request connection
	wait for our turn 
"""
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip_address, port_num));
clientSocket.send(create_request_message(student_key, '_C'));
wait_for_turn();

""" once its our turn, connect to the TCP socket again
"""
clientSocket.connect((ip_address, port_num));

# ❌ (probably wrong)
# if (mode == RELIABLE_CHANNEL_MODE):
# 	clientSocket.connect((ip_address, RELIABLE_CHANNEL_PORT_NUMBER));
# elif (mode == ERROR_CHANNEL_MODE):
# 	clientSocket.connect((ip_address, ERROR_CHANNEL_PORT_NUMBER));
# else: # mode == REORDERING_CHANNEL_MODE
# 	clientSocket.connect((ip_address, REORDERING_CHANNEL_PORT_NUMBER));

""" ---- HELPER FUNCTIONS -------------------------------------------------- """

def create_request_message(method_code, data=''):
	return (method_code + data).encode();

def get_response_message():
	return clientSocket.recv(1000);

def wait_for_turn():
	queue_len = get_response_message();

	while (queue_len != b'0_'):
		print(queue_len); # TO REMOVE
		queue_len = get_response_message();

""" my own notes
- my student-key is 651723

- to test the code,
python3 Client-A0218234L.py 651723 0 137.132.92.111 4445 output.txt

"""