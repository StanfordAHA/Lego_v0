import os
import json
import argparse
import itertools
import shutil

# Function to generate input data
def generate_input_data(entry):
    name = entry["name"]
    sweep = entry["sweep"]
    tile_list = entry["tile_list"]
    datasets = entry["datasets"]
    app = entry["app"][0]  # Assuming single app for each entry
    schedule_list = entry["schedule_list"][0]  # Assuming single schedule list for each entry
    bitstreams = entry["bitstreams"]
    pre_process = entry["pre_process"][0]
    flags = entry["flags"]

    if sweep == 1:
        # Generate input data for sweeping over tile_list and datasets
        input_data = []
        for tile in tile_list:
            for dataset in datasets:
                input_data.append([[app], schedule_list, tile, pre_process, dataset])
        return name, input_data, bitstreams, flags
    elif sweep == 0:
        # Pair tile_list and datasets element by element
        if len(tile_list) != len(datasets):
            raise ValueError("tile_list and datasets length mismatch for sweep=0")
        input_data = []
        for tile, dataset in zip(tile_list, datasets):
            input_data.append([[app], schedule_list, tile, pre_process, dataset])
        return name, input_data, bitstreams, flags 
    else:
        raise ValueError(f"Unknown sweep mode: {sweep}")

# Main function to process all data entries and generate input data
def process_data(data):
    all_input_data = []
    for entry in data:
        name, input_data, bitstreams, flags = generate_input_data(entry)
        all_input_data.append([name, input_data, bitstreams, flags])
    return all_input_data

def generate_program_txt(equation, schedules, tile_splits, activation_ap='none', activation_cp='none', activation_cgra='none'):
    """
    Generates the content of the program.txt file based on dynamic indices.
    
    :param equation: String, the equation for matrix multiplication (e.g. "X(i,j)=B(i,j)*C(i,j)")
    :param schedules: List of schedules, 3 elements for ap, cp, cgra (e.g. ["ikj", "ikj", "ijk"])
    :param tile_splits: List of splits for indices (e.g. [30, 30, 30] for i, j, k)
    :param activation_ap: String, activation for ap (default: none)
    :param activation_cp: String, activation for cp (default: none)
    :param activation_cgra: String, activation for cgra (default: none)
    
    :return: String, content of program.txt
    """
    # Build split strings dynamically based on number of indices
    splits = ""
    for idx, split in zip(schedules[0], tile_splits):  # Using schedule_ap to match with tile splits
        splits += f"{idx}:split:10000:10000:{split}\n"

    program_txt = f"""
app_name: matmul_ijk
stmt: {equation[0]}
schedule_ap:   [{schedules[0]}]
schedule_cp:   [{schedules[1]}]
schedule_cgra: [{schedules[2]}]
{splits.strip()}
activation_ap:   {activation_ap}
activation_cp:   {activation_cp}
activation_cgra: {activation_cgra}
"""
    return program_txt.strip()

def generate_tensor_txt(tensor_data, dataset_names):
    """
    Generates the content of the tensor.txt file.
    
    :param tensor_data: List of tensors and their info (e.g. ["B:0", "C:onyx_matmul"])
    :param dataset_names: List of datasets to be appended to tensors (e.g. ["ss", "football"])
    
    :return: String, content of tensor.txt with hardcoded 60.
    """
    tensor_txt = ""
    for tensor in tensor_data:
        name, var = tensor.split(":")
        tensor_txt += f"{name}:{dataset_names[0]}:{dataset_names[1]}:s:{var}:60:int\n"
    return tensor_txt.strip()

def process_input_data(data):
    """
    Processes the input data and generates the program.txt and tensor.txt files.
    
    :param input_data: List containing the equation, schedules, tile splits, tensors, and datasets.
    """
    #print(data)
    # Unpack input data
    equation, schedules, tile_splits, tensor_data, dataset_names = data
        
    # Generate content for program.txt and tensor.txt
    program_txt_content = generate_program_txt(equation, schedules, tile_splits)
    tensor_txt_content = generate_tensor_txt(tensor_data, dataset_names)

    # Write the content to program.txt
    with open("input/program.txt", "w+") as program_file:
        program_file.write(program_txt_content)
        
    # Write the content to tensor.txt
    with open("input/tensor.txt", "w+") as tensor_file:
        tensor_file.write(tensor_txt_content)


def create_input_data(apps, schedule_list, tile_list, pre_process, datasets):
    # Create Cartesian product of all inputs
    input_data = list(itertools.product(apps, schedule_list, tile_list, pre_process, datasets))
    return input_data

if __name__ == "__main__":
    # Input format

    parser = argparse.ArgumentParser(
                    prog="JSSC Lego Wrapper",
                    description="Generates the input and outputs for JSSC testing")

    parser.add_argument("--json", type=str, default="jssc_inputs/jssc_matmul_input.json")           
    args = parser.parse_args()

    with open(args.json) as f:
        json_data = json.load(f)

    data = process_data(json_data)
   

    for item in data: 
        curr_app_name   = item[0]
        curr_input_data = item[1]
        curr_bitstreams = item[2]
        curr_flags      = item[3]

        if not os.path.exists(f"./jssc_outputs/{curr_app_name}/"):
            os.makedirs(f"./jssc_outputs/{curr_app_name}/", exist_ok=True)

        for input in curr_input_data: 
            for bitstream in curr_bitstreams: 

                out_dir = f"./jssc_outputs/{curr_app_name}/{input[1][-1]}_{input[4][-1]}_{input[2][-1]}_{bitstream[0][-8:]}_{bitstream[1]}/"
                if os.path.exists(out_dir):     
                    shutil.rmtree(out_dir)               
                os.makedirs(out_dir, exist_ok=True)

                bitstream_file   = f"./jssc_inputs/{bitstream[0]}/bitstream.bs"
                reg_write_file   = f"./jssc_inputs/{bitstream[0]}/reg_write.h"
                design_meta_file = f"./jssc_inputs/{bitstream[0]}/design_meta.json"

                if(bitstream[1] == 1):
                    args_list = "--mode onyx -u" 
                else:
                    args_list = "--mode onyx"

                unroll_flag = bitstream[1] 
                process_input_data(input)

                for flag in curr_flags[0]: 
                    if flag != "":
                        args_list += f" {flag}"

                os.system("rm -rf lego_scratch/")
                os.system("mkdir lego_scratch/")
                os.system("rm -rf main.cpp")

                args = f"{args_list} --bitstream {bitstream_file} --design_meta {design_meta_file} --reg_write {reg_write_file} --output_dir {out_dir}"

                # print(args)

                os.system("python3 main.py " + args)
                os.system("g++ -o main main.cpp src/data_parser.cpp src/mem_op.cpp")
                os.system("./main")
                
                os.chdir(out_dir)
                print(out_dir)
                os.system("find . -type f -exec cp {} . \;")
                os.system("rm -rf " + curr_app_name)
                os.chdir("/aha/Lego_v0")

