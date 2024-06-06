import numpy as np

B = np.load("./lego_scratch/tensor_B/numpy_array.npz")['array1']
C = np.load("./lego_scratch/tensor_C/numpy_array.npz")['array1']

out = np.einsum('ik,kj->ij',B,C)

out = out.reshape(-1)
out_path = "./lego_scratch/gold_output.npz"
np.savez(out_path, array1 = out)
