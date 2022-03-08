from socket import *

s = socket(AF_INET, SOCK_STREAM)
s.connect(("137.132.92.111", 4445))
s.sendall("STID_651723_C".encode())
resp = s.recv(4096).decode()
print(f"resp = {resp}")