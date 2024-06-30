import sys
import os 
import re

def unrolling(inputs, outputs, input_order, output_order, f, app_name):
    input_place_list = input_order
    output_place_list = output_order 

    checkpoint = 0
    f.write("#include \"glb.h\"\n")
    f.write("#include \"" + app_name + "_extents.h\"\n")
    f.write("int output_mask = 0b111;\n")
    f.write("\n")

    for idx, input_name in enumerate(inputs):
        input_name_str = input_name.replace("hw_", "")
        input_name_str = input_name_str.replace(".raw", "")
        f.write(f"int {input_name_str}_unroll = {len(input_place_list[idx])};\n")
        f.write(f"int {input_name_str}_unroll_array[{len(input_place_list[idx])}] = {{")
        input_str = ", ".join([str(elem) for elem in input_place_list[idx]])
        f.write(input_str)
        f.write(f"}};\n")
        f.write("\n")

    f.write("static void move_input_data()\n")
    f.write("{\n")
    for idx, input_name in enumerate(inputs):
        input_name_str = input_name.replace("hw_", "")
        input_name_str = input_name_str.replace(".raw", "")
        f.write(f"  write_glb_memory(0x40000 * ({input_name_str}_unroll_array[0]), (uint16_t * ) app_{input_name_str}_data, app_{input_name_str}_data_size / {input_name_str}_unroll, 0, {input_name_str}_unroll);\n")

        checkpoint = checkpoint + len(input_place_list[idx])
    f.write("}\n\n")

    # stream val calculations
    stream_pulse_g2f = 0
    stream_pulse_f2g = 0

    for io_in in input_place_list:
        stream_pulse_g2f |= (1 << io_in[0])
    for io_out in output_place_list:
        stream_pulse_f2g |= (1 << io_out[0])

    f.write(f"int stream_pulse_g2f = {hex(stream_pulse_g2f)};\n")
    f.write(f"int stream_pulse_f2g = {hex(stream_pulse_f2g)};\n\n")

    for idx, input_name in enumerate(inputs):
        input_name_str = input_name.replace("hw_", "")
        input_name_str = input_name_str.replace(".raw", "")

        f.write(f"int {input_name_str}_extents_sum = 0;\n")
        f.write(f"int {input_name_str}_extents_len;\n")

    f.write("\n")
    f.write("static void update_glb_input(int k)\n")
    f.write("{\n")
    for idx, input_name in enumerate(inputs):
        f.write("\n")
        input_name_str = input_name.replace("hw_", "")
        input_name_str = input_name_str.replace(".raw", "")
        f.write(f"  {input_name_str}_extents_sum = {input_name_str}_extents[2 * k] * 2;\n")
        f.write(f"  {input_name_str}_extents_len = {input_name_str}_extents[2 * k + 1] - {input_name_str}_extents[2 * k] - 2;\n")
        f.write(f"  HAL_Cgra_Glb_WriteReg(0x100 * ({input_name_str}_unroll_array[0]) + GLB_LD_DMA_HEADER_0_START_ADDR_R, 0x40000 * ({input_name_str}_unroll_array[0]) + {input_name_str}_extents_sum);\n")
        f.write(f"  HAL_Cgra_Glb_WriteReg(0x100 * ({input_name_str}_unroll_array[0]) + GLB_LD_DMA_HEADER_0_RANGE_0_R, {input_name_str}_extents_len);\n")
        f.write("\n")
    f.write("}\n")

if __name__ == '__main__':
    unrolling(inputs, outputs, input_order, output_order, app_name)

