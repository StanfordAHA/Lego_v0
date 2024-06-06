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

int build_vec_val(std::vector<double> &vec, std::string file_path) {
    double val;
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

	boost::format hex03("%03x");
	header_file << "0x" << hex03 % mode_0[0];

	for(int i = 1; i < mode_0.size(); i++) {
		header_file << ", ";
		header_file << "0x" << hex03 % mode_0[i];
	}
	header_file << "\n";
	header_file << "};"; 
	header_file << "\n";
	header_file << "\n";

	return 0;
}

int val_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<double> mode_0){

	
	header_file << "const unsigned int app_tensor_" << tensor_name << "_mode_" << mode_name << "_data_size =  " << mode_0.size() << ";";
	header_file << "\n";		
	
	header_file << "uint16_t app_tensor_" << tensor_name << "_mode_" << mode_name << "_data[] " <<  "__attribute__((section(\".app_tensor_" <<  tensor_name << "_mode_" << mode_name << "_data\"))) = {";
	header_file << "\n";

	boost::format hex03("%03x");
	header_file << "0x" << hex03 % int(mode_0[0]);

	for(int i = 1; i < mode_0.size(); i++) {
		header_file << ", ";
		header_file << "0x" << hex03 % int(mode_0[i]);
	}
	header_file << "\n";
	header_file << "};"; 
	header_file << "\n";
	header_file << "\n";

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

int rtl_vals_data_printer(std::vector<double> mode_0, std::string output_path, std::string tensor_name) {

	std::string output_file_name = output_path + "/tensor_" + tensor_name + "_mode_vals";
	ofstream output_file(output_file_name.c_str());

	for (int pA = 0; pA < mode_0.size(); pA++) {
		// FIXME: Temporary fix to avoid precision loss
		// TODO: Find a better way to set the digit precision
		output_file << setprecision(30) << mode_0[pA];
		output_file << "\n";
	}
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

int output_subtile_printer(double *op_vals, int output_subtile_size, int curr_subtile_num, ofstream &output_gold_file) {

    output_gold_file << "const uint16_t gold_" << curr_subtile_num << "_[" << output_subtile_size << "] = {";

    for (int pA = 0; pA < output_subtile_size; pA++) {
        output_gold_file << int(op_vals[pA]);
        if(pA != output_subtile_size - 1){
            output_gold_file << ", ";
        }
    }

    output_gold_file << "};\n";

    return 0;
}

int subtile_paths_printer(const std::vector<std::string> & subtile_paths, const int &batch_size) {
	
	int batch_idx = 0;
	for (int i = 0; i < subtile_paths.size(); i += batch_size) {
		std::string subtile_paths_file_path = "./subtile_paths_" + std::to_string(batch_idx) + ".toml";
		std::ofstream subtile_paths_file;
		subtile_paths_file.open(subtile_paths_file_path, std::ios::out);
		
		// prefix fields required by comal
		subtile_paths_file << "[sam_config]" << "\n";
		subtile_paths_file << "sam_path = [ \n";

		for (int j = 0; j < batch_size && i+j < subtile_paths.size(); j++) {
			subtile_paths_file << "    \"" << subtile_paths[i+j] << "\",\n";
		}

		subtile_paths_file << "    ]";
		subtile_paths_file.close();
		batch_idx++;
	}

	return 0;
}