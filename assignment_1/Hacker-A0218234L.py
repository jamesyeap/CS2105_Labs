from socket import *
import hashlib
import sys

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

# create local socket
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((SERVER_IP_ADDRESS, SERVER_PORT))

# request for connection to server
student_key = sys.argv(1)
can_connect = request_connection(student_key)

if (not can_connect):
	print("Handshake could not be established due to invalid student id")
	clientSocket.close()
	exit(1)

# try to login using all possible password combinations (0000-9999)
for i in range(0, 1000):
	can_login = login(i)

	if (can_login):
		target_file = get_file()
		md5_hash = get_MD5_hash(target_file)
		is_valid_hash = validate_hash(md5_hash)

		if (not is_valid_hash):
			print("hash generated from the file is not valid")
			clientSocket.close()
			exit(1)

# ------- SEND REQUEST METHODS ---------------------------------------------------

def request_connection(student_key):
	clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key))

	if (get_response_code() == HANDSHAKE_SUCCESSFUL):
		return true

	return false

def login(password):
	clientSocket.send(create_request_message(LOGIN_REQUEST, password))
	return get_response_code() == LOGIN_SUCCESSFUL

def logout():
	clientSocket.send(create_request_message(LOGOUT_REQUEST))
	return get_response_code() == LOGOUT_SUCCESSFUL

""" returns the file received from server in byte-format """
def get_file():
	clientSocket.send(create_request_message(GET_REQUEST))
	file_size = get_file_size()

	file = clientSocket.recv(file_size)

	if (clientSocket.recv(1024).length != 0):
		print("seems like there are still some bytes to be read; perhaps the file_size in packet header was incorrect");
		clientSocket.close()
		exit(1)		

	return file

def validate_hash(hash):
	clientSocket.send(create_request_message(SEND, hash))
	if (get_response_code() == HASH_MATCHED):
		return true

	return false

# ------- UTIL METHODS -------------------------------------------------------------

def create_request_message(method_code, data=""):
	return (method_code + data).encode();

def get_response_code():
	return clientSocket.recv(4).decode()

""" note: get_file_size() should only be called inside the function get_file() """
def get_file_size():
	# can ignore the status code because
	get_response_code() # can assume always successful according to the FSM

	encodedFileSize = b''
	x = clientSocket.recv(1)

	while (x != b'_'):
		encodedFileSize += x
		x = clientSocket.recv(1)

	return int(encodedFileSize)

def get_MD5_hash(data):
	return str(hashlib.md5(data).hexdigest())
