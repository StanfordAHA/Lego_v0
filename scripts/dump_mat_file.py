import toml
import argparse
import numpy as np 
import scipy
import os
import struct
from lassen.utils import float2bfbin

parser = argparse.ArgumentParser(
                prog='dump_mat_file',
                description='Matlab matrix fomat dumping file for the dense hardware',)
parser.add_argument("--tile_list", type=str, help="The path to the tile list file")
args = parser.parse_args()

input_name  = "B"
kernel_name = "C"
tile_path = os.path.dirname(args.tile_list)


with open(args.tile_list, "r") as f:
    tile_list_dict = toml.load(f)
    tile_pairs_list = tile_list_dict["sam_config"]["sam_path"]


for tile_pair in tile_pairs_list:
    input_shape_file = f"tensor_{input_name}_mode_shape"
    input_shape = []
    with open(os.path.join(tile_path, tile_pair, input_shape_file), "r") as f:
        for line in f:
            input_shape.append(int(line.strip()))

    input_tensor = np.zeros(input_shape, dtype=np.uint16)
    input_vals_file = f"tensor_{input_name}_mode_vals"
    i = 0
    j = 0
    with open(os.path.join(tile_path, tile_pair, input_vals_file), "r") as f:
        for line in f:
            data = float(line.strip())
            data_bin = float2bfbin(data)
            input_tensor[i][j] = int(data_bin, 2)
            j += 1
            if j == input_shape[1]:
                j = 0
                i += 1

    kernel_shape_file = f"tensor_{kernel_name}_mode_shape"
    kernel_shape = []
    with open(os.path.join(tile_path, tile_pair, kernel_shape_file), "r") as f:
        for line in f:
            kernel_shape.append(int(line.strip()))
    
    kernel_tensor = np.zeros(kernel_shape, dtype=np.uint16)
    kernel_vals_file = f"tensor_{kernel_name}_mode_vals"
    i = 0
    j = 0
    with open(os.path.join(tile_path, tile_pair, kernel_vals_file), "r") as f:
        for line in f:
            data = float(line.strip())
            data_bin = float2bfbin(data)
            kernel_tensor[j][i] = int(data_bin, 2)
            j += 1
            if j == kernel_shape[0]:
                j = 0
                i += 1

    output_shape_file = "tensor_out_mode_shape"
    output_shape = []
    with open(os.path.join(tile_path, tile_pair, output_shape_file), "r") as f:
        for line in f:
            output_shape.append(int(line.strip()))

    output_tensor = np.zeros(output_shape, dtype=np.uint16)
    output_vals_file = f"output_gold.h"
    i = 0
    j = 0
    with open(os.path.join(tile_path, tile_pair, output_vals_file), "r") as f:
        for line in f:
            data = float(line.strip())
            data_bin = float2bfbin(data)
            output_tensor[i][j] = int(data_bin, 2)
            j += 1
            if j == output_shape[1]:
                j = 0
                i += 1
    input_tensor = np.transpose(input_tensor)
    kernel_tensor = np.transpose(kernel_tensor)
    output_tensor = np.transpose(output_tensor)
    scipy.io.savemat(f"{tile_path}/{tile_pair}/input_host_stencil.mat", {"input_host_stencil": input_tensor})
    scipy.io.savemat(f"{tile_path}/{tile_pair}/kernel_host_stencil.mat", {"kernel_host_stencil": kernel_tensor})
    scipy.io.savemat(f"{tile_path}/{tile_pair}/hw_output.mat", {"hw_output": output_tensor})
