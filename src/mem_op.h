#ifndef MEM_OP_H
#define MEM_OP_H

#include "data_def.h"
#include <fstream>
#include <iostream>
#include <string>
using namespace std;

tile2 tensor_mem_op_2(int **tensor_op, int index);
subtile2 tile_mem_op_2(tile2 tile_op, int index); 
cg_subtile2 cg_tile_mem_op_2(cg_subtile2 cg_subtile_op, int **store_subtile_op, tile2 tile_op, int index, int id_store_op); 
cg_extents2 build_extents_2(cg_extents2 op_extents, int **store_subtile_op, int id_store_op);
int rtl_output_subtile_printer(double *op_vals, int output_subtile_size, int curr_subtile_num, ofstream &output_gold_file);
int rtl_subtile2_print(subtile2 subtile_op, std::string output_path, std::string mode_name, int dim1, int dim2);


#endif