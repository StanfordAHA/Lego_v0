import numpy as np
import argparse
import torch
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

input_mat = np.load(args.input)

gold = torch.from_numpy(gold_mat).max(1, keepdim=True)[1]
input = torch.from_numpy(input_mat).max(1, keepdim=True)[1]

if torch.equal(input, gold):
    print("\033[32m=========== OUTPUT MATCHES GOLD ===========\033[0m")
else:
    print("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")
    print(input)
    print(gold)
    raise ValueError("\033[31m=========== OUTPUT DOES NOT MATCH GOLD ===========\033[0m")

