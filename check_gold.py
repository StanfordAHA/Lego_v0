import numpy as np
output_mat = np.zeros((3327, 3327), dtype=np.float32)
with open("./lego_scratch/data_files/output.txt", "r") as f:
    for i in range(3327):
        for j in range(3327):
            output_mat[i][j] = float(f.readline().strip())

gold_mat = np.load("/nobackup/bwcheng/sparse-datasets/sparse-ml/gcn/citeseer/layer1/adj_source_scaling/X.npy")
print(np.allclose(output_mat, gold_mat))
print(output_mat.shape)
print(gold_mat.shape)