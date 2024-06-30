def main_gen_header_files(file):

    file.write("#include <stdio.h>\n")
    file.write("#include <stdlib.h>\n")
    file.write("#include \"diag/trace.h\"\n")
    file.write("#include \"amberm3vx_hal.h\"\n")
    file.write("#include \"glb.h\"\n")
    file.write("#include \"glc.h\"\n")
    file.write("#include \"memory.h\"\n")
    file.write("#include \"define.h\"\n")
    file.write("\n")

def main_spec_header_files(file, app_name):

    file.write("#include \"" + app_name + "_script.h\"\n")
    file.write("#include \"" + app_name + "_input_script.h\"\n")
    file.write("#include \"" + app_name + "_unrolling.h\"\n")
    file.write("#include \"" + app_name + "_reg_write.h\"\n")
    file.write("#include \"" + app_name + "_gold.h\"\n")
    file.write("\n")

def main_block_1(file):
    
    file.write("HAL_PtfmCtrl_t PtfmCtl;\n")
    file.write("\n")
    file.write("int main(int argc, char* argv[])\n")
    file.write("{\n")
    file.write("    HAL_UNUSED(argc);\n")
    file.write("    HAL_UNUSED(argv);\n")
    file.write("\n")
    file.write("    // Send a greeting to the trace device\n")
    file.write("    int status = HAL_PtfmCtrl_Initialize( & PtfmCtl);\n")
    file.write("    trace_printf(\"Status \\n\");\n")
    file.write("\n")
    file.write("    u32 cgra_mask = (1 << AHASOC_PCTRL_CGRA_Pos);\n")
    file.write("    u32 sys_mask = (1 << AHASOC_PCTRL_SYS_Pos);\n")
    file.write("\n")
    file.write("\n")
    file.write("    // Slower clocks for configuration\n")
    file.write("    status = HAL_PtfmCtrl_SelectClock( & PtfmCtl, cgra_mask, 0); \n")
    file.write("    status = HAL_PtfmCtrl_SelectClock( & PtfmCtl, sys_mask, 3); \n")
    file.write("    status = HAL_PtfmCtrl_DisableCG( & PtfmCtl, cgra_mask);\n")
    file.write("    status = HAL_PtfmCtrl_ClearReset( & PtfmCtl, cgra_mask);\n")
    file.write("\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_CGRA_STALL_R, 0xFFFF);\n")
    file.write("\n")
    file.write("    trace_printf(\"Config App\\n\\n\");\n")
    file.write("\n")
    file.write("    for (int config = 0; config < app_size; config++){\n")
    file.write("        HAL_Cgra_Tile_WriteReg(app_addrs_script[config], app_datas_script[config]);\n")
    file.write("    }\n")
    file.write("\n")
    file.write("    trace_printf(\"\\nCheck Config\\n\\n\");\n")
    file.write("    for (int config = 0; config < app_size; config++){\n")
    file.write("        uint32_t read_data = HAL_Cgra_Tile_ReadReg(app_addrs_script[config]);\n")
    file.write("        uint32_t addr = app_addrs_script[config];\n")
    file.write("        uint32_t gold = app_datas_script[config];\n")
    file.write("\n")
    file.write("        if ( read_data != gold){\n")
    file.write("            trace_printf(\"config error: %d \", config);\n")
    file.write("            trace_printf(\"address: %lx \", addr);\n")
    file.write("            trace_printf(\"read_data %lx \", read_data);\n")
    file.write("            trace_printf(\"gold data %lx\\n\", gold);\n")
    file.write("        }\n")
    file.write("    }\n")
    file.write("\n")
    file.write("\n")
    file.write("    // Faster clocks for App\n")
    file.write("    status = HAL_PtfmCtrl_SelectClock( & PtfmCtl, sys_mask, 1); // 2^2 = 4 60/4 = 15\n")

def main_block_2(file, mapping_dict, op_list):

    file.write("    uint16_t* input_read_base = AHASOC_CGRA_DATA_BASE;\n")
    
    num_tiles = 0
    for op in op_list:
        num_tiles += len(mapping_dict[op]) 

    file.write("\n")
    for i in range(num_tiles):
        file.write("    input_read_base = AHASOC_CGRA_DATA_BASE + 0x40000 * " + str(i) + ";\n")
        file.write("    trace_printf(\"first location: %lx\\n\", input_read_base[0]);\n")

    file.write("    trace_printf(\"\\nCONFIG GLB\\n\");\n") 
    file.write("    app_glb_config();\n")
    file.write("\n")
    file.write("    trace_printf(\"\\nAPP Prep\\n\");\n")
    file.write("\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_GLB_FLUSH_CROSSBAR_R, 0);\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_CGRA_STALL_R, 0x0);\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_GLOBAL_IER_R, 1);\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_STRM_F2G_IER_R, 0xffff);\n")
    file.write("    HAL_Cgra_Glc_WriteReg(GLC_STRM_G2F_IER_R, 0xffff);\n")
    file.write("\n")
    file.write("    trace_printf(\"\\n** Run code-gen  **\\n\");\n")
    file.write("\n")
    file.write("    const uint32_t start_addr = 0x0;\n")
    file.write("    const uint32_t read_start_addr = 0x20000;\n")

def main_block_3(file, mapping_dict, dest):

    out_tensor_dim = len(mapping_dict[dest])
    for i in range(out_tensor_dim):
        curr_mapping = mapping_dict[dest][i]    
        file.write("    uint16_t* output_read_base" + str(i) + " = (uint16_t*) (AHASOC_CGRA_DATA_BASE + read_start_addr + 0x40000*" + str(curr_mapping) + ");\n")
    file.write("\n")

    for i in range(out_tensor_dim - 1):
        file.write("    int " + dest + "_mode_" + str(i) + "_idx = 0;\n")
    file.write("    int " + dest + "_mode_vals_idx = 0;\n")
    file.write("\n")

    file.write("    int size;\n")
    for i in range(out_tensor_dim - 1):
        file.write("    int " + dest + "_mode_" + str(i) + "_size;\n")
    file.write("    int " + dest + "_mode_vals_size;\n")
    file.write("\n")

    file.write("    uint32_t cycles = 0;\n")    
    file.write("\n")
    file.write("    // 1. Enable trace and debug (if not enabled already)\n")
    file.write("    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;\n")
    file.write("\n")
    file.write("    // 2. Reset cycle counter\n")
    file.write("    DWT->CYCCNT = 0;\n")
    file.write("\n")
    file.write("    // 3. Start cycle counter\n")
    file.write("    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;\n")
    file.write("\n")
    file.write("\n")
    file.write("    for(int run=0; run < runs; run++){\n")
    file.write("\n")
    file.write("        // Update Input Pointers\n")
    file.write("        update_glb_input(run);\n")
    file.write("\n")
    file.write("        // Start Input/Output GLB Tiles\n")
    file.write("        HAL_Cgra_Glc_WriteReg(GLC_STREAM_START_PULSE_R, stream_pulse_f2g << 16 | stream_pulse_g2f); // pulsed reg.\n")
    file.write("\n")
    file.write("        // Wait for inputs to finish sending\n")
    file.write("        while(HAL_Cgra_Glc_ReadReg(GLC_STRM_G2F_ISR_R) != stream_pulse_g2f){\n")
    file.write("            //cnt++;\n")
    file.write("        }\n")
    file.write("        // Clear input statuses\n")
    file.write("        HAL_Cgra_Glc_WriteReg(GLC_STRM_G2F_ISR_R, stream_pulse_g2f);\n")
    file.write("\n")
    file.write("        // Wait for outputs to all fill in\n")
    file.write("        while(HAL_Cgra_Glc_ReadReg(GLC_STRM_F2G_ISR_R) != stream_pulse_f2g){\n")
    file.write("            //cnt++;\n")
    file.write("        }\n")
    file.write("\n")
    file.write("        // Clear output statuses\n")
    file.write("        HAL_Cgra_Glc_WriteReg(GLC_STRM_F2G_ISR_R, stream_pulse_f2g);\n")
    file.write("\n")
    file.write("        // Don't update for last tile\n")
    file.write("        if(run == runs-1){\n")
    file.write("            break;\n")
    file.write("        }\n")
    file.write("\n")

    file.write("        // Updating output pointers\n")
    file.write("        int size;\n")

    for i in range(out_tensor_dim - 1): 
        file.write("        size = output_read_base0[" + dest + "_mode_" + str(i) + "_idx];\n")
        file.write("        int " + dest + "_mode_" + str(i) + "_size = size + 1 + output_read_base0[" + dest + "_mode_" + str(i) + "_idx + size + 1] + 1;\n")
    
    file.write("        int " + dest + "_mode_vals_size = output_read_base" + str(out_tensor_dim) + "[" + dest + "_mode_vals_idx] + 1;\n")
    file.write("\n")

    for i in range(out_tensor_dim - 1):
        file.write("        " + dest + "_mode_" + str(i) + "_idx += " + dest + "_mode_" + str(i) + "_size;\n")
    file.write("        " + dest + "_mode_vals_idx += " + dest + "_mode_vals_size;\n")
    file.write("\n")

    for i in range(out_tensor_dim - 1):
        curr_mapping = mapping_dict[dest][i]
        file.write("        HAL_Cgra_Glb_WriteReg(0x100 * " + str(curr_mapping) + " + GLB_ST_DMA_HEADER_0_START_ADDR_R, 0x20000 + 0x40000 *" + str(curr_mapping) + " + " + dest + "_mode_" + str(i) + "_idx*2);\n")
    val_mapping = mapping_dict[dest][out_tensor_dim - 1]
    file.write("        HAL_Cgra_Glb_WriteReg(0x100 * " + str(val_mapping) + " + GLB_ST_DMA_HEADER_0_START_ADDR_R, 0x20000 + 0x40000 *" + str(val_mapping) + " + " + dest + "_mode_vals_idx*2);\n")
    file.write("\n")

    file.write("    }\n")   
    file.write("\n")
    file.write("    // 5. Stop cycle counter\n")
    file.write("    cycles = DWT->CYCCNT;\n")
    file.write("\n")
    file.write("    // 6. Disable cycle counter\n")
    file.write("    DWT->CTRL &= ~CoreDebug_DEMCR_TRCENA_Msk;\n")
    file.write("\n")
    file.write("    trace_printf(\"total cycles %d\\n\", cycles*2);\n")
    file.write("\n")
    file.write("    trace_printf(\"wait for app\\n\");\n")
    file.write("\n")
    file.write("    int errors = 0;\n")
    file.write("\n")
    file.write("    uint16_t* output_read_base = AHASOC_CGRA_DATA_BASE + 0x40000*0 + 0x20000;\n")

    for i in range(out_tensor_dim):
        file.write("        output_read_base = AHASOC_CGRA_DATA_BASE + 0x40000*" + str(i) + " + 0x20000;\n")
        file.write("        trace_printf(\"first location: %lx\\n\", output_read_base" + str(i) + "[0]);\n")

    file.write("    trace_printf(\"check gold data\\n\");\n")
    file.write("    errors = check_gold_data();\n")
    file.write("    trace_printf(\"total errors: %d\\n\", errors);\n")
    file.write("    return 0;\n")
    file.write("}\n")
