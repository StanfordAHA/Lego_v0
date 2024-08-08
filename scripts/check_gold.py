import numpy as np
import argparse
from sam.util import bfbin2float

parser = argparse.ArgumentParser(
                prog='check_gold',
                description='Check the Lego output against the gold input matrix',)

parser.add_argument('--gold', type=str, help='The path to the gold matrix',)
parser.add_argument('--input', type=str, help='The path to the input matrix',)
parser.add_argument('--bf16', action='store_true', help='Whether the input matrix is in bf16 format',)
parser.add_argument('--dump_numpy', action='store_true', help='Dump the input matrix as a numpy file and ignore check results',)

args = parser.parse_args()

output_mat = None
with open(args.input, "r") as f:
    n_dim = int(f.readline().strip())
    output_dim = []
    for i in range(n_dim):
        output_dim.append(int(f.readline().strip()))
    output_mat = np.zeros(output_dim, dtype=np.float32)
    for idx, val in np.ndenumerate(output_mat):
            output_mat[idx] = float(f.readline().strip())

if args.dump_numpy:
    np_mat_path = args.input.replace(".txt", ".npy")
    np.save(np_mat_path, output_mat)

gold_mat = np.load(args.gold)
if args.bf16:
    gold_fp_mat = np.empty_like(gold_mat, dtype=np.float32)
    for idx, val in np.ndenumerate(gold_mat):
        gold_fp_mat[idx] = bfbin2float(str(val).split("'")[1])
    gold_mat = gold_fp_mat
if np.allclose(output_mat, gold_mat, rtol=0.01):
    print("\033[32m=========== OUTPUT MATCHES GOLD ===========\033[0m")
else:  
    if not args.dump_numpy:
        print(output_mat.shape)
        print(gold_mat.shape)
        print(output_mat)
        print(gold_mat)
        neq = np.where(output_mat != gold_mat)
        for i, idx in enumerate(neq[0]):
            print(f"Index: {idx} {neq[1][i]}, Output: {output_mat[idx][neq[1][i]]}, Gold: {gold_mat[idx][neq[1][i]]}")
        raise ValueError("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")
    else:
        print(output_mat.shape)
        print(gold_mat.shape)
        print(output_mat)
        print(gold_mat)
        print(("\033[31m=========== OUTPUT DOES NOT MATCH GOLD (IGNORED) ===========\033[0m"))
