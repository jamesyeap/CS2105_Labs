#!/usr/bin/env python3
import os
import random

# the seed used by rand
import sys

seed = int(sys.argv[1])
random.seed(seed)

# the size of random files being created in MB
if seed == 0 or seed == 2:
    size_small = 128
    size_large = 512
else:
    size_small = 8
    size_large = 16

# crate the data directory
dir_name_data = os.path.join('test', 'output')
os.makedirs(dir_name_data, exist_ok=True)
dir_name_data = os.path.join('test', 'input')
os.makedirs(dir_name_data, exist_ok=True)


def generate_file(name, size):
    f_name = os.path.join(dir_name_data, name + ".dat")
    if not os.path.isfile(f_name):
        print("generating:", f_name)

        with open(f_name, 'wb') as f_out:
            # generating 1 MB data in each iteration
            m = 1024 * 1024
            for _ in range(size):
                data = random.getrandbits(8 * m).to_bytes(m, 'little')
                f_out.write(data)


generate_file(str(seed)+'_small', size_small)
generate_file(str(seed)+'_large', size_large)
