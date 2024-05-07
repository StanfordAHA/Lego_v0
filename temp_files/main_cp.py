import pre_process
import temp_refactor
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

    tensor_path_dict_keys = data[0].split(",")

    num_tensors = len(tensor_path_dict_keys)

    for i in range(0, num_tensors):
        tensor_path_dict[tensor_path_dict_keys[i]] = data[i + 1]
    
    for i in range(0, num_tensors):
        tensor_type_dict[tensor_path_dict_keys[i]] = data[i + num_tensors + 1]

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

    split_factor_rule = Word(alphas) + ':' + "["
        
    for i in range(num_ids):
        split_factor_rule += "[" + Word(alphanums) + "," + Word(alphanums) + "]"
        
    schedule_split_rule = Word(alphas) + ":" + "[" + Word(alphas) + "]"
    schedule_split = list(schedule_split_rule.parseString(data[6])[3])

    split_factor = {}

    for i in range(num_ids):
        split_factor[schedule_split[i]] = [int(split_factor_rule.parseString(data[5])[4 + 5 * i])]
        split_factor[schedule_split[i]].append(int(split_factor_rule.parseString(data[5])[6 + 5 * i]))
    
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

def ap_tensor_decleration(ap_driver_file, ap_source_id):

    for key, value in ap_source_id.items():

        tensor_dim = len(value)

        ap_driver_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            ap_driver_file.write("    " + "std::vector<int> " + key + str(i + 1) + "_pos"  + ";\n")
            ap_driver_file.write("    " + "std::vector<int> " + key + str(i + 1) + "_crd"  + ";\n")

        ap_driver_file.write("    " + "std::vector<int> " + key + "_vals;\n")

        ap_driver_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            ap_driver_file.write("    " + "build_vec(" + key + str(i + 1) +  "_pos, " + "\"lego_scratch/tensor_" + key + "/tcsf_pos" + str(i + 1) + ".txt\");\n")
            ap_driver_file.write("    " + "build_vec(" + key + str(i + 1) +  "_crd, " + "\"lego_scratch/tensor_" + key + "/tcsf_crd" + str(i + 1) + ".txt\");\n")

        ap_driver_file.write("    " + "build_vec(" + key + "_vals, " + "\"lego_scratch/tensor_" + key + "/tcsf_vals.txt\");\n")
        
        ap_driver_file.write("\n")

        ap_driver_file.write("    " + "int **tensor_" + key + ";\n")
        ap_driver_file.write("    " + "tensor_" + key + " = (int**)malloc(sizeof(int*) * (" + str(6 * tensor_dim + 1) + "));\n")

        ap_driver_file.write("\n")

        for i in range(0, 3 * tensor_dim):
            ap_driver_file.write("    " + "tensor_" + key + "[" + str(2 * i) + "] = " + key + str(i + 1) + "_pos.data();\n")
            ap_driver_file.write("    " + "tensor_" + key + "[" + str(2 * i + 1) + "] = " + key + str(i + 1) + "_crd.data();\n")

        ap_driver_file.write("    " + "tensor_" + key + "[" + str(6 * tensor_dim) + "] = " + key + "_vals.data();\n")
    
        ap_driver_file.write("\n")

        for i in range(0, 2 * tensor_dim):
            ap_driver_file.write("    " + "std::vector<int> tile_" + key + str(i + 1) + "_pos;\n")
            ap_driver_file.write("    " + "std::vector<int> tile_" + key + str(i + 1) + "_crd;\n")

        ap_driver_file.write("    " + "std::vector<int> tile_" + key + "_vals;\n")

        ap_driver_file.write("\n")

        ap_driver_file.write("    " + "int **tile_" + key + ";\n")
        ap_driver_file.write("    " + "tile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(4 * tensor_dim + 1) + "));\n")

        ap_driver_file.write("\n")
        
        for i in range(0, 2 * tensor_dim):
            ap_driver_file.write("    " + "tile_" + key + "[" + str(2 * i) + "] = tile_" + key + str(i + 1) + "_pos.data();\n")
            ap_driver_file.write("    " + "tile_" + key + "[" + str(2 * i + 1) + "] = tile_" + key + str(i + 1) + "_crd.data();\n")

        ap_driver_file.write("    " + "tile_" + key + "[" + str(4 * tensor_dim) + "] = tile_" + key + "_vals.data();\n") 

def cp_tensor_decleration(cp_driver_file, cp_source_id, split_dict):

    for key, value in cp_source_id.items():

        tensor_dim = len(value)
        cp_driver_file.write("\n")

        for i in range(0, 2 * tensor_dim):
            cp_driver_file.write("    " + "int *" + key + str(i + 1) + "_pos = tile_" + key + ".pos" + str(i + 1) + ".data();\n")
            cp_driver_file.write("    " + "int *" + key + str(i + 1) + "_crd = tile_" + key + ".pos" + str(i + 1) + ".data();\n")

        cp_driver_file.write("    " + "int *" + key + "_vals = tile_" + key + ".vals.data();" + "\n")
        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "subtile" + str(tensor_dim) + " subtile_" + key + ";\n")

        cp_driver_file.write("\n")

        total_size = 1
        for id in cp_source_id[key]:
            total_size *= int(split_dict[id][0]/split_dict[id][1])

        cp_driver_file.write("    " + "int store_size_" + key + " = " + str(total_size) + ";\n")
        cp_driver_file.write("    " + "int id_store_" + key + ";\n")
        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "bool *store_" + key + " = (bool *) calloc((store_size_" + key + " + 1), sizeof(bool));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "int *" + key + "_mode" + str(i) + "_start = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
            cp_driver_file.write("    " + "int *" + key + "_mode" + str(i) + "_end = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
        
        cp_driver_file.write("    " + "int *" + key + "_mode_vals_start = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
        cp_driver_file.write("    " + "int *" + key + "_mode_vals_end = (int *)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
      
        cp_driver_file.write("\n")
        cp_driver_file.write("    " + "int **store_subtile_" + key + ";\n")
        cp_driver_file.write("    " + "store_subtile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(2 * tensor_dim + 2) + "));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * i) + "] = " + key + "_mode" + str(i) + "_start;\n")
            cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * i + 1) + "] = " + key + "_mode" + str(i) + "_end;\n")

        cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim) + "] = " + key + "_mode_vals_start;\n")
        cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim + 1) + "] = " + key + "_mode_vals_end;\n")

        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "cg_subtile" + str(tensor_dim) + " cg_subtile_" + key + ";\n")
        cp_driver_file.write("    " + "cg_extents" + str(tensor_dim) + " cg_extents_" + key + ";\n") 

    cp_driver_file.write("\n")

    cp_driver_file.write("    " + "int curr_subtile_num = 0;\n")    
    cp_driver_file.write("    " + "std::string out_dir = \"lego_scratch/data_files/\" + curr_tile;\n")
    cp_driver_file.write("    " + "const char *data_path = out_dir.c_str();\n")
    cp_driver_file.write("\n")
    cp_driver_file.write("    " + "std::string input_data_path = out_dir + \"/input_data.h\";\n")
    cp_driver_file.write("    " + "std::ofstream input_data_file;\n")
    cp_driver_file.write("\n")
    cp_driver_file.write("    " + "std::string input_meta_data_path = out_dir + \"/input_meta_data.h\";\n")
    cp_driver_file.write("    " + "std::ofstream input_meta_data_file;\n")
    cp_driver_file.write("\n")
    cp_driver_file.write("    " + "std::string output_gold_path = out_dir + \"/output_gold.h\";\n")
    cp_driver_file.write("    " + "std::ofstream output_gold_file;\n")

def cp_closing_decleration(cp_driver_file, cg_source_id, cg_source_map, op_list):

    cp_driver_file.write("\n")
    stmt = "    "
    stmt += "if(cg_extents_" + op_list[0] + ".extents_mode_0.size() > 0) {" 
    cp_driver_file.write(stmt + "\n")

    cp_driver_file.write("\n")
    cp_driver_file.write("        " + "input_data_file.open(input_data_path);\n")
    cp_driver_file.write("        " + "input_meta_data_file.open(input_meta_data_path);\n")
    cp_driver_file.write("\n")

    for key, value in cg_source_id.items():

        tensor_dim = len(value)

        for i in range(0, tensor_dim):
            cp_driver_file.write("        " + "mode_data_printer(input_data_file, \"" + key + "\", \"" + str(cg_source_map[key][i]) + "\", cg_subtile_" + key + ".mode_" + str(i) + ");\n")
            cp_driver_file.write("        " + "extent_data_printer(input_meta_data_file, \"" + key + "\", \"" + str(cg_source_map[key][i]) + "\", cg_extents_" + key + ".extents_mode_" + str(i) + ");\n")
            cp_driver_file.write("\n")

        cp_driver_file.write("        " + "mode_data_printer(input_data_file, \"" + key + "\", \"vals\", cg_subtile_" + key + ".mode_vals);\n")
        cp_driver_file.write("        " + "extent_data_printer(input_meta_data_file, \"" + key + "\", \"vals\", cg_extents_" + key + ".extents_mode_vals);\n")

        cp_driver_file.write("\n")

    cp_driver_file.write("        " + "input_data_file.close();\n")
    cp_driver_file.write("        " + "input_meta_data_file.close();\n")
    
    cp_driver_file.write("    " + "}\n")


if __name__ == "__main__":

    tensor_path_input = "input/tensor.txt"
    tensor_path_dict, tensor_type_dict = tensor_path_type_dict(tensor_path_input)

    program_spec_input = "input/program.txt"

    level = "cp"
    _, _, cp_dest_id, cp_dest_map, cp_source_id, cp_source_map, expr,  split_factor, op_list, cp_schedule = parse(program_spec_input, level)

    level = "cg"
    _, _, cg_dest_id, cg_dest_map, cg_source_id, cg_source_map, _, _, _, cg_schedule = parse(program_spec_input, level)

    cp_driver_file = open("lego_scratch/tile_operate.cpp", "w+")   

    tensor_dim = str(len(cp_source_id[op_list[0]]))
    stmt = ""
    stmt = stmt + "(" + "tile" + tensor_dim + " tile_" + op_list[0]  
    
    for op in op_list[1:]: 
        tensor_dim = str(len(cp_source_id[op]))
        stmt = stmt + ", " + "tile" + tensor_dim + " tile_" + op
    stmt += ", std::string curr_tile"
    stmt = stmt + ")"

    cp_driver_file.write("int tile_operate" + stmt + " {\n")

    cp_tensor_decleration(cp_driver_file, cp_source_id, split_factor)
    cp_driver_file.write("\n")
    
    for element in temp_refactor.lower(expr, cp_source_id, cp_source_id, op_list, cp_schedule, 1, "cp", split_factor):
        if element != [""]:
            cp_driver_file.write(element[0])
            cp_driver_file.write("\n")

    cp_closing_decleration(cp_driver_file, cp_source_id, cg_source_map, op_list)
    
    cp_driver_file.write("\n")

    cp_driver_file.write("    return 0;\n")
    cp_driver_file.write("}\n")