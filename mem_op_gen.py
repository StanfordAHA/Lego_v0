
import os

def mem_op_gen(in_format, out_format, file_name) :

    file = open(file_name, "w")

    # Defining the vector lib files 
    file.write("#include <vector>\n\n")

    # Defining the required structs 
    in_encoding = "".join(in_format)
    file.write(f"struct tile_{in_encoding}")
    file.write("{\n")
    for i in range(len(in_format)):
        if(in_format[i] == "s"):
            file.write(f"std::vector<int> pos{i + 1};\n")
            file.write(f"std::vector<int> crd{i + 1};\n")
    file.write("std::vector<float> vals;\n")
    file.write("};\n\n")

    out_encoding = "".join(out_format)
    file.write(f"struct tile_{out_encoding}")
    file.write("{\n")
    for i in range(len(out_format)):
        if(out_format[i] == "s"):
            file.write(f"std::vector<int> pos{i + 1};\n")
            file.write(f"std::vector<int> crd{i + 1};\n")
   
    file.write("std::vector<float> vals;\n")
    file.write("};\n\n")

    # Defining the function to generate the memory operation
    file.write(f"tile_{out_encoding} tensor_mem_op(tile_{in_encoding} tensor_op, int index)")
    file.write("{\n")

    len_in = len(in_format)
    len_out = len(out_format)

    if out_format != in_format[len_in - len_out:]:
        print("Error: Output format should be a subset of input format")
        return

    for i in range(len_out):
        if(out_format[i] == "s"):
            file.write(f"int *pos{i + 1} = tensor_op.pos{i + 1 + len_in - len_out}.data();\n")
            file.write(f"int *crd{i + 1} = tensor_op.crd{i + 1 + len_in - len_out}.data();\n")

    file.write("float *vals = tensor_op.vals.data();\n\n")

    file.write(f"tile_{out_encoding} tile_op;\n\n")

    for i in range(len_out):
        file.write(f"int i{i}_end = 0;\n")


    for i in range(len_out):
        if i == 0:
            prev_i = "ndex"
        else:
            prev_i = i - 1

        if(out_format[i] == "d"):
            file.write(f"for(int i{i} = i{prev_i} * i{i}_dim; i{i} < (i{prev_i} + 1) * i{i}_dim; i{i}++)")
            file.write("{\n")
            file.write(f"if(i{i} == (i{prev_i} + 1) * i{i}_dim - 1) i{i}_end = 1;\n")
        elif(out_format[i] == "s"):
            if i == 0: 
                file.write(f"tile_op.pos{i+1}.push_back(pos{i+1}[index]);\n")
                file.write(f"tile_op.pos{i+1}.push_back(pos{i+1}[index + 1]);\n")
            else: 
                file.write(f"tile_op.pos{i+1}.push_back(pos{i+1}[i{prev_i} + 1]);\n")
                file.write("if(i0_end")
                for j in range(1, i):
                    file.write(f" && i{j}_end")
                file.write(") ")
                file.write(f"tile_op.pos{i+1}.push_back(i{i-1}_end + 1);\n")
            file.write(f"for(int i{i} = pos{i+1}[i{prev_i}]; i{i} < pos{i+1}[i{prev_i} + 1]; i{i}++)")
            file.write("{\n")
            file.write(f"if(i{i} == pos{i+1}[i{prev_i} + 1] - 1) i{i}_end = 1;")
            file.write(f"tile_op.crd{i+1}.push_back(crd{i+1}[i{i}]);\n")

        if(i == len_out - 1):
            file.write(f"tile_op.vals.push_back(vals[i{i}]);\n")
            file.write("}" * len_out)
            file.write("\n\n")

    for i in range(len_out):
        if(out_format[i] == "s"):
            file.write(f"std::transform(tile_op.pos{i+1}.begin(), tile_op.pos{i+1}.end(), tile_op.pos{i+1}.begin(), [pos{i+1}[0]](int elem)" + "{return elem - pos" +  str(i+1) + "[0]; });\n")
            


    file.write("}\n\n")





if __name__ == "__main__":

    in_format = ["s", "s", "s", "s", "s", "s"]
    out_format = ["s", "s", "s"]
    file_name = "mem_op.cpp"
    mem_op_gen(in_format, out_format, file_name)
    os.system(f"clang-format -i {file_name}")




