from socket import *

s = socket(AF_INET, SOCK_STREAM)
s.connect(("137.132.92.111", 4445))
# s.sendall("STID_A0218234L_C".encode())
s.sendall("STID_6517234_C")
resp = s.recv(4096).decode()
print(f"resp = {resp}")