import sys

# numbers indicating the mode of the simulators
RELIABLE_CHANNEL_MODE = 0;
ERROR_CHANNEL_MODE = 1;
REORDERING_CHANNEL_MODE = 2;

# request message headers
request_connection = 'STID_'

def request_connection()

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = sys.argv[4]; 		# get the port number of the TCP socket of the simulator on the machine
output_file_name = sys.argv[5]; # get the name of the file to write the hash to

""" request connection and get queue_length """
# TODO

""" get updated queue_length """

""" once queue_length is '0_',
	connect to the TCP socket of the machine running the simulator
	a second time
"""
clientSocket = socket(AF_INET, SOCK_STREAM);
clientSocket.connect((ip_address, port_num));



