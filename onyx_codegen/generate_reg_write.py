def generate_reg_write(input_reg_write_path, glb_tile_offset, glb_bank_offset):
    reg_write_input_list = []
    reg_write_output_list = []

    # TODO: app currently only uses up to 10 input glb tiles, need to change this to be more general
    for i in range(0, 10):
        input_glb_tile_offset = int(glb_tile_offset, 16) * i
        reg_write_input_list.append(f"0x{i}80, {hex(input_glb_tile_offset)} + {glb_tile_offset} * i")

    # TODO: app currently only uses up to 4 output glb tiles, need to change this to be more general
    for i in range(0, 4):
        ouput_glb_tile_offset = int(glb_tile_offset, 16) * i + int(glb_bank_offset, 16)
        reg_write_output_list.append(f"0x{i}1c, {hex(ouput_glb_tile_offset)} + {glb_tile_offset} * i")

    # replace the SoC function calls with the HAL function calls
    # also replace address and the data for input and output glb tiles  
    with open(input_reg_write_path, 'r') as file:
        data = file.read()
        data = data.replace('glb_config()', 'glb_config(int i)')
        for item in reg_write_input_list:
            data = data.replace(item, item)
        for item in reg_write_output_list:
            data = data.replace(item, item)
        data = data.replace('glb_reg_write(', 'HAL_Cgra_Glb_WriteReg(0x100 * i + ')

    return data

    