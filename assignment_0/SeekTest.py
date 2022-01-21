import sys

def main():
	data = sys.stdin.buffer.read1(-1)
	print(int(data[0:2]))
	

		
if __name__ == "__main__":
	main()

# Max header-case:
	# 	"Size: 1048576B"