import numpy as np
import argparse
from sam.util import bfbin2float

parser = argparse.ArgumentParser(
                prog='check_gold',
                description='Check the Lego output against the gold input matrix',)

parser.add_argument('--gold', type=str, help='The path to the gold matrix',)
parser.add_argument('--input', type=str, help='The path to the input matrix',)
parser.add_argument('--bf16', action='store_true', help='Whether the input matrix is in bf16 format',)

args = parser.parse_args()

gold_mat = np.load(args.gold)
if args.bf16:
    gold_fp_mat = np.empty_like(gold_mat, dtype=np.float32)
    for idx, val in np.ndenumerate(gold_mat):
        gold_fp_mat[idx] = bfbin2float(str(val).split("'")[1])
    gold_mat = gold_fp_mat

output_mat = np.zeros(gold_mat.shape, dtype=np.float32)
with open(args.input, "r") as f:
    for i in range(gold_mat.shape[0]):
        for j in range(gold_mat.shape[1]):
            output_mat[i][j] = float(f.readline().strip())

if np.allclose(output_mat, gold_mat, rtol=0.01):
    print("\033[32m=========== OUTPUT MATCHES GOLD ===========\033[0m")
else:  
    print(output_mat.shape)
    print(gold_mat.shape)
    print(output_mat)
    print(gold_mat)
    neq = np.where(output_mat != gold_mat)
    for i, idx in enumerate(neq[0]):
        print(f"Index: {idx} {neq[1][i]}, Output: {output_mat[idx][neq[1][i]]}, Gold: {gold_mat[idx][neq[1][i]]}")
    raise ValueError("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")
