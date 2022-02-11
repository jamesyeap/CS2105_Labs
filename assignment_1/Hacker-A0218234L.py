from socket import *
import hashlib
import sys
import time

# server details
SERVER_IP_ADDRESS = '137.132.92.111'
SERVER_PORT = 4444

# request message - request method codes
REQUEST_CONNECTION = b'STID_'
LOGIN_REQUEST = b'LGIN_'
LOGOUT_REQUEST = b'LOUT_'
GET_REQUEST = b'GET__'
SEND = b'PUT__'
CLOSE_CONNECTION = b'BYE__'

# response message - response codes
FILE_DATA = b'100_'
HANDSHAKE_SUCCESSFUL = b'200_'
LOGIN_SUCCESSFUL = b'201_'
LOGOUT_SUCCESSFUL = b'202_'
HASH_MATCHED = b'203_'
HANDSHAKE_FAILED_INVALIDSTUDENTKEY = b'401_'
INVALID_OPERATION = b'402_'
INVALID_PASSWORD = b'403_'
INVALID_HASH = b'404_'
PERMISSION_DENIED = b'405_'
INVALID_REQUEST_METHOD = b'406_'

# ------- SEND REQUEST METHODS ---------------------------------------------------

def request_connection(clientSocket, student_key):
	clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key))
	return get_response_code(clientSocket) == HANDSHAKE_SUCCESSFUL		

def request_login(clientSocket, password):
	clientSocket.send(create_request_message(LOGIN_REQUEST, password))
	return get_response_code(clientSocket) == LOGIN_SUCCESSFUL

def request_logout(clientSocket):
	clientSocket.send(create_request_message(LOGOUT_REQUEST))
	return get_response_code(clientSocket) == LOGOUT_SUCCESSFUL

""" returns the file received from server in byte-format """
def request_get_file(clientSocket):
	clientSocket.send(create_request_message(GET_REQUEST))
	file_size = extract_file_size(clientSocket)
	file = clientSocket.recv(file_size)

	return file

def request_validate_hash(clientSocket, hash):
	clientSocket.send(create_request_message(SEND, hash))
	return get_response_code(clientSocket) == HASH_MATCHED

def request_close_connection(clientSocket):
	clientSocket.send(create_request_message(CLOSE_CONNECTION))

# ------- UTIL METHODS -------------------------------------------------------------

def create_request_message(method_code, data=b''):
	request_message = method_code + data
	return request_message;

def get_response_code(clientSocket):
	response_code = clientSocket.recv(4)
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
	return str(hashlib.md5(data).hexdigest()).encode()

# returns a local socket that is connected to the specified server
def create_socket(student_key):
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((SERVER_IP_ADDRESS, SERVER_PORT))
	request_connection(clientSocket, student_key)	

	return clientSocket

# ------ MAIN ----------------------------------------------------------------

# get student key to establish connection with server
student_key = (sys.argv[1]).encode()

# pre-compute password combinations
precomputed_passwords = []
for i in range(0, 10000):
	precomputed_passwords.append(str(i).encode().rjust(4, b'0'))

# request for connection to server
clientSocket = create_socket(student_key)

# keep track of the number of successful file-retrievals
num_success = 0

# keep track of passwords attempted
current_password = 0

# try to login using all possible password combinations (0000-9999)
while (num_success < 8 and current_password < 10000):
	padded_password = precomputed_passwords[current_password]

	can_login = request_login(clientSocket, padded_password)

	if (can_login):
		can_validate_hash = False

		while (can_validate_hash == False):			
			target_file = request_get_file(clientSocket)
			md5_hash = generate_MD5_hash(target_file)
			can_validate_hash = request_validate_hash(clientSocket, md5_hash)
		
		request_logout(clientSocket)
		num_success += 1

	current_password += 1

# close the connection to the server
request_close_connection(clientSocket)
clientSocket.close()








