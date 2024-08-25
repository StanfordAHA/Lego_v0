#include "data_parser.h"
#include <csignal>
#include <iomanip>

int build_vec(std::vector<int> &vec, std::string file_path) {
    int val;

    ifstream input_file(file_path);   
	if (input_file.good()) {
		while(input_file >> val){
			vec.push_back(val);
		}	
	} else {
		throw std::runtime_error("Error: File not found: " + file_path);
	}

    return 0;
}

int build_vec_val(std::vector<float> &vec, std::string file_path) {
    float val;
    ifstream input_file(file_path);   
	if (input_file.good()) {
    	while(input_file >> setprecision(30) >> val){
			// FIXME: Temporary fix to avoid precision loss
			// TODO: Find a better way to set the digit precision
        	vec.push_back(val);
    	}
	} else {
		throw std::runtime_error("Error: File not found: " + file_path);
	}
    return 0;
}

int mode_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> mode_0){

	header_file << "const unsigned int app_tensor_" << tensor_name << "_mode_" << mode_name << "_data_size =  " << mode_0.size() << ";";
	header_file << "\n";		
	
	header_file << "uint16_t app_tensor_" << tensor_name << "_mode_" << mode_name << "_data[] " <<  "__attribute__((section(\".app_tensor_" <<  tensor_name << "_mode_" << mode_name << "_data\"))) = {";
	header_file << "\n";

	header_file << "0x" << std::hex << std::setw(3) << std::setfill('0') << mode_0[0];

	for(int i = 1; i < mode_0.size(); i++) {
		header_file << ", ";
		header_file << "0x" << std::hex << std::setw(3) << std::setfill('0') << mode_0[i];
	}
	header_file << "\n";
	header_file << "};"; 
	header_file << "\n";
	header_file << "\n";
	header_file << std::dec;

	return 0;
}

int val_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<float> mode_0, std::string dtype){

	if(dtype == "int"){
		header_file << "const unsigned int app_tensor_" << tensor_name << "_mode_" << mode_name << "_data_size =  " << mode_0.size() << ";";
		header_file << "\n";		
		
		header_file << "uint16_t app_tensor_" << tensor_name << "_mode_" << mode_name << "_data[] " <<  "__attribute__((section(\".app_tensor_" <<  tensor_name << "_mode_" << mode_name << "_data\"))) = {";
		header_file << "\n";

		header_file << "0x" << std::hex << std::setw(3) << std::setfill('0') << int(abs(mode_0[0]));

		for(int i = 1; i < mode_0.size(); i++) {
			header_file << ", ";
			header_file << "0x" << std::hex << std::setw(3) << std::setfill('0') << int(abs(mode_0[i]));
		}
		header_file << "\n";
		header_file << "};"; 
		header_file << "\n";
		header_file << "\n";
		header_file << std::dec;
	}
	
	// if(dtype == "float"){
		// Add functions to store float data to bfloat16 hex
	// 	}

	return 0;
}

int extent_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> extents_mode_0){
    header_file << "int tensor_" << tensor_name << "_mode_" << mode_name << "_extents" << "[" << extents_mode_0.size() << "] = {";
    header_file << extents_mode_0[0];
    for(int i = 1; i < extents_mode_0.size(); i++){
        header_file << ", " << extents_mode_0[i];
    }
    header_file << "};";
    header_file << "\n";

    return 0;
}

int rtl_mode_data_printer(std::vector<int> mode_0, std::string output_path, std::string tensor_name, std::string mode_type, std::string mode_name) {

	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_" + mode_name + "_" + mode_type;
	ofstream output_file(output_file_name.c_str());

	for (int pA = 0; pA < mode_0.size(); pA++) {
		output_file << mode_0[pA];
		output_file << "\n";
	}

	return 0;
}

int rtl_vals_data_printer(std::vector<float> mode_0, std::string output_path, std::string tensor_name) {

	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_vals";
	ofstream output_file(output_file_name.c_str());

	for (int pA = 0; pA < mode_0.size(); pA++) {
		// FIXME: Temporary fix to avoid precision loss
		// TODO: Find a better way to set the digit precision
		output_file << std::fixed << setprecision(30) << mode_0[pA];
		output_file << "\n";
	}

	// TODO: Store integer values to file if dtype is integer 
	// Propogate data type 


	return 0;
}

int rtl_size_data_printer_1(std::string output_path, std::string tensor_name, int dim1) {

	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_shape";
	ofstream output_file(output_file_name.c_str());

	output_file << dim1 << "\n";

	return 0;
}

int rtl_size_data_printer_2(std::string output_path, std::string tensor_name, int dim1, int dim2) {

	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_shape";
	ofstream output_file(output_file_name.c_str());

	output_file << dim1 << "\n";
	output_file << dim2 << "\n";

	return 0;
}

int rtl_size_data_printer_3(std::string output_path, std::string tensor_name, int dim1, int dim2, int dim3) {
	
	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_shape";
	ofstream output_file(output_file_name.c_str());

	output_file << dim1 << "\n";
	output_file << dim2 << "\n";
	output_file << dim3 << "\n";

	return 0;
}

int output_subtile_printer(float *op_vals, int output_subtile_size, int curr_subtile_num, ofstream &output_gold_file, std::string dtype) {

	if(dtype == "int"){

    	output_gold_file << "const uint16_t gold_" << curr_subtile_num << "_[" << output_subtile_size << "] = {";

    	for (int pA = 0; pA < output_subtile_size; pA++) {
        	output_gold_file << int(op_vals[pA]);
        	if(pA != output_subtile_size - 1){
            	output_gold_file << ", ";
        	}
    	} 
    	output_gold_file << "};\n";
	} 

	// if(dtype == "float"){
	// 	Float processing 
	// }

    return 0;
}

int subtile_paths_printer(const std::vector<std::string> &subtile_paths,
						  const std::string &output_dir,
						  const std::string &kernel_name, 
						  const int &batch_size) {
	
	int batch_idx = 0;
	for (int i = 0; i < subtile_paths.size(); i += batch_size) {
		std::string subtile_paths_file_path = output_dir + "/" + kernel_name + "/subtile_paths_" + std::to_string(batch_idx) + ".toml";
		std::ofstream subtile_paths_file;
		subtile_paths_file.open(subtile_paths_file_path, std::ios::out);
		
		if (!subtile_paths_file) {
			std::cerr << "Error: Cannot open file " << subtile_paths_file_path << "for writing" << std::endl;
			return 1;
		}

		// prefix fields required by comal
		subtile_paths_file << "[sam_config]" << "\n";
		subtile_paths_file << "name = \"" << kernel_name << "\"\n";
		subtile_paths_file << "sam_path = [ \n";

		std::string path_prefix = "output/" + kernel_name + "/";

		for (int j = 0; j < batch_size && i+j < subtile_paths.size(); j++) {
			std::string subtile_path = subtile_paths[i+j];
			std::string::size_type i = subtile_path.find(path_prefix);
			if (i != std::string::npos) {
				subtile_path.erase(i, path_prefix.length());
			}
			subtile_paths_file << "    \"" << subtile_path << "\",\n";
		}

		subtile_paths_file << "    ]";
		subtile_paths_file.close();
		batch_idx++;
	}

	return 0;
}

int header_meta_data(ofstream &header_file, std::string label, int max_run){
	header_file << "int runs" << label << " = " << max_run << ";" << "\n";
	return 0; 
} 

int header_check_gold(ofstream &output_gold_file, int output_subtile_size){
	output_gold_file << "#define AHASOC_CGRA_DATA_BASE    (0x20400000UL)  /*!< (CGRA DATA ) Base Address */" << "\n";

	output_gold_file << "\n"; 
	
	output_gold_file << "const uint16_t check_0_[" << output_subtile_size << "] = {0";

	for(int i = 0; i < output_subtile_size - 1; i++){
		output_gold_file << ", 0";
	}

	output_gold_file << "};" << "\n";
	output_gold_file << "\n"; 

	return 0;
}

int header_subtile_dim_decl(ofstream &header_file, int dim_id, int dim_size){
	header_file << "#define STILE_DIM" << dim_id << " " << dim_size << "\n";
	return 0;
}

int codegen_check_gold_head(ofstream &output_gold_file, int max_run, int tensor_dim, int unroll){
	output_gold_file << "\n"; 
	output_gold_file << "uint16_t check_gold_data(){" << "\n";
	output_gold_file << "\n"; 
	output_gold_file << "    uint16_t size; " << "\n";
	output_gold_file << "    uint16_t err = 0;" << "\n";
	for(int i = 0; i < tensor_dim; i++){
		output_gold_file << "    uint16_t mode" << i << "_idx = 0;" << "\n";
	}
	output_gold_file << "    uint16_t vals_idx = 0;" << "\n";	

	if(unroll){
		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "    uint16_t mode" << i << "_idx_unroll = 0;" << "\n";
		}
		output_gold_file << "    uint16_t vals_idx_unroll = 0;" << "\n";	
	}

	output_gold_file << "\n"; 
	output_gold_file << "    const uint32_t read_start_addr = 0x20000;" << "\n";

	output_gold_file << "\n";
	output_gold_file << "    for(uint16_t run = 0; run < " << max_run << "; run++){" << "\n";
	output_gold_file << "\n"; 
	output_gold_file << "        uint16_t * gold_ptr;" << "\n";
	output_gold_file << "        uint16_t * check_ptr;" << "\n";
	output_gold_file << "        switch(run){" << "\n";

	for(int i = 0; i < max_run; i++){
		output_gold_file << "            case " << i << ":" << "\n";
		output_gold_file << "                gold_ptr = gold_" << i << "_;" << "\n";
		output_gold_file << "                check_ptr = check_0_; " << "\n";
		output_gold_file << "                break;" << "\n";
	}
	output_gold_file << "            default:" << "\n";
	output_gold_file << "                break;" << "\n";
	output_gold_file << "        }\n"; 
	output_gold_file << "\n"; 

	return 0;
} 

int codegen_check_gold_unroll_ifdef_open(ofstream &output_gold_file, int select){

	if(select == 0){
		output_gold_file << "        if(runs % 1 == 0){" << "\n";
	}

	if(select == 1){
		output_gold_file << "        if(run % 2 == 0){" << "\n"; 
	}

	if(select == 2){
		output_gold_file << "        if(run % 2 == 1){" << "\n"; 
	}

	return 0; 
}

int codegen_check_gold_outmap(ofstream &output_gold_file, std::string base_id, std::string tile_id){
	output_gold_file << "            uint16_t * read_base_" << base_id << " = (uint16_t*) (AHASOC_CGRA_DATA_BASE + read_start_addr + " << tile_id << " * 0x40000);" << "\n";
	return 0; 
}

int codegen_check_gold_outmap_unroll(ofstream &output_gold_file, std::string base_id, std::string tile_id){
	output_gold_file << "            uint16_t * read_base_" << base_id << " = (uint16_t*) (AHASOC_CGRA_DATA_BASE + read_start_addr + " << tile_id << " * 0x40000 + 0x40000 * 8);" << "\n";
	return 0; 
}

int codegen_check_gold_tail(ofstream &output_gold_file, int max_run, int tensor_dim, std::string type){
	
	
	if(tensor_dim > 0) {
		output_gold_file << "\n"; 
		output_gold_file << "            size = read_base_0[mode0_idx" << type << "];" << "\n";
		output_gold_file << "            uint16_t mode0_size = size + 1 + read_base_0[mode0_idx" << type << " + size + 1] + 1;" << "\n";
		output_gold_file << "            uint16_t mode0_stream_size = read_base_0[mode0_idx" << type << " + size + 1];" << "\n";
		output_gold_file << "            uint16_t mode0_base = size + 1 + 1;" << "\n";

		for(int i = 1; i < tensor_dim; i++){
			output_gold_file << "\n"; 
			output_gold_file << "            size = read_base_" << i << "[mode" << i << "_idx" << type << "];" << "\n";
			output_gold_file << "            uint16_t mode" << i << "_base = size + 1 + 1;" << "\n";
			output_gold_file << "            uint16_t mode" << i << "_size = size + 1 + read_base_" << i << "[mode" << i << "_idx" << type << " + size + 1] + 1;" << "\n";
		}

		output_gold_file << "            uint16_t vals_size = read_base_" << tensor_dim << "[vals_idx" << type <<"] + 1;" << "\n";

		output_gold_file << "\n"; 
		output_gold_file << "            uint16_t x0;" << "\n";

		for(int i = 1; i < tensor_dim; i++){
			output_gold_file << "            uint16_t x" << i << ";" << "\n";
			output_gold_file << "            uint16_t x" << i << "_dim;" << "\n";
			output_gold_file << "            uint16_t x" << i << "_idx = 0;" << "\n";
		}

		output_gold_file << "\n"; 

		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "            for(uint16_t i" << i << " = 0; i" << i << " < STILE_DIM" << i <<  "; i" << i << "++){" << "\n";
			for(int j = 0; j < i + 1; j++){
				output_gold_file << "    ";
			}
		}

		std::string id; 
		std::string id_x; 

		id = ""; 

		for(int i = 0; i < tensor_dim; i++){
			id += "i" + std::to_string(i);
			for(int j = i + 1; j < tensor_dim; j++){
				id += " * STILE_DIM" + std::to_string(j);
			}
			if(i != tensor_dim - 1){
				id += " + ";
			}
		}

		output_gold_file << "            check_ptr[" << id << "] = 0;" << "\n";

		for(int i = 0; i < tensor_dim; i++){
			for(int j = 0; j < tensor_dim - i; j++){
				output_gold_file << "    "; 
			}
			output_gold_file << "        }" << "\n";
		}

		output_gold_file << "\n"; 

		id_x = "";
		for(int i = 0; i < tensor_dim; i++){
			id_x += "x" + std::to_string(i);
			for(int j = i + 1; j < tensor_dim; j++){
				id_x += " * STILE_DIM" + std::to_string(j);
			}
			if(i != tensor_dim - 1){
				id_x += " + ";
			}
		}

		int i  = 0;
		output_gold_file << "            for(uint16_t i" << i << " = 0; i" << i << " < mode" << i << "_stream_size; i" << i << "++){" << "\n";
		output_gold_file << "                x" << i << " = read_base_" << i << "[mode" << i << "_idx" << type << "  + mode" << i << "_base + i" << i << "];" << "\n";

		if(tensor_dim > 1) {
			i++;
			output_gold_file << "                x" << i << "_dim = read_base_" << i << "[mode" << i << "_idx" << type <<"  + i" << i - 1 << " + 2] - read_base_" << i << "[mode" << i << "_idx" << type <<"  + i" << i - 1 << " + 1];" << "\n";

			for(int i = 1; i < tensor_dim; i++){
				for(int j = 0; j < i; j++){
					output_gold_file << "    ";
				}
				output_gold_file << "            for(uint16_t i" << i << " = 0; i" << i << " < x" << i << "_dim; i" << i << "++){" << "\n";
				for(int j = 0; j < i; j++){
					output_gold_file << "    ";
				}
				output_gold_file << "                x" << i << " = read_base_" << i << "[mode" << i << "_idx" << type <<" + mode" << i << "_base + x" << i << "_idx + i" << i << "];" << "\n";
				if(i == tensor_dim - 1){
					for(int j = 0; j < i; j++){
						output_gold_file << "    ";
					}
					output_gold_file << "                check_ptr[" << id_x << "] = read_base_" << tensor_dim << "[vals_idx" << type <<" + x" << i << "_idx + " << "i" << i << " + 1];" << "\n";
				}
				else{
					int j = i + 1; 
					for(int k = 0; k < i; k++){
						output_gold_file << "    ";
					}
					output_gold_file << "                x" << j << "_dim = read_base_" << j << "[mode" << j << "_idx" << type <<"  + i" << j - 1 << " + 2] - read_base_" << j << "[mode" << j << "_idx" << type <<" + i" << j - 1 << " + 1];" << "\n";
				}
			}
		}
		else{
			output_gold_file << "                check_ptr[" << id_x << "] = read_base_" << tensor_dim << "[vals_idx" << type <<" + " << "i" << i << " + 1];\n";
		}

		for(int i = tensor_dim - 1; i > 0; i--){
			for(int j = 0; j < i; j++){
				output_gold_file << "    "; 
			}
			output_gold_file << "            }" << "\n";
			for(int j = 0; j < i; j++){
				output_gold_file << "    "; 
			}
			output_gold_file << "            x" << i << "_idx += x" << i << "_dim;" << "\n";
		}

		output_gold_file << "            }" << "\n";
		output_gold_file << "\n";

		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "            for(uint16_t i" << i << " = 0; i" << i << " < STILE_DIM" << i <<  "; i" << i << "++){" << "\n";
			for(int j = 0; j < i + 1; j++){
				output_gold_file << "    "; 
			}
		}

		output_gold_file << "            if(check_ptr[" << id << "] != gold_ptr[" << id << "]){" << "\n";

		for(int j = 0; j < tensor_dim; j++){
			output_gold_file << "    ";
		}
		output_gold_file << "                trace_printf(\"error! tile: %d, "; 
		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "i" << i << ": %d ";
		}
		output_gold_file << "gold_ptr:%d check_ptr:%d\\n\", run, ";
		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "i" << i << ", ";
		}

		output_gold_file << "gold_ptr[" << id << "], check_ptr[" << id << "]);" << "\n";
		
		for(int j = 0; j < tensor_dim; j++){
			output_gold_file << "    ";
		}
		output_gold_file << "                err++;" << "\n";

		for(int i = 0; i < tensor_dim + 1; i++){
			for(int j = 0; j < tensor_dim - i; j++){
				output_gold_file << "    ";
			}
			output_gold_file << "            }" << "\n";
		}

		for(int i = 0; i < tensor_dim; i++){
			output_gold_file << "            mode" << i << "_idx" << type <<" += mode" << i << "_size;" << "\n";
		}

		output_gold_file << "            vals_idx" << type <<" += vals_size;" << "\n";
		output_gold_file << "        }" << "\n";
	}
	else{
		output_gold_file << "            uint16_t vals_size = read_base_0[vals_idx" << type <<"] + 1;" << "\n";
		output_gold_file << "            if(read_base_0[vals_idx" << type <<" + 1] != gold_ptr[0]){" << "\n"; 
		output_gold_file << "                trace_printf(\"error! tile: %d, gold_ptr:%d check_ptr:%d\\n\", run, gold_ptr[0], read_base_0[vals_idx" << type <<"  + 1]);" << "\n"; 
		output_gold_file << "                err++;" << "\n";
		output_gold_file << "            }" << "\n";
		output_gold_file << "            vals_idx" << type <<" += vals_size;" << "\n";
		output_gold_file << "        }" << "\n";
	}
	output_gold_file << "\n";

	return 0;
}

int codegen_check_gold_ret(ofstream &output_gold_file){
	output_gold_file << "    }\n";
	output_gold_file << "    return err;\n";
	output_gold_file << "}\n";
	return 0;
}