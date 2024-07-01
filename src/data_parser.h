#ifndef DATA_PARSER_H
#define DATA_PARSER_H

#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <boost/format.hpp>
using namespace std;

int build_vec(std::vector<int> &vec, std::string file_path);
int build_vec_val(std::vector<double> &vec, std::string file_path);
int mode_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> mode_0);
int val_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<double> mode_0, std::string dtype);
int extent_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> extents_mode_0);
int rtl_mode_data_printer(std::vector<int> mode_0, std::string output_path, std::string tensor_name, std::string mode_type, std::string mode_name);
int rtl_vals_data_printer(std::vector<double> mode_0, std::string output_path, std::string tensor_name);
int rtl_size_data_printer_1(std::string output_path, std::string tensor_name, int dim1);
int rtl_size_data_printer_2(std::string output_path, std::string tensor_name, int dim1, int dim2);
int rtl_size_data_printer_3(std::string output_path, std::string tensor_name, int dim1, int dim2, int dim3);
int output_subtile_printer(double *op_vals, int output_subtile_size, int curr_subtile_num, ofstream &output_gold_file, std::string dtype);
int subtile_paths_printer(const std::vector<std::string> & subtile_paths, const int &batch_size);
int header_check_gold(ofstream &output_gold_file, int output_subtile_size);
int header_subtile_dim_decl(ofstream &header_file, int dim_id, int dim_size);
int codegen_check_gold_head(ofstream &output_gold_file, int max_run, int tensor_dim);
int codegen_check_gold_tail(ofstream &output_gold_file, int max_run, int tensor_dim);
int codegen_check_gold_outmap(ofstream &output_gold_file, std::string base_id, std::string tile_id);
int header_meta_data(ofstream &header_file, int max_run);
#endif