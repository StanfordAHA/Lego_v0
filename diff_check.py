import numpy as np
import argparse

file1 = "lego_scratch/gold_output.npz"
file2 = "lego_scratch/data_files/output.txt"

gold_mat = np.load(file1)['array1']
output_mat = np.zeros(gold_mat.shape, dtype=np.float32)
with open("./lego_scratch/data_files/output.txt", "r") as f:
    for i in range(gold_mat.shape[0]):
            output_mat[i] = float(f.readline().strip())

if np.allclose(output_mat, gold_mat, rtol=0.001):
    print("\033[32m=========== OUTPUT MATCHES GOLD ===========\033[0m")
else:  
    print("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")
