#!/usr/bin/env python3
import hashlib
import os
import random

# the seed used by rand
import sys

seed = int(sys.argv[1])
random.seed(seed)

# the size of random files being created in MB
size_small = 128
size_large = 512

# crate the data directory
dir_name = os.path.join('test', 'output')
os.makedirs(dir_name, exist_ok=True)
dir_name = os.path.join('test', 'input')
os.makedirs(dir_name, exist_ok=True)


def generate_file(name, size):
    m = 1024 * 1024
    f_name_data = os.path.join(dir_name, name + ".dat")
    f_name_hash = os.path.join(dir_name, name + ".hash")

    flag_create_file = False
    if not os.path.isfile(f_name_hash):
        flag_create_file = True
    elif not os.path.isfile(f_name_data):
        flag_create_file = True
    elif os.path.getsize(f_name_data) != size*m:
        flag_create_file = True

    if flag_create_file:
        print("generating:", f_name_data)

        # generate hash
        md5_hash = hashlib.md5()

        with open(f_name_data, 'wb') as f_out:
            # generating 1 MB data in each iteration
            for _ in range(size):
                data = random.getrandbits(8 * m).to_bytes(m, 'little')
                f_out.write     (data)
                md5_hash.update (data)
        digest = md5_hash.hexdigest()
        with open(f_name_hash, "w") as f_out:
            f_out.write(digest)


generate_file(str(seed)+'_small', size_small)
generate_file(str(seed)+'_large', size_large)
