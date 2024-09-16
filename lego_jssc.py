import os 
import re
import numpy as np 
import argparse
import shutil


directory = "jssc_inputs/"

app_list = os.listdir(directory)

if os.path.exists("./jssc_outputs"):
    shutil.rmtree("./jssc_outputs")
os.mkdir("./jssc_outputs")

regex = re.compile(r'program.*\.txt')

for app in app_list: 
    app_name = app 

    design_meta_file = directory + app + "/design_meta.json"
    reg_write_file   = directory + app + "/reg_write.h"

    bitstream_list = os.listdir(directory + app + "/bitstreams/")
    file_list = os.listdir(directory + app + "/inputs/")

    program_list = []
    for file in file_list: 
        if regex.match(file): 
            program_list.append(file)

    for bitstream in bitstream_list:
        for program in program_list:
            bitstream_name = bitstream[9:-3]
            program_name   = program[7:-4]

            bitstream_file = directory + app + "/bitstreams/" + bitstream
            program_file   = directory + app + "/inputs/" + program 
            tensor_file    = directory + app + "/inputs/tensor" + program[7:]

            output_dir     = "jssc_outputs/" + app + "_bit_" + bitstream_name + "_program_" + program_name 

            os.system("./lego_onyx_codegen.sh " + program_file + " " + tensor_file + " " + bitstream_file + " " + design_meta_file + " " + reg_write_file + " " + output_dir)

    


