import pre_process
import codegen
import sys
import argparse

sys.path.insert(0, './')
sys.path.insert(0, './sam')

from pyparsing import Word, alphas, one_of, alphanums

def tensor_path_type_dict(tensor_path_input):

    tensor_path_dict = {}
    tensor_type_dict = {}
    tensor_transpose_dict = {}

    tensor_path_dict_keys = [] 

    with open(tensor_path_input, 'r') as f:
        data = f.read().splitlines()    
    
    data = [i for i in data]
    data = [i.replace(" ", "") for i in data]


    data = [i for i in data]
    data = [i.replace(" ", "") for i in data]

    for i in range(0, len(data)):
        parsed_data = data[i].split(":")
        tensor_type_dict[parsed_data[0]] = parsed_data[1]
        tensor_path_dict[parsed_data[0]] = parsed_data[2]   
        tensor_transpose_dict[parsed_data[0]] = parsed_data[3]

    return tensor_path_dict, tensor_type_dict, tensor_transpose_dict

def data_parser(data):

    data = [i.replace(" ", "") for i in data]

    arith_op = one_of("+ - * /")

    num_op_rule = Word(alphas) + ":" + Word(alphanums)
    num_op = num_op_rule.parseString(data[0])[2]
    # TODO this seems to only support 2 or 3 operands
    # need to generalize this
    if(num_op == '2'):
        expr_rule = Word(alphas) + ":" + Word(alphas) + '(' + Word(alphas) + ')' +  '=' + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')' 

        expr = expr_rule.parseString(data[1])
        dest = {}
        dest[expr[2]] = list(expr[4])

        op_list =  []
        op_list.append(list(expr[7]))
        op_list.append(list(expr[11]))
        op_list.append(list(expr[12]))

        op = {}
        op[expr[7]] = list(expr[9])
        op[expr[12]] = list(expr[14])
    else:
        expr_rule = Word(alphas) + ":" + Word(alphas) + '(' + Word(alphas) + ')' +  '=' + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')'

        expr = expr_rule.parseString(data[1])
        dest = {}
        dest[expr[2]] = list(expr[4])

        op_list = []
        op_list.append(list(expr[7]))
        op_list.append(list(expr[11]))
        op_list.append(list(expr[12]))
        op_list.append(list(expr[16]))
        op_list.append(list(expr[17]))

        op = {}
        op[expr[7]] = list(expr[9])
        op[expr[12]] = list(expr[14])
        op[expr[17]] = list(expr[19])
        

    schedule_rule = Word(alphanums) + "_" + Word(alphanums) + ':' + '[' + Word(alphas) + ']'

    schedule_1 = list((schedule_rule.parseString(data[2]))[5])
    schedule_2 = list((schedule_rule.parseString(data[3]))[5])
    schedule_3 = list((schedule_rule.parseString(data[4]))[5])

    num_ids = len(schedule_1)

    split_factor_rule = Word(alphas) + ':split:' + Word(alphanums) + ':' + Word(alphanums) + ':' + Word(alphanums)

    split_factor = {}

    for i in range(num_ids):
        parsed_split = split_factor_rule.parseString(data[5 + i])
        split_factor[parsed_split[0]] = [int(parsed_split[2]), int(parsed_split[4]), int(parsed_split[6])]

    return num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor

def parse(input_file, level):

    with open(input_file, 'r') as f:
        data = f.read().splitlines()
    num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor= data_parser(data)

    if(level == "ap"): 
        schedule = schedule_1
        for id in split_factor:
            split_factor[id].pop()
    elif(level == "cp"):
        schedule = schedule_2
        for id in split_factor:
            split_factor[id].pop(0)
    else:
        schedule = schedule_3
        for id in split_factor:
            split_factor[id].pop(0)
    dest_id = {}
    dest_map = {}

    source_id = {}
    source_map = {}

    for tensor in op:
        source_id[tensor] = []
        source_map[tensor] = []

    for tensor in dest:
        dest_id[tensor] = []
        dest_map[tensor] = []

    for tensor in op:
        for id in schedule: 
            if id in op[tensor]:
                source_id[tensor].append(id)
                source_map[tensor].append(op[tensor].index(id)) 

    for tensor in dest:
        for id in schedule:
            if id in dest[tensor]:
                dest_id[tensor].append(id)
                dest_map[tensor].append(dest[tensor].index(id))
    # TODO: this only handles 2 or 3 operands
    # need to generalize this
    if(num_op == "3"):
        expr = "((" + op_list[0][0] + " " + op_list[1][0] + " " + op_list[2][0] + ") " + op_list[3][0] + " " + op_list[4][0] + ")"
        op_list = [op_list[0][0], op_list[2][0], op_list[4][0]]
    elif(num_op == "2"): 
        expr = "(" + op_list[0][0] + " " + op_list[1][0] + " " + op_list[2][0] + ")"
        op_list = [op_list[0][0], op_list[2][0]]

    return dest, op, dest_id, dest_map, source_id, source_map, expr, split_factor, op_list, schedule

def ap_tensor_decleration(main_file, ap_source_id):

    for key, value in ap_source_id.items():

        tensor_dim = len(value)

        main_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            main_file.write("    " + "std::vector<int> " + key + str(i + 1) + "_pos"  + ";\n")
            main_file.write("    " + "std::vector<int> " + key + str(i + 1) + "_crd"  + ";\n")

        main_file.write("    " + "std::vector<double> " + key + "_vals;\n")

        main_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            main_file.write("    " + "build_vec(" + key + str(i + 1) +  "_pos, " + "\"lego_scratch/tensor_" + key + "/tcsf_pos" + str(i + 1) + ".txt\");\n")
            main_file.write("    " + "build_vec(" + key + str(i + 1) +  "_crd, " + "\"lego_scratch/tensor_" + key + "/tcsf_crd" + str(i + 1) + ".txt\");\n")

        main_file.write("    " + "build_vec_val(" + key + "_vals, " + "\"lego_scratch/tensor_" + key + "/tcsf_vals.txt\");\n")
        
        main_file.write("\n")

        main_file.write("    " + "int **tensor_" + key + ";\n")
        main_file.write("    " + "tensor_" + key + " = (int**)malloc(sizeof(int*) * (" + str(6 * tensor_dim + 1) + "));\n")

        main_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            main_file.write("    " + "tensor_" + key + "[" + str(2 * i) + "] = " + key + str(i + 1) + "_pos.data();\n")
            main_file.write("    " + "tensor_" + key + "[" + str(2 * i + 1) + "] = " + key + str(i + 1) + "_crd.data();\n")

        main_file.write("    " + "tensor_" + key + "[" + str(6 * tensor_dim) + "] = (int *)" + key + "_vals.data();\n")
    
        main_file.write("\n")

        main_file.write("    " + "tile" + str(tensor_dim) + " tile_" + key + ";\n"); 

    main_file.write("\n")  
    main_file.write("    " + "std::string tile_name;")
    main_file.write("\n")

def cp_tensor_decleration(main_file, cp_source_id, split_dict, mode):

    for key, value in cp_source_id.items():

        tensor_dim = len(value)
        main_file.write("\n")

        for i in range(0, 2 * tensor_dim):
            main_file.write("    " + "int *" + key + str(i + 1) + "_pos = tile_" + key + ".pos" + str(i + 1) + ".data();\n")
            main_file.write("    " + "int *" + key + str(i + 1) + "_crd = tile_" + key + ".crd" + str(i + 1) + ".data();\n")

        main_file.write("    " + "double *" + key + "_vals = tile_" + key + ".vals.data();" + "\n")
        main_file.write("\n")

        main_file.write("    " + "subtile" + str(tensor_dim) + " subtile_" + key + ";\n")

        main_file.write("\n")

        if(mode != 'rtl'):

            total_size = 1
            for id in cp_source_id[key]:
                total_size *= int(split_dict[id][0]/split_dict[id][1])

            main_file.write("    " + "int store_size_" + key + " = " + str(total_size) + ";\n")
            main_file.write("    " + "int id_store_" + key + ";\n")
            main_file.write("\n")

            main_file.write("    " + "bool *store_" + key + " = (bool *) calloc((store_size_" + key + " + 1), sizeof(bool));\n")

            for i in range(0, tensor_dim):
                main_file.write("    " + "int *" + key + "_mode" + str(i) + "_start = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
                main_file.write("    " + "int *" + key + "_mode" + str(i) + "_end = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
            
            main_file.write("    " + "int *" + key + "_mode_vals_start = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
            main_file.write("    " + "int *" + key + "_mode_vals_end = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
        
            main_file.write("\n")
            main_file.write("    " + "int **store_subtile_" + key + ";\n")
            main_file.write("    " + "store_subtile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(2 * tensor_dim + 2) + "));\n")

            for i in range(0, tensor_dim):
                main_file.write("    " + "store_subtile_" + key + "[" + str(2 * i) + "] = " + key + "_mode" + str(i) + "_start;\n")
                main_file.write("    " + "store_subtile_" + key + "[" + str(2 * i + 1) + "] = " + key + "_mode" + str(i) + "_end;\n")

            main_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim) + "] = " + key + "_mode_vals_start;\n")
            main_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim + 1) + "] = " + key + "_mode_vals_end;\n")

            main_file.write("\n")

            main_file.write("    " + "cg_subtile" + str(tensor_dim) + " cg_subtile_" + key + ";\n")
            main_file.write("    " + "cg_extents" + str(tensor_dim) + " cg_extents_" + key + ";\n") 

    main_file.write("\n")

    main_file.write("    " + "int curr_subtile_num = 0;\n")    
    main_file.write("    " + "std::string out_dir = \"lego_scratch/data_files/\" + curr_tile;\n")
    main_file.write("    " + "const char *data_path = out_dir.c_str();\n")
    main_file.write("\n")

    if(mode != 'rtl'):
        main_file.write("    " + "std::string input_data_path = out_dir + \"/input_data.h\";\n")
        main_file.write("    " + "std::ofstream input_data_file;\n")
        main_file.write("\n")
        main_file.write("    " + "std::string input_meta_data_path = out_dir + \"/input_meta_data.h\";\n")
        main_file.write("    " + "std::ofstream input_meta_data_file;\n")
        main_file.write("\n")
    
    main_file.write("    " + "std::string output_gold_path = out_dir + \"/output_gold.h\";\n")
    main_file.write("    " + "std::ofstream output_gold_file;\n")

    if(mode == 'rtl'): 
        main_file.write("    std::string subtile_path;\n")

    main_file.write("\n")

def cp_closing_decleration(main_file, cg_source_id, cg_source_map, op_list, mode):

    if(mode != 'rtl'):
        main_file.write("\n")
        stmt = "    "
        stmt += "if(curr_subtile_num > 0) {" 
        main_file.write(stmt + "\n")

        main_file.write("\n")
        main_file.write("        " + "input_data_file.open(input_data_path);\n")
        main_file.write("        " + "input_meta_data_file.open(input_meta_data_path);\n")
        main_file.write("\n")

        for key, value in cg_source_id.items():

            tensor_dim = len(value)

            for i in range(0, tensor_dim):
                main_file.write("        " + "mode_data_printer(input_data_file, \"" + key + "\", \"" + str(cg_source_map[key][i]) + "\", cg_subtile_" + key + ".mode_" + str(i) + ");\n")
                main_file.write("        " + "extent_data_printer(input_meta_data_file, \"" + key + "\", \"" + str(cg_source_map[key][i]) + "\", cg_extents_" + key + ".extents_mode_" + str(i) + ");\n")
                main_file.write("\n")

            main_file.write("        " + "val_data_printer(input_data_file, \"" + key + "\", \"vals\", cg_subtile_" + key + ".mode_vals);\n")
            main_file.write("        " + "extent_data_printer(input_meta_data_file, \"" + key + "\", \"vals\", cg_extents_" + key + ".extents_mode_vals);\n")

            main_file.write("\n")

        main_file.write("        " + "input_data_file.close();\n")
        main_file.write("        " + "input_meta_data_file.close();\n")
        
        main_file.write("    " + "}\n")

def cg_tensor_decleration(main_file, cg_source_id, split_factor, cg_dest_id): 

    for key, value in cg_source_id.items():

        tensor_dim = len(value)
        main_file.write("\n")
        
        for i in range(0, tensor_dim):
            main_file.write("    " + "int *" + key + str(i + 1) + "_pos = subtile_" + key + ".pos" + str(i + 1) + ".data();\n")
            main_file.write("    " + "int *" + key + str(i + 1) + "_crd = subtile_" + key + ".crd" + str(i + 1) + ".data();\n")

        main_file.write("    " + "double *" + key + "_vals = subtile_" + key + ".vals.data();" + "\n")
        main_file.write("\n")

    outsize = 1

    for key, value in cg_dest_id.items():
        for id in value:
            outsize *= int(split_factor[id][1])
    
        main_file.write("    " + "int output_subtile_size = " + str(outsize) + ";\n")
        main_file.write("\n")

        main_file.write("    " + "double *" + key + "_vals = (double*)malloc(sizeof(double) * output_subtile_size);\n")
        main_file.write("\n")

        main_file.write("    " + "for (int p" + key + " = 0; p" + key + " < output_subtile_size; p" + key + "++) {\n")
        main_file.write("        " + key + "_vals[p" + key + "] = 0;\n")
        main_file.write("    }\n")

        main_file.write("\n")
        main_file.write("    " + "int p" + key + ";\n")

def subtile_output_decleration(main_file, dest_id, split_factor):
    # dest_name = "Res"
    for name, id in dest_id.items():
        dest_name = name
    # declare the vectors 
    for idx, _ in enumerate(dest_id[dest_name]):
        main_file.write("    std::vector<int> " + dest_name + str(idx + 1) + "_pos_vec;\n")
        main_file.write("    std::vector<int> " + dest_name + str(idx + 1) + "_crd_vec;\n")
    main_file.write("    std::vector<double> " + dest_name + "_vals_vec;\n")

    main_file.write("\n")

    # build the vectors to store the results from the output file of comal/rtl
    for idx, _ in enumerate(dest_id[dest_name]):
        main_file.write("    build_vec(" + dest_name + str(idx + 1) + "_pos_vec, subtile_path + \"/tensor_" + dest_name + "_mode_" + str(idx) + "_seg\");\n")
        main_file.write("    build_vec(" + dest_name + str(idx + 1) + "_crd_vec, subtile_path + \"/tensor_" + dest_name + "_mode_" + str(idx) + "_crd\");\n") 
    main_file.write("    build_vec_val(" + dest_name + "_vals_vec, subtile_path + \"/tensor_" + dest_name + "_mode_vals\");\n")

    main_file.write("\n")

    # get the pointer to the data
    for idx, _ in enumerate(dest_id[dest_name]):
        main_file.write("    int *" + dest_name + str(idx + 1) + "_pos = " + dest_name + str(idx + 1) + "_pos_vec.data();\n")
        main_file.write("    int *" + dest_name + str(idx + 1) + "_crd = " + dest_name + str(idx + 1) + "_crd_vec.data();\n")
    main_file.write("    double *" + dest_name + "_vals = " + dest_name + "_vals_vec.data();\n")

    main_file.write("\n")

    outsize = 1
    for key, value in dest_id.items():
        for id in value:
            outsize *= int(split_factor[id][1])
    
        main_file.write("    " + "int output_subtile_size = " + str(outsize) + ";\n")
        main_file.write("\n")

        main_file.write("    " + "double *" + key + "_output_vals = (double*)malloc(sizeof(double) * output_subtile_size);\n")
        main_file.write("\n")

        main_file.write("    " + "for (int p" + key + " = 0; p" + key + " < output_subtile_size; p" + key + "++) {\n")
        main_file.write("        " + key + "_output_vals[p" + key + "] = 0;\n")
        main_file.write("    }\n")

        main_file.write("\n")
        main_file.write("    " + "int p" + key + "_output;\n")
        
def write_output(main_file, ap_split_factor, dest_id):
    output_tile_size = 0;
    dest_name = None
    for name, id in dest_id.items():
        dest_name = name
        for i in id:
            if output_tile_size == 0:
                output_tile_size = ap_split_factor[i][0]
            else:
                output_tile_size *= ap_split_factor[i][0]
    main_file.write("    std::string output_path = \"lego_scratch/data_files/output.txt\";\n")
    main_file.write("    std::ofstream output_file;\n")
    main_file.write("    output_file.open(output_path, std::ios::app);\n")
    main_file.write("    rtl_output_subtile_printer(" + dest_name + "_vals, " + str(output_tile_size) + ", 0, output_file);\n")
    main_file.write("    output_file.close();\n")

def write_subtile_paths(main_file):
    main_file.write("    std::string subtile_paths_path = \"./subtile_paths.toml\";\n")
    main_file.write("    std::ofstream subtile_paths_file;\n")
    main_file.write("    subtile_paths_file.open(subtile_paths_path, std::ios::app);\n")
    main_file.write("    subtile_paths_printer(subtile_paths, subtile_paths_file);\n")
    main_file.write("    subtile_paths_file.close();\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog="Lego_v0",
                    description="Generate Cpp code for tiling and reduction given the input program and tensors")
    parser.add_argument("-t", "--tensor", type=str, default="./input/tensor.txt")
    parser.add_argument("-p", "--program", type=str, default="./input/program.txt")
    parser.add_argument("-m", "--mode", type=str, default="rtl")

    args = parser.parse_args()

    tensor_path_dict, tensor_type_dict, tensor_transpose_dict = tensor_path_type_dict(args.tensor)

    level = "ap"
    dest, op, ap_dest_id, ap_dest_map, ap_source_id, ap_source_map, expr, ap_split_factor, op_list, ap_schedule = parse(args.program, level)

    level = "cp"
    _, _, cp_dest_id, cp_dest_map, cp_source_id, cp_source_map, _, cp_split_factor, _, cp_schedule = parse(args.program, level)

    level = "cg"
    _, _, cg_dest_id, cg_dest_map, cg_source_id, cg_source_map, _, cg_split_factor, _, cg_schedule = parse(args.program, level)

    for key, value in tensor_path_dict.items():
        output_dir_path = "./lego_scratch/" + "tensor_" + key 
        tensor_schedule = []
        tensor_schedule.append(ap_source_map[key])
        tensor_schedule.append(cp_source_map[key])
        tensor_schedule.append(cg_source_map[key])

        tensor_size = []
        id_list = op[key]

        for i in range(0, 2):
            tensor_size.append([])
        
        for i in range(0, len(id_list)):
            tensor_size[0].append(int(cp_split_factor[id_list[i]][0]))
            tensor_size[1].append(int(cp_split_factor[id_list[i]][1]))

        input_dir_path = tensor_path_dict[key]
        tensor_type    = tensor_type_dict[key]
        transpose      = tensor_transpose_dict[key]    

        pre_process.process(tensor_type, input_dir_path, output_dir_path, tensor_size, tensor_schedule, transpose)    
    
    mode = args.mode

    main_file = open("main.cpp", "w+")

    # Printing the header files
    main_file.write("#include <stdlib.h>\n")   
    main_file.write("#include <stdio.h>\n")
    main_file.write("#include <cstring>\n")
    main_file.write("#include <iostream>\n")
    main_file.write("#include <fstream>\n")
    main_file.write("#include <vector>\n")
    main_file.write("#include <string>\n")
    main_file.write("#include <boost/format.hpp>\n")
    main_file.write("#include <sys/types.h>\n")
    main_file.write("#include <sys/stat.h>\n")
    main_file.write("using namespace std;\n")
    main_file.write("\n")
    main_file.write("#include \"src/data_parser.h\"")
    main_file.write("\n")
    main_file.write("#include \"src/mem_op.h\"")
    main_file.write("\n")
    main_file.write("\n")

    # CGRA gold code
    tensor_dim = str(len(cg_source_id[op_list[0]]))
    stmt = ""
    stmt = stmt + "(" + "subtile" + tensor_dim + " subtile_" + op_list[0]  

    for op in op_list[1:]: 
        tensor_dim = str(len(cg_source_id[op]))
        stmt = stmt + ", " + "subtile" + tensor_dim + " subtile_" + op
    stmt += ", int curr_subtile_num, ofstream &output_gold_file)"

    main_file.write("double* subtile_gold" + stmt + " {\n")
    cg_tensor_decleration(main_file, cg_source_id, cg_split_factor, cg_dest_id)


    for element in codegen.lower(expr, cg_source_id, cg_source_id, op_list, cg_schedule, 1, "cg", cg_split_factor, cg_dest_id, mode, cg_source_id, cg_source_map):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")

    for key in dest.keys():
        dest = key

    main_file.write("\n")  

    if(mode == "rtl"):
        stmt = "    rtl_output_subtile_printer(" + dest + "_vals, output_subtile_size, curr_subtile_num, output_gold_file);"
    else: 
        stmt = "    output_subtile_printer(" + dest + "_vals, output_subtile_size, curr_subtile_num, output_gold_file);"

    main_file.write(stmt)
    main_file.write("\n")
    main_file.write("\n")
    for key in cg_dest_id.keys():
        return_key = key
    main_file.write("    return " + return_key + "_vals;\n")
    main_file.write("\n")
    main_file.write("}\n")
    main_file.write("\n")

    main_file.write("double* read_subtile_output(std::string subtile_path) {\n")
    subtile_output_decleration(main_file, cg_dest_id, cg_split_factor)
    rtl_output_dest_id = {}
    for key in cg_dest_id.keys():
        dest_name = key
        # have to do this conversion to prevent input vals array and the converted dense output array 
        # having the same variable name due to the expression A = A
        rtl_output_dest_id[key + "_output"] = cg_dest_id[key]

    # Conversion from fibertree sparse rtl/comal output file to dense matrix representation for reduction
    # This is accomplished by generating code using the A = A expression 
    for element in codegen.lower("(" + dest_name + ")", cg_dest_id, cg_dest_id, [dest_name], cg_dest_id[dest_name], 1, "cg", cg_split_factor, rtl_output_dest_id, mode, rtl_output_dest_id, cg_dest_map):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")
    main_file.write("\n")
    main_file.write("    return " + dest_name + "_output_vals;\n")
    main_file.write("}\n")
    main_file.write("\n")

    # Sub-tile pairing code
    tensor_dim = str(len(cp_source_id[op_list[0]]))
    stmt = ""
    stmt = stmt + "(" + "tile" + tensor_dim + " tile_" + op_list[0]  
    
    for op in op_list[1:]: 
        tensor_dim = str(len(cp_source_id[op]))
        stmt = stmt + ", " + "tile" + tensor_dim + " tile_" + op
    stmt += ", std::string curr_tile"
    
    if mode == 'rtl':
        stmt += ", std::vector<std::string> &subtile_paths, std::string mode"

    stmt = stmt + ")"

    main_file.write("double* tile_operate" + stmt + " {\n")

    cp_tensor_decleration(main_file, cp_source_id, cp_split_factor, mode)
    main_file.write("\n")
    main_file.write(codegen.workspace_declaration(cp_split_factor, cp_dest_id))
    main_file.write("\n")

    for element in codegen.lower(expr, cp_source_id, cp_source_id, op_list, cp_schedule, 1, "cp", cp_split_factor, cp_dest_id, mode, cg_source_id, cg_source_map):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")

    cp_closing_decleration(main_file, cp_source_id, cg_source_map, op_list, mode)
    main_file.write("\n")
    stmt = codegen.workspace_reduction(cp_split_factor, "cp", cp_dest_id)
    for line in stmt:
        main_file.write(line)
    
    main_file.write("\n")
    for key in cg_dest_id.keys():
        return_key = key
    main_file.write("    return " + return_key + "_vals;\n")
    main_file.write("}\n")
    main_file.write("\n")

    # AP driver code
    main_file.write("int main(int argc, char *argv[]) {\n")
    main_file.write("\n")
    if mode == "rtl":
        # parsing command line argument that specify if we are in reduction mode or not
        # reduction mode: iterate through all the subtile results computed by rtl/comal and perform reduction/combination
        # tiling mode: iterate through all the subtiles and print them out for rtl/comal
        main_file.write("    assert(argc == 2);\n")
        main_file.write("    std::string mode = argv[1];\n")

    ap_tensor_decleration(main_file, ap_source_id)

    # vector for storing the list of all the subtile path 
    # this is for comal
    if mode == "rtl":
        main_file.write("\n")
        main_file.write("    std::vector<std::string> subtile_paths;\n")

    main_file.write("\n")
    main_file.write(codegen.workspace_declaration(ap_split_factor, ap_dest_id))
    main_file.write("\n")
    for element in codegen.lower(expr, ap_source_id, ap_source_id, op_list, ap_schedule, 1, "ap", ap_split_factor, ap_dest_id, mode, cp_source_id, cp_source_map):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")
    stmt = codegen.workspace_reduction(ap_split_factor, "ap", ap_dest_id)
    for line in stmt:
        main_file.write(line)
    main_file.write("\n")
    
    # generate code that write the output matrix to file
    write_output(main_file, ap_split_factor, ap_dest_id)
    main_file.write("\n")

    # genearte the toml path list file for comal
    if mode == "rtl":
        write_subtile_paths(main_file)

    main_file.write("\n")
    main_file.write("    return 0;\n")
    main_file.write("}\n")
    main_file.close()
