import numpy as np
import argparse

parser = argparse.ArgumentParser(
                prog='check_gold',
                description='Check the Lego output against the gold input matrix',)

parser.add_argument('--gold', type=str, help='The path to the gold matrix',)

args = parser.parse_args()

gold_mat = np.load(args.gold)

output_mat = np.zeros(gold_mat.shape, dtype=np.float32)
with open("./lego_scratch/data_files/output.txt", "r") as f:
    for i in range(gold_mat.shape[0]):
        for j in range(gold_mat.shape[1]):
            output_mat[i][j] = float(f.readline().strip())

if np.allclose(output_mat, gold_mat, rtol=0.001):
    print("\033[32m=========== OUTPUT MATCHES GOLD ===========\033[0m")
else:  
    print("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")
