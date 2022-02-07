from socket import *
import hashlib
import sys
import time

# my own notes:
#  student-key is 651723

# server details
SERVER_IP_ADDRESS = '137.132.92.111'
SERVER_PORT = 4444

# request message - request method codes
REQUEST_CONNECTION = 'STID_'
LOGIN_REQUEST = 'LGIN_'
LOGOUT_REQUEST = 'LOUT_'
GET_REQUEST = 'GET__'
SEND = 'PUT__'
CLOSE_CONNECTION = 'BYE__'

# response message - response codes
FILE_DATA = '100_'
HANDSHAKE_SUCCESSFUL = '200_'
LOGIN_SUCCESSFUL = '201_'
LOGOUT_SUCCESSFUL = '202_'
HASH_MATCHED = '203_'
HANDSHAKE_FAILED_INVALIDSTUDENTKEY = '401_'
INVALID_OPERATION = '402_'
INVALID_PASSWORD = '403_'
INVALID_HASH = '404_'
PERMISSION_DENIED = '405_'
INVALID_REQUEST_METHOD = '406_'

# ------- SEND REQUEST METHODS ---------------------------------------------------

def request_connection(clientSocket, student_key):
	clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key))
	# return get_response_code(clientSocket) == HANDSHAKE_SUCCESSFUL	
	get_response_code(clientSocket)

def request_login(clientSocket, password):
	clientSocket.send(create_request_message(LOGIN_REQUEST, password))
	# return get_response_code(clientSocket) == LOGIN_SUCCESSFUL
	get_response_code(clientSocket)

def request_logout(clientSocket):
	clientSocket.send(create_request_message(LOGOUT_REQUEST))
	# return get_response_code(clientSocket) == LOGOUT_SUCCESSFUL
	get_response_code(clientSocket)

""" returns the file received from server in byte-format """
def request_get_file(clientSocket):
	clientSocket.send(create_request_message(GET_REQUEST))
	file_size = extract_file_size(clientSocket)
	file = clientSocket.recv(file_size)

	return file

def request_validate_hash(clientSocket, hash):
	clientSocket.send(create_request_message(SEND, hash))
	# if (get_response_code(clientSocket) == HASH_MATCHED):
	# 	print("File validated!")
	# 	return True

	# return False
	get_response_code(clientSocket)

def request_close_connection(clientSocket):
	clientSocket.send(create_request_message(CLOSE_CONNECTION))

# ------- UTIL METHODS -------------------------------------------------------------

def create_request_message(method_code, data=""):
	request_message = method_code + data
	return (request_message).encode();

def get_response_code(clientSocket):
	response_code = clientSocket.recv(4).decode();
	return response_code

""" note: get_file_size() should only be called inside the function get_file() """
def extract_file_size(clientSocket):
	# can ignore the status code because
	get_response_code(clientSocket) # can assume always successful according to the FSM

	encodedFileSize = b''
	x = clientSocket.recv(1)

	while (x != b'_'):
		encodedFileSize += x
		x = clientSocket.recv(1)

	file_size = int(encodedFileSize)

	return file_size

def generate_MD5_hash(data):
	return str(hashlib.md5(data).hexdigest())

# returns a local socket that is connected to the specified server
def create_socket(student_key):
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((SERVER_IP_ADDRESS, SERVER_PORT))
	# can_connect = request_connection(clientSocket, student_key)
	request_connection(clientSocket, student_key)

	# if (not can_connect):
	# 	print("Handshake could not be established due to invalid student id")
	# 	clientSocket.close()
	# 	exit(1)

	return clientSocket


# ------ MAIN ---------------------------------------------------------------

# get student key to establish connection with server
student_key = sys.argv[1]

# request for connection to server
clientSocket = create_socket(student_key)

# keep track of the number of successful file-retrievals
num_success = 0

# keep track of passwords attempted
current_password = 0

# try to login using all possible password combinations (0000-9999)
while (num_success < 8 and current_password < 10000):
	padded_password = str(current_password).zfill(4)
	can_login = request_login(clientSocket, padded_password)

	if (can_login):
		target_file = request_get_file(clientSocket)
		md5_hash = generate_MD5_hash(target_file)
		request_validate_hash(clientSocket, md5_hash)

		num_success += 1
		request_logout(clientSocket)

	current_password += 1

# close the connection to the server
request_close_connection(clientSocket)
clientSocket.close()








