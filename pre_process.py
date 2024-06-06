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

from pathlib import Path

from sam.util import SUITESPARSE_PATH, SuiteSparseTensor, InputCacheSuiteSparse, PydataTensorShifter, ScipyTensorShifter, \
    FROSTT_PATH, FrosttTensor, PydataSparseTensorDumper, InputCacheTensor, constructOtherMatKey, constructOtherVecKey
# InputCacheSparseML, SPARSEML_PATH, SparseMLTensor
from sam.sim.src.tiling.process_expr import parse_all

def process_coo(tensor, tile_dims, output_dir_path, format, schedule_dict):
    
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
    d_list = np.zeros((num_values), dtype=np.float32)

    # Creating the COO representation for the tiled tensor at each level
    for i in range(num_values):
        d_list[i] = data[i] 
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

    # tiled_coo.coords holds the COO coordinates for each level
    # tiled_coo.data holds the data for each level

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
            f.write("%s\n" % (tiled_COO.data[val]))
                
    return n_lists, d_list, crd_dict, pos_dict

inputCacheSuiteSparse = InputCacheSuiteSparse()
inputCacheTensor = InputCacheTensor()

def process(tensor_type, input_path, output_dir_path, tensor_size, schedule_dict, format, transpose, nnz, gold_check):

    tensor = None
    cwd = os.getcwd()
    inputCache = None

    if tensor_type == "gen":
        # Generating a random tensor for testing purposes of pre-processing kernel 
        size = tuple(tensor_size[0])
        nnz = int(np.prod(size) * nnz / 100)
        tensor = sparse.COO(sparse.random(size, nnz=nnz))
    elif tensor_type == "ex":
        # Reading an extensor tensor for testing purposes of pre-processing kernel
        tensor = scipy.io.mmread(input_path)
        tensor = sparse.COO(tensor)
    elif tensor_type == "ss":
        # Reading a SuiteSparse tensor for testing purposes of pre-processing kernel
        inputCache = inputCacheSuiteSparse
        tensor_path = os.path.join(SUITESPARSE_PATH, input_path + ".mtx")
        ss_tensor = SuiteSparseTensor(tensor_path)
        tensor = inputCache.load(ss_tensor, False)
        tensor = sparse.COO(tensor)
    elif tensor_type == "frostt":
        # Reading a FROSTT tensor for testing purposes of pre-processing kernel
        inputCache = inputCacheTensor
        tensor_path = os.path.join(FROSTT_PATH, input_path + ".tns")
        frostt_tensor = FrosttTensor(tensor_path)
        tensor = inputCache.load(frostt_tensor, False)
        tensor = sparse.COO(tensor)
    elif tensor_type == "sparse_ml":
        inputCache = InputCacheSparseML()
        tensor_path = os.path.join(SPARSEML_PATH, input_path + ".npy")
        sparse_ml_tensor = SparseMLTensor(tensor_path)
        tensor = inputCache.load(sparse_ml_tensor, False)
        tensor = sparse.COO(tensor)
    else:
       raise ValueError("This choice of 'tensor_type' is unreachable")

    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    if(gold_check == "d"):
        dense_tensor = tensor.todense()
        numpy_array = np.array(dense_tensor)
        out_path = output_dir_path + "/numpy_array" + ".npz"
        np.savez(out_path, array1 = numpy_array)
    elif(gold_check == "s"):
        pass  

    tile_size = tensor_size[1:]
    process_coo(tensor, tile_size, output_dir_path, format, schedule_dict)

