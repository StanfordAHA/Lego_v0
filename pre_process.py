import sys
import numpy as np
import scipy.sparse
import scipy.io
import os
import argparse
import ast
import yaml
import copy
import pickle
import random
import sparse
import sys
import math
import pytaco as pt
from pytaco import dense, compressed
import re
from typing import Dict, List

from pathlib import Path

from sam.util import SUITESPARSE_PATH, SuiteSparseTensor, InputCacheSuiteSparse, PydataTensorShifter, ScipyTensorShifter, \
    FROSTT_PATH, FrosttTensor, PydataSparseTensorDumper, InputCacheTensor, constructOtherMatKey, constructOtherVecKey, \
    InputCacheSparseML, SPARSEML_PATH, SparseMLTensor
from sam.sim.src.tiling.process_expr import parse_all
from lassen.utils import float2bfbin, bfbin2float

class PydataSparseTensorDumper:
    def dump(self, coo_tensor, output_path):
        """Write a COO tensor to a .tns file in coordinate format."""
        
        if not isinstance(coo_tensor, sparse.COO):
            raise TypeError("Input tensor must be a pydata/sparse COO tensor")
        
        indices = coo_tensor.coords  # shape (ndim, nnz)
        data = coo_tensor.data  # shape (nnz,)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            for i in range(data.shape[0]):
                index_list = ' '.join(str(indices[dim, i] + 1) for dim in range(indices.shape[0]))  # 1-based index
                f.write(f"{index_list} {data[i]}\n")
        
        print(f"Tensor successfully dumped to {output_path}")

def parse_tiled_tensor(tiled_tensor_str: str) -> Dict[str, List]:
    """
    Parses the tiled_tensor string and extracts compressed sections into pos_i, crd_i lists,
    and extracts the vals list.

    Args:
        tiled_tensor_str (str): The string representation of the tiled tensor.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'compressed': A dictionary where each key is the compressed index (i),
                           and the value is another dictionary with 'pos_i' and 'crd_i' lists.
            - 'vals': The vals list extracted from the string.
    """
    compressed_pattern = r'compressed\s*\((\d+)\):\s*\[\s*([^\]]*?)\s*\]\s*\[\s*([^\]]*?)\s*\]'
    compressed_matches = re.findall(compressed_pattern, tiled_tensor_str, re.DOTALL | re.IGNORECASE)

    compressed_data = {}

    for match in compressed_matches:
        index = int(match[0])

        pos_i_str = match[1]
        pos_i = [int(num.strip()) for num in pos_i_str.replace('\n', '').split(',') if num.strip()]

        crd_i_str = match[2]
        crd_i = [int(num.strip()) for num in crd_i_str.replace('\n', '').split(',') if num.strip()]

        compressed_data[index] = {
            'pos': pos_i,
            'crd': crd_i
        }

    # Now, extract the 'vals' list.
    # Assume 'vals' is the last list in the string not associated with any compressed(i)
    # First, find all lists in the string
    list_pattern = r'\[\s*([\d,\s]+?)\s*\]'
    all_lists = re.findall(list_pattern, tiled_tensor_str, re.DOTALL)

    # Extract lists associated with compressed(i)
    associated_lists = []
    for match in compressed_matches:
        associated_lists.append(match[1])  # pos_i
        associated_lists.append(match[2])  # crd_i

    # Find lists that are not associated with compressed(i)
    vals_candidates = []
    for lst in all_lists:
        if lst not in associated_lists:
            # To ensure it's not part of other sections like 'dense', you might need additional checks
            # For simplicity, we'll assume the last unmatched list is 'vals'
            vals_candidates.append(lst)

    if vals_candidates:
        vals_str = vals_candidates[-1]  # Assuming the last unmatched list is 'vals'
        vals = [int(num.strip()) for num in vals_str.replace('\n', '').split(',') if num.strip()]
    else:
        vals = []

    return {
        'compressed': compressed_data,
        'vals': vals
    }


def process_coo(tensor, tile_dims, output_dir_path, format, schedule_dict, positive_only, dtype, data_format):
    
    ''' 
    This is the main function that is called to tile and store as CSF
    Inputs: 
    tensor: The input tensor in COO format
    tile_dims: The dimensions of the tiles at each level
    output_dir_path: The path to the output directory to store the CSF tiles
    '''
    
    # The input tensor is a COO tensor

    coords = []
    data = []

    if format == "s": 
        coords = tensor.coords
        data = tensor.data
    # if the input format is dense, we need to fill in all the zero entries
    elif format == "d":
        n_dim = len(tensor.coords)
        for i in range(n_dim):
            coords.append([])
        for idx, val in np.ndenumerate(tensor.todense()):
            for i in range(n_dim):
                coords[i].append(idx[i])
            data.append(val)
    else:
        raise ValueError("Format must be either \"s\" or \"d\"")

    # The number of values in the tensor
    num_values = len(data)
    n_dim = len(coords)

    # The number of dimensions in the tensor
    n_dim = len(coords)

    # The number of levels of tiling
    n_levels = len(tile_dims)

    # Create n_levels * n_dim lists to store the coordinates and data
    n_lists = np.zeros(((n_levels + 1) * n_dim, num_values), dtype=int)
    if dtype == "int":
        d_list = np.zeros((num_values), dtype=int)
    else:
        d_list = np.zeros((num_values), dtype=float)

    # Creating the COO representation for the tiled tensor at each level
    for i in range(num_values):
        d_list[i] = abs(data[i])
        for level in range(n_levels):
            for dim in range(n_dim):

                crd_dim = schedule_dict[level][dim] 
                nxt_dim = schedule_dict[level + 1].index(crd_dim)

                idx1 = level * n_dim + dim
                idx2 = (level + 1) * n_dim + nxt_dim

                if(level == 0):
                    n_lists[idx1][i] = coords[crd_dim][i] // tile_dims[level][crd_dim]
                    n_lists[idx2][i] = coords[crd_dim][i] % tile_dims[level][crd_dim]
                else:
                    n_lists[idx1][i] = n_lists[idx1][i] // tile_dims[level][crd_dim]
                    n_lists[idx2][i] = coords[crd_dim][i] % tile_dims[level][crd_dim]
    
    tiled_COO = sparse.COO(n_lists, d_list)

    """

    # Write the tiled COO as .tns file
    dumper = PydataSparseTensorDumper()
    dumper.dump(tiled_COO, output_dir_path + "/tiled_tensor.tns")

    # Create the custom tiled tensor

    for i in range(len(data_format)):
        if data_format[i] == "s":
            data_format[i] = compressed
        else:
            data_format[i] = dense

    taco_tensor = pt.read(output_dir_path + "/tiled_tensor.tns", pt.format(data_format))
    internal_tensor = taco_tensor._tensor
    tiled_dict = parse_tiled_tensor(str(internal_tensor))

    for keys in tiled_dict['compressed'].keys():
        if keys != None:
            pos_path = output_dir_path + "/tcsf_pos" + str(keys + 1) + ".txt"
            with open(pos_path, 'w+') as f:
                for item in tiled_dict['compressed'][keys]['pos']:
                    f.write("%s\n" % item)
            crd_path = output_dir_path + "/tcsf_crd" + str(keys + 1) + ".txt"
            with open(crd_path, 'w+') as f:
                for item in tiled_dict['compressed'][keys]['crd']:
                    f.write("%s\n" % item)
    
    # print(output_dir_path)
    # if output_dir_path == "./lego_scratch/tensor_B":
    #    print(tiled_dict['vals'])
    d_list_path = output_dir_path + "/tcsf_vals" + ".txt"
    with open(d_list_path, 'w+') as f:
        for item in tiled_dict['vals']:
            f.write("%s\n" % item)

    # tiled_coo.coords holds the COO coordinates for each level
    # tiled_coo.data holds the data for each level

    """

    # Create the CSF representation for the tensor at each level
    crd_dict = {} 
    pos_dict = {}

    pos_ctr = np.ones(((n_levels + 1) * n_dim), dtype=int)
 
    for i in range(num_values):   
        propogate = 0; 
        for level in range(n_levels + 1):
            for dim in range(n_dim):
                idx = level * n_dim + dim
                if(i == 0): 
                    crd_dict[idx] = [tiled_COO.coords[idx][i]]
                    pos_dict[idx] = [0] 
                else:
                    if(crd_dict[idx][-1] != tiled_COO.coords[idx][i]):
                        propogate = 1

                    if(propogate == 1):
                        pos_ctr[idx] += 1
                        crd_dict[idx].append(tiled_COO.coords[idx][i])
                        if(idx != n_levels * n_dim + n_dim - 1):
                            pos_dict[idx + 1].append(pos_ctr[idx + 1])
                     
    for level in range(n_levels + 1):
        for dim in range(n_dim):
            idx = level * n_dim + dim
            if(idx == 0):
                pos_dict[idx].append(pos_ctr[idx])
            if(idx != n_levels * n_dim + n_dim - 1):
                pos_dict[idx + 1].append(pos_ctr[idx + 1])

    # Write the CSF representation to disk
    for level in range(n_levels + 1):
        for dim in range(n_dim):
            crd_dict_path = output_dir_path + "/tcsf_crd" + str(level * n_dim + dim + 1) + ".txt"
            with open(crd_dict_path, 'w+') as f:
                for item in crd_dict[level * n_dim + dim]:
                    f.write("%s\n" % item)
            pos_dict_path = output_dir_path + "/tcsf_pos" + str(level * n_dim + dim + 1) + ".txt"
            with open(pos_dict_path, 'w+') as f:
                for item in pos_dict[level * n_dim + dim]:
                    f.write("%s\n" % item)
    
    d_list_path = output_dir_path + "/tcsf_vals" + ".txt"
    with open(d_list_path, 'w+') as f:
        for val in range(num_values):
            if(dtype == "int"):
                if positive_only:
                    f.write("%s\n" % (abs(int(tiled_COO.data[val]))))
                else:
                    f.write("%s\n" % (int(tiled_COO.data[val])))
            else:   
                f.write("%s\n" % (tiled_COO.data[val]))                
    return n_lists, d_list, crd_dict, pos_dict
    

def write_csf(COO, output_dir_path): 

    # The number of values in the tensor
    num_values = len(COO.data)
    n_dim = len(COO.coords)

    # Create the CSF representation for the tensor at each level
    crd_dict = {} 
    pos_dict = {}

    pos_ctr = np.ones(n_dim, dtype=int)
 
    for i in range(num_values):   
        propogate = 0; 
        for dim in range(n_dim):
            idx = dim
            if(i == 0): 
                crd_dict[idx] = [COO.coords[idx][i]]
                pos_dict[idx] = [0] 
            else:
                if(crd_dict[idx][-1] != COO.coords[idx][i]):
                    propogate = 1

                if(propogate == 1):
                    pos_ctr[idx] += 1
                    crd_dict[idx].append(COO.coords[idx][i])
                    if(idx != n_dim - 1):
                        pos_dict[idx + 1].append(pos_ctr[idx + 1])
                     
    for dim in range(n_dim):
        idx = dim
        if(idx == 0):
            pos_dict[idx].append(pos_ctr[idx])
        if(idx != n_dim - 1):
            pos_dict[idx + 1].append(pos_ctr[idx + 1])

    for dim in range(n_dim):
        crd_dict_path = output_dir_path + "/csf_crd" + str(dim + 1) + ".txt"
        with open(crd_dict_path, 'w+') as f:
            for item in crd_dict[dim]:
                f.write("%s\n" % item)
        pos_dict_path = output_dir_path + "/csf_pos" + str(dim + 1) + ".txt"
        with open(pos_dict_path, 'w+') as f:
            for item in pos_dict[dim]:
                f.write("%s\n" % item)
    
    d_list_path = output_dir_path + "/csf_vals" + ".txt"
    with open(d_list_path, 'w+') as f:
        for val in range(num_values):
            f.write("%s\n" % (COO.data[val]))

inputCacheSuiteSparse = InputCacheSuiteSparse()
inputCacheTensor = InputCacheTensor()

def process(tensor_type, input_path, output_dir_path, tensor_size, schedule_dict, format, gen_tensor, density, gold_check, positive_only, dtype, data_format):

    tensor = None
    cwd = os.getcwd()
    inputCache = None

    other_nonempty = True

    if tensor_type == "gen":
        # Generating a random tensor for testing purposes of pre-processing kernel 
        size = tuple(tensor_size[0])
        tensor = None
        # TODO: Parameterize this
        np.random.seed(0)
        if dtype == "int":
            value_cap = 10
            tensor = np.random.randint(low=-1 * value_cap / 2, high = value_cap / 2, size=size)
        else:
            value_cap = 10
            tensor = np.random.uniform(low=-1 * value_cap / 2, high = value_cap / 2, size=size)
            if dtype == "bf16":
                for idx, val in np.ndenumerate(tensor):
                    tensor[idx] = bfbin2float(float2bfbin(val))
        num_zero = int(np.prod(tensor.shape) * (1 - density / 100))
        zero_indices = np.random.choice(np.prod(tensor.shape), num_zero, replace=False)
        tensor[np.unravel_index(zero_indices, tensor.shape)] = 0
        # tensor = scipy.sparse.coo_array(tensor)
        # tensor = sparse.COO(tensor)
    elif tensor_type == "ex":
        # Reading an extensor tensor for testing purposes of pre-processing kernel
        tensor = scipy.io.mmread(input_path)
    elif tensor_type == "ss":
        # Reading a SuiteSparse tensor for testing purposes of pre-processing kernel
        inputCache = inputCacheSuiteSparse
        tensor_path = os.path.join(SUITESPARSE_PATH, input_path + ".mtx")
        ss_tensor = SuiteSparseTensor(tensor_path)
        tensor = inputCache.load(ss_tensor, False)
    elif tensor_type == "frostt":
        # Reading a FROSTT tensor for testing purposes of pre-processing kernel
        inputCache = inputCacheTensor
        tensor_path = os.path.join(FROSTT_PATH, input_path + ".tns")
        frostt_tensor = FrosttTensor(tensor_path)
        tensor = inputCache.load(frostt_tensor, False)
    elif tensor_type == "sparse_ml":
        inputCache = InputCacheSparseML()
        tensor_path = os.path.join(SPARSEML_PATH, input_path + ".npy")
        sparse_ml_tensor = SparseMLTensor(tensor_path)
        tensor = inputCache.load(sparse_ml_tensor, False)
    else:
       raise ValueError("This choice of 'tensor_type' is unreachable")

    if gen_tensor == "transpose":
        tensor = tensor.transpose()
    elif gen_tensor == "shift_dim2":
        shifted = ScipyTensorShifter().shiftLastMode(tensor)
        tensor = shifted
    elif gen_tensor == "shift_transpose_dim2": 
        shifted = ScipyTensorShifter().shiftLastMode(tensor)
        tensor = shifted.transpose()
    elif gen_tensor == "onyx_matmul": 
        shifted = ScipyTensorShifter().shiftLastMode(tensor)
        tensor = shifted.transpose()

        tensor = sparse.COO(tensor)
        num_values = len(tensor.data)

        tile_op_crd_list = np.zeros((2, num_values), dtype=int)
        tile_op_val_list = []
        
        for idx in range(0, num_values):

            i = tensor.coords[0][idx]
            j = tensor.coords[1][idx]
   
            crd_i = i%30
            crd_j = j%30

            ii = i - crd_i + crd_j
            jj = j - crd_j + crd_i  

            tile_op_crd_list[0][idx] = ii 
            tile_op_crd_list[1][idx] = jj
            tile_op_val_list.append(tensor.data[idx])
        
        tensor = sparse.COO(tile_op_crd_list, tile_op_val_list)
        
    elif gen_tensor == "shift_twice_dim2":
        shifted = ScipyTensorShifter().shiftLastMode(tensor)
        shifted2 = ScipyTensorShifter().shiftLastMode(shifted)
        tensor = shifted2
    elif gen_tensor == "gen_colvec_dim1":
        rows, cols = tensor.shape
        tensor_c = scipy.sparse.random(cols, 1, data_rvs=np.ones).toarray().flatten()
        if other_nonempty: tensor_c[0] = 1
        tensor = tensor_c
    elif gen_tensor == "gen_rowvec_dim1":
        rows, cols = tensor.shape
        tensor_c = scipy.sparse.random(rows, 1, data_rvs=np.ones).toarray().flatten()
        if other_nonempty: tensor_c[0] = 1 
        tensor = tensor_c
    elif gen_tensor == "shift_dim3": 
        shifted = PydataTensorShifter().shiftLastMode(tensor)
        tensor = shifted
    elif gen_tensor == "tensor3_ttv":
        tensorName = input_path
        variant = "mode2"  
        path = constructOtherVecKey(tensorName, variant)
        tensor_c_loader = FrosttTensor(path)
        tensor_c = tensor_c_loader.load().todense()
        size_i, size_j, size_k = tensor.shape  # i,j,k
        tensor_c = scipy.sparse.random(size_k, 4, data_rvs=np.ones).toarray().flatten()
        if other_nonempty:
            tensor_c[0] = 1
        tensor = tensor_c   
    elif gen_tensor == "tensor3_ttm":
        tensorName = input_path
        variant = "mode2_ttm"
        path = constructOtherMatKey(tensorName, variant)
        matrix_c_loader = FrosttTensor(path)
        matrix_c = matrix_c_loader.load().todense()
        # size_i, size_j, size_l = tensor.shape  # i,j,k
        # print("OTHER SIZES: ", size_i, size_j, size_l)
        # # dimension_k = random.randint(min(tensor.shape), 10)
        # dimension_k = 3
        # tensor_c = scipy.sparse.random(dimension_k, size_l, density=0.25, data_rvs=np.ones).toarray()
        # tensor_c = scipy.sparse.random(dimension_k, size_l, data_rvs=np.ones).toarray().flatten()
        if other_nonempty:
            matrix_c[0] = 1
        tensor = matrix_c
    elif gen_tensor == "tensor3_mttkrp1":
        size_i, size_j, size_l = tensor.shape  
        tensorName = input_path
        variant = "mode1_mttkrp"
        path = constructOtherMatKey(tensorName, variant)
        matrix_c_loader = FrosttTensor(path)
        matrix_c = matrix_c_loader.load().todense()
        if other_nonempty:
            matrix_c[0] = 1
        tensor = matrix_c
    elif gen_tensor == "tensor3_mttkrp2":
        size_i, size_j, size_l = tensor.shape
        tensorName = input_path
        variant = "mode2_mttkrp"
        path = constructOtherMatKey(tensorName, variant)
        matrix_d_loader = FrosttTensor(path)
        matrix_d = matrix_d_loader.load().todense()
        # size_k = random.randint(min(tensor.shape), 10)
        # # C & D are dense according to TACO documentation
        # matrix_c = scipy.sparse.random(size_j, size_k, density=1, data_rvs=np.ones).toarray()
        # matrix_d = scipy.sparse.random(size_j, size_l, density=1, data_rvs=np.ones).toarray()
        if other_nonempty:
            matrix_d[0] = 1
        tensor = matrix_d
    elif gen_tensor != "0":
        raise NotImplementedError

    tensor = sparse.COO(tensor)

    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    if(gold_check == "d"):
        dense_tensor = tensor.todense()
        numpy_array = np.array(dense_tensor)
        out_path = output_dir_path + "/numpy_array" + ".npz"
        np.savez(out_path, array1 = numpy_array)
    elif(gold_check == "s"):
        size = tensor_size[0]
        write_csf(tensor, output_dir_path)

    tile_size = tensor_size[1:]
    process_coo(tensor, tile_size, output_dir_path, format, schedule_dict, positive_only, dtype, data_format)
