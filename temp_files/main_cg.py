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
            cp_driver_file.write("    " + "int *" + key + str(i + 1) + "_pos = tile_" + key + "[" + str(2 * i) + "];\n")
            cp_driver_file.write("    " + "int *" + key + str(i + 1) + "_crd = tile_" + key + "[" + str(2 * i + 1) + "];\n")

        cp_driver_file.write("    " + "int *" + key + "_vals = tile_" + key + "[" + str(4 * tensor_dim) + "];\n")
        cp_driver_file.write("\n")

        for i in range (0, tensor_dim):
            cp_driver_file.write("    " + "std::vector<int> " + "subtile_" + key + str(i + 1) + "_pos;\n")
            cp_driver_file.write("    " + "std::vector<int> " + "subtile_" + key + str(i + 1) + "_crd;\n")

        cp_driver_file.write("    " + "std::vector<int> " + "subtile_" + key + "_vals;\n")   
        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "int **subtile_" + key + ";\n")
        cp_driver_file.write("    " + "subtile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(2 * tensor_dim + 1) + "));\n")

        cp_driver_file.write("\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "subtile_" + key + "[" + str(2 * i) + "] = subtile_" + key + str(i + 1) + "_pos.data();\n")
            cp_driver_file.write("    " + "subtile_" + key + "[" + str(2 * i + 1) + "] = subtile_" + key + str(i + 1) + "_crd.data();\n")

        cp_driver_file.write("    " + "subtile_" + key + "[" + str(2 * tensor_dim) + "] = subtile_" + key + "_vals.data();\n")
        cp_driver_file.write("\n")

        total_size = 1
        for id in cp_source_id[key]:
            total_size *= int(split_dict[id][0]/split_dict[id][1])

        cp_driver_file.write("    " + "int store_size_" + key + " = " + str(total_size) + ";\n")
        cp_driver_file.write("    " + "int id_store_" + key + ";\n")
        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "bool *store_" + key + " = (bool *) calloc((store_size_" + key + " + 1), sizeof(bool));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "int *" + key + "_mode" + str(i) + "_start = (int*)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
            cp_driver_file.write("    " + "int *" + key + "_mode" + str(i) + "_end = (int*)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
        
        cp_driver_file.write("    " + "int *" + key + "_mode_vals_start = (int*)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
        cp_driver_file.write("    " + "int *" + key + "_mode_vals_end = (int*)malloc((store_size_" + key + " + 1) * sizeof(int));\n")
      
        cp_driver_file.write("\n")
        cp_driver_file.write("    " + "int **store_subtile_" + key + ";\n")
        cp_driver_file.write("    " + "store_subtile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(2 * tensor_dim + 2) + "));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * i) + "] = " + key + "_mode" + str(i) + "_start;\n")
            cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * i + 1) + "] = " + key + "_mode" + str(i) + "_end;\n")

        cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim) + "] = " + key + "_mode_vals_start;\n")
        cp_driver_file.write("    " + "store_subtile_" + key + "[" + str(2 * tensor_dim + 1) + "] = " + key + "_mode_vals_end;\n")

        cp_driver_file.write("\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "std::vector<int> " + key + "_mode_" + str(i) + ";\n")
        cp_driver_file.write("    " + "std::vector<int> " + key + "_mode_vals;\n")
        cp_driver_file.write("\n")

        for i in range(0, tensor_dim): 
            cp_driver_file.write("    " + "std::vector<int> " + key + "_extents_mode_" + str(i) + ";\n")
        cp_driver_file.write("    " + "std::vector<int> " + key + "_extents_mode_vals;\n")
        cp_driver_file.write("\n")

        cp_driver_file.write("    " + "int **cg_subtile_" + key + ";\n")
        cp_driver_file.write("    " + "cg_subtile_" + key + " = (int**)malloc(sizeof(int*) * (" + str(tensor_dim + 1) + "));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "cg_subtile_" + key + "[" + str(i) + "] = " + key + "_mode_" + str(i) + ".data();\n")
        cp_driver_file.write("    " + "cg_subtile_" + key + "[" + str(tensor_dim) + "] = " + key + "_mode_vals.data();\n")

        cp_driver_file.write("\n")
        cp_driver_file.write("    " + "int **cg_extents_" + key + ";\n")
        cp_driver_file.write("    " + "cg_extents_" + key + " = (int**)malloc(sizeof(int*) * (" + str(tensor_dim + 1) + "));\n")

        for i in range(0, tensor_dim):
            cp_driver_file.write("    " + "cg_extents_" + key + "[" + str(i) + "] = " + key + "_extents_mode_" + str(i) + ".data();\n")
        cp_driver_file.write("    " + "cg_extents_" + key + "[" + str(tensor_dim) + "] = " + key + "_extents_mode_vals.data();\n")
       
def cg_tensor_decleration(cg_driver_file, cg_source_id, split_factor, cg_dest_id): 

    for key, value in cg_source_id.items():

        tensor_dim = len(value)
        cg_driver_file.write("\n")

        for i in range(0, tensor_dim):
            cg_driver_file.write("    " + "int *" + key + str(i + 1) + "_pos = tile_" + key + ".pos" + str(i + 1) + ".data();\n")
            cg_driver_file.write("    " + "int *" + key + str(i + 1) + "_crd = tile_" + key + ".pos" + str(i + 1) + ".data();\n")

        cg_driver_file.write("    " + "int *" + key + "_vals = tile_" + key + ".vals.data();" + "\n")
        cg_driver_file.write("\n")

    outsize = 1

    for key, value in cg_dest_id.items():
        for id in value:
            outsize *= int(split_factor[id][1])
    
        cg_driver_file.write("    " + "int output_subtile_size = " + str(outsize) + ";\n")
        cg_driver_file.write("\n")

        cg_driver_file.write("    " + "int *" + key + "_vals = (int*)malloc(sizeof(int) * output_subtile_size);\n")
        cg_driver_file.write("\n")

        cg_driver_file.write("    " + "for (int p" + key + " = 0; p" + key + " < output_subtile_size; p" + key + "++) {\n")
        cg_driver_file.write("        " + key + "_vals[p" + key + "] = 0;\n")
        cg_driver_file.write("    }\n")

        cg_driver_file.write("\n")
        cg_driver_file.write("    " + "int p" + key + ";\n")

if __name__ == "__main__":

    tensor_path_input = "input/tensor.txt"
    tensor_path_dict, tensor_type_dict = tensor_path_type_dict(tensor_path_input)

    program_spec_input = "input/program.txt"

    level = "cg"
    dest, op, cg_dest_id, cg_dest_map, cg_source_id, cg_source_map, expr, split_factor, op_list, cg_schedule = parse(program_spec_input, level)

    cg_driver_file = open("lego_scratch/subtile_gold.cpp", "w+")

    tensor_dim = str(len(cg_source_id[op_list[0]]))
    stmt = ""
    stmt = stmt + "(" + "tile" + tensor_dim + " tile_" + op_list[0]  
    
    for op in op_list[1:]: 
        tensor_dim = str(len(cg_source_id[op]))
        stmt = stmt + ", " + "tile" + tensor_dim + " tile_" + op
    stmt += ", int curr_subtile_num, ofstream &output_gold_file)"

    cg_driver_file.write("int subtile_gold" + stmt + " {\n")
    cg_tensor_decleration(cg_driver_file, cg_source_id, split_factor, cg_dest_id)


    for element in temp_refactor.lower(expr, cg_source_id, cg_source_id, op_list, cg_schedule, 1, "cg", split_factor, cg_dest_id):
        if element != [""]:
            cg_driver_file.write(element[0])
            cg_driver_file.write("\n")

    print(expr)

    for key in dest.keys():
        dest = key

    cg_driver_file.write("\n")  
    stmt = "    output_subtile_printer(" + dest + "_vals, output_subtile_size, curr_subtile_num, output_gold_file);"
    cg_driver_file.write(stmt)
    cg_driver_file.write("\n")
    cg_driver_file.write("\n")
    cg_driver_file.write("    return 0;\n")
    cg_driver_file.write("\n")
    cg_driver_file.write("}\n")
    cg_driver_file.close()  
