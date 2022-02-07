from socket import *
import hashlib
import sys

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

	if (clientSocket.recv(1024).length != 0):
		print("seems like there are still some bytes to be read; perhaps the file_size in packet header was incorrect");
		clientSocket.close()
		exit(1)		

	return file

def request_validate_hash(clientSocket, hash):
	clientSocket.send(create_request_message(SEND, hash))
	if (get_response_code(clientSocket) == HASH_MATCHED):
		return True

	return False

# ------- UTIL METHODS -------------------------------------------------------------

def create_request_message(method_code, data=""):
	request_message = method_code + str(data)
	print("request_message sent: " + request_message)
	return (request_message).encode();

def get_response_code(clientSocket):
	response_code = clientSocket.recv(4).decode();

	while (len(response_code) == 0):
		sleep(1)
		response_code = clientSocket.recv(4).decode();

	print("response_code received: " + response_code)
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

	return int(encodedFileSize)

def generate_MD5_hash(data):
	return str(hashlib.md5(data).hexdigest())

# returns a local socket that is connected to the specified server
def create_socket(student_key):
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((SERVER_IP_ADDRESS, SERVER_PORT))
	can_connect = request_connection(clientSocket, student_key)

	if (not can_connect):
		print("Handshake could not be established due to invalid student id")
		clientSocket.close()
		exit(1)

	return clientSocket


# ------ MAIN ---------------------------------------------------------------

# get student key to establish connection with server
student_key = sys.argv[1]

num_success = 0
last_tried_password = 0 # all possible password combinations (0000-9999)

# request for connection to server
clientSocket = create_socket(student_key)

while (num_success < 8):
	# try to login using all possible password combinations (0000-9999)
	for i in range(last_tried_password, 10000):
		try:
			can_login = request_login(clientSocket, i)
			print("--- tried password: " + str(i)) # FOR DEBUGGING ONLY: see how far we could get

			if (can_login):
				target_file = request_get_file(clientSocket)
				md5_hash = generate_MD5_hash(target_file)
				is_valid_hash = request_validate_hash(clientSocket, md5_hash)

				if (not is_valid_hash):
					print("hash generated from the file is not valid")
					clientSocket.close()
					exit(1)

				num_success += 1
				print("successful file validation")

				request_logout(clientSocket)
				continue

		except ConnectionError:
			last_tried_password = i-1
			clientSocket = create_socket(student_key)








