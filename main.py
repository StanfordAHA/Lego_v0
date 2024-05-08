import pre_process
import codegen
import sys

sys.path.insert(0, './')
sys.path.insert(0, './sam')

from pyparsing import Word, alphas, one_of, alphanums

def tensor_path_type_dict(tensor_path_input):

    tensor_path_dict = {}
    tensor_type_dict = {}

    tensor_path_dict_keys = [] 

    with open(tensor_path_input, 'r') as f:
        data = f.read().splitlines()
    
    data = [i for i in data]
    data = [i.replace(" ", "") for i in data]

    for i in range(0, len(data)):
        if(data[i] == ""):
            data.pop(i)
        parsed_data = data[i].split(":")
        tensor_type_dict[parsed_data[0]] = parsed_data[1]
        tensor_path_dict[parsed_data[0]] = parsed_data[2]   

    return tensor_path_dict, tensor_type_dict

def file_parser(input_file):
    with open(input_file, 'r') as f:
        data = f.read().splitlines()
    return data

def data_parser(data):

    data = [i for i in data]
    data = [i.replace(" ", "") for i in data]

    arith_op = one_of("+ - * /")

    num_op_rule = Word(alphas) + ":" + Word(alphanums)
    num_op = num_op_rule.parseString(data[0])[2]

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

    split_factor_rule = Word(alphas) + ':split:' + Word(alphanums) + ':' + Word(alphanums)

    split_factor = {}

    for i in range(num_ids):
        parsed_split = split_factor_rule.parseString(data[5 + i])
        split_factor[parsed_split[0]] = [int(parsed_split[2]), int(parsed_split[4])]
    
    return num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor

def parse(input_file, level):

    data = file_parser(input_file)
    num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor = data_parser(data)

    if(level == "ap"): 
        schedule = schedule_1
    elif(level == "cp"):
        schedule = schedule_2
    else:
        schedule = schedule_3

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

if __name__ == "__main__":

    tensor_path_input = "input/tensor.txt"
    tensor_path_dict, tensor_type_dict = tensor_path_type_dict(tensor_path_input)

    program_spec_input = "input/program.txt"

    level = "ap"
    dest, op, ap_dest_id, ap_dest_map, ap_source_id, ap_source_map, expr, split_factor, op_list, ap_schedule = parse(program_spec_input, level)

    level = "cp"
    _, _, cp_dest_id, cp_dest_map, cp_source_id, cp_source_map, _, _, _, cp_schedule = parse(program_spec_input, level)

    level = "cg"
    _, _, cg_dest_id, cg_dest_map, cg_source_id, cg_source_map, _, _, _, cg_schedule = parse(program_spec_input, level)

    for key, value in tensor_path_dict.items():
        output_dir_path = "./lego_scratch/" + "tensor_" + key 
        tensor_schedule = []
        tensor_schedule.append(ap_source_map[key])
        tensor_schedule.append(cp_source_map[key])
        tensor_schedule.append(cg_source_map[key])

        tensor_size = []
        id_list = op[key]

        for id in id_list:
            tensor_size.append([])
        
        for i in range(0, len(id_list)):
            tensor_size[0].append(int(split_factor[id_list[i]][0]))
            tensor_size[1].append(int(split_factor[id_list[i]][1]))

        input_dir_path = tensor_path_dict[key]
        tensor_type    = tensor_type_dict[key]    

        pre_process.process(tensor_type, input_dir_path, output_dir_path, tensor_size, tensor_schedule)    
    

    mode = sys.argv[1]

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

    main_file.write("int subtile_gold" + stmt + " {\n")
    cg_tensor_decleration(main_file, cg_source_id, split_factor, cg_dest_id)


    for element in codegen.lower(expr, cg_source_id, cg_source_id, op_list, cg_schedule, 1, "cg", split_factor, cg_dest_id, mode, cg_source_id):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")

    for key in dest.keys():
        dest = key

    main_file.write("\n")  

    if(mode == "rtl"):
        stmt = "    rtl_output_subtile_printer(" + dest + "_vals, output_subtile_size, curr_subtile_num, output_gold_file);"
    else: 
        stmt = "    output_subtile_printer(" + dest + "_vals, output_subtile_size, curr_subtile_num);"

    main_file.write(stmt)
    main_file.write("\n")
    main_file.write("\n")
    main_file.write("    return 0;\n")
    main_file.write("\n")
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
    stmt = stmt + ")"

    main_file.write("int tile_operate" + stmt + " {\n")

    cp_tensor_decleration(main_file, cp_source_id, split_factor, mode)
    main_file.write("\n")
    
    for element in codegen.lower(expr, cp_source_id, cp_source_id, op_list, cp_schedule, 1, "cp", split_factor, cp_dest_id, mode, cg_source_id):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")

    cp_closing_decleration(main_file, cp_source_id, cg_source_map, op_list, mode)
    
    main_file.write("\n")
    main_file.write("    return 0;\n")
    main_file.write("}\n")
    main_file.write("\n")

    # AP driver code
    main_file.write("int main() {\n")
    ap_tensor_decleration(main_file, ap_source_id)
    main_file.write("\n")
    for element in codegen.lower(expr, ap_source_id, ap_source_id, op_list, ap_schedule, 1, "ap", split_factor, ap_dest_id, mode, cp_source_id):
        if element != [""]:
            main_file.write(element[0])
            main_file.write("\n")
    main_file.write("\n")
    main_file.write("    return 0;\n")
    main_file.write("}\n")
    main_file.close()
