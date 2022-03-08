import sys

# numbers indicating the mode of the simulators
RELIABLE_CHANNEL_MODE = 0;
ERROR_CHANNEL_MODE = 1;
REORDERING_CHANNEL_MODE = 2;

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = sys.argv[4]; 		# get the port number of the TCP socket of the simulator on the machine
input_file_name = sys.argv[5];  # get the name of the file to write the hash to

""" connect to the TCP socket of the machine running the simulator """
clientSocket = socket(AF_INET, SOCK_STREAM); # ⚠️ should the server program have a client socket or server socket
clientSocket.connect((ip_address, port_num));

""" request connection """
# TODO

""" open the file to be transferred """
file_to_transfer = open(input_file_name);
