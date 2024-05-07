#include <stdlib.h>
#include <stdio.h>

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <boost/format.hpp>


using namespace std;

int stile_unpack(std::vector<int> &mode_0, std::vector<int> &mode_1, std::vector<int> &mode_vals, std::vector<int> &extents_mode_0, std::vector<int> &extents_mode_1, std::vector<int> &extents_mode_vals, int **in_ptrs, int index) {

	int *pos1 = (int*)in_ptrs[0];
	int *crd1 = (int*)in_ptrs[1];
	int *pos2 = (int*)in_ptrs[2];
	int *crd2 = (int*)in_ptrs[3];
	int *vals = (int*)in_ptrs[4];

	int stile_pos1_len = 2;	
	int stile_pos2_len = pos1[index + 1] - pos1[index] + 1;
	int stile_crd1_len = pos1[index + 1] - pos1[index];
	int stile_crd2_len = pos2[pos1[index + 1]] - pos2[pos1[index]];
	int stile_vals_len = pos2[pos1[index + 1]] - pos2[pos1[index]];

	mode_0.push_back(stile_pos1_len);
	mode_0.push_back(pos1[index] - pos1[index]);
	mode_0.push_back(pos1[index + 1] - pos1[index]);
	mode_0.push_back(stile_crd1_len);

    for(int i = pos1[index]; i < pos1[index + 1]; i++) {
		mode_0.push_back(crd1[i]);
    }

	mode_1.push_back(stile_pos2_len); 
    for(int i = pos1[index]; i <= pos1[index + 1]; i++) {
        mode_1.push_back(pos2[i] - pos2[pos1[index]]);
    }

	mode_1.push_back(stile_crd2_len);
	mode_vals.push_back(stile_vals_len);

	for(int i = pos1[index]; i < pos1[index + 1]; i++) {
        for(int j = pos2[i]; j < pos2[i + 1]; j++) {
            mode_1.push_back(crd2[j]);
            mode_vals.push_back(1);
        }
    }

	extents_mode_0.push_back(extents_mode_0.back() + stile_pos1_len + stile_crd1_len + 2); 
	extents_mode_1.push_back(extents_mode_1.back() + stile_pos2_len + stile_crd2_len + 2);
	extents_mode_vals.push_back(extents_mode_vals.back() + stile_vals_len + 1);

	return 0;
}

int extent_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> extents_mode_0){
	header_file << "int tensor_" << tensor_name << "_mode_" << mode_name << "_extents[" << extents_mode_0.size() << "] = {";
	for(int i = 0; i < extents_mode_0.size() - 1; i++) {
		header_file << extents_mode_0[i] << ", ";
	}
	header_file <<  extents_mode_0[extents_mode_0.size() - 1] << "};" << std::endl;

	return 0;
}

int mode_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> mode_0){

	
	header_file << "const unsigned int app_tensor_" << tensor_name << "_mode_" << mode_name << "_data_size =  " << mode_0.size() << ";";
	header_file << "\n";		
	
	header_file << "uint16_t app_tensor_" << tensor_name << "_mode_" << mode_name << "_data[] " <<  "((section(\".app_tensor_" <<  tensor_name << "_mode_" << mode_name << "_data\"))) = {";
	header_file << "\n";

	boost::format hex03("%03x");
	header_file << hex03 % mode_0[0];

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

int pos_crd_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_num, std::string mode_name, std::vector<int> pos_crd_vec){

	header_file << "int " << tensor_name << mode_num << "_" << mode_name << "[" << pos_crd_vec.size() << "] = {";

	header_file << pos_crd_vec[0];	

	for(int i = 1; i < pos_crd_vec.size(); i++) {
		header_file << ", ";
		header_file << pos_crd_vec[i];
	}

	header_file << "};";
	header_file << "\n";

	return 0;

}

int glb_tile_pack(int **in_ptrs, int index){

	int *pos1 = (int*)in_ptrs[4];
	int *crd1 = (int*)in_ptrs[5];
	int *pos2 = (int*)in_ptrs[6];
	int *crd2 = (int*)in_ptrs[7];
	int *pos3 = (int*)in_ptrs[8];
	int *crd3 = (int*)in_ptrs[9];
	int *pos4 = (int*)in_ptrs[10];
	int *crd4 = (int*)in_ptrs[11];
	int *vals = (int*)in_ptrs[12];

	std::vector<int> tile_pos1; 
	std::vector<int> tile_crd1;
	std::vector<int> tile_pos2;
	std::vector<int> tile_crd2;
	std::vector<int> tile_pos3;
	std::vector<int> tile_crd3;
	std::vector<int> tile_pos4;
	std::vector<int> tile_crd4;
	std::vector<int> tile_vals;

	std::vector<int> mode_0;
	std::vector<int> mode_1;
	std::vector<int> mode_vals;
	std::vector<int> extents_mode_0;
	std::vector<int> extents_mode_1;
	std::vector<int> extents_mode_vals;

	tile_pos1.push_back(0);
	tile_pos1.push_back(pos1[index + 1] - pos1[index]);

    for(int i = pos1[index]; i < pos1[index + 1]; i++) {
        tile_crd1.push_back(crd1[i]);
        for(int j = pos2[i]; j < pos2[i + 1]; j++) {
			tile_crd2.push_back(crd2[j]);
            for(int k = pos3[j]; k < pos3[j + 1]; k++) {
                tile_crd3.push_back(crd3[k]);
                for(int l = pos4[k]; l < pos4[k + 1]; l++) {
					tile_crd4.push_back(crd4[l]);
					tile_vals.push_back(vals[l]);
            	}
            }
        }
    }

    for(int i = pos1[index]; i <= pos1[index + 1]; i++) {
		tile_pos2.push_back(pos2[i] - pos2[pos1[index]]);
    }

    for(int i = pos1[index]; i < pos1[index + 1]; i++) {
        for(int j = pos2[i]; j < pos2[i + 1]; j++) {
			tile_pos3.push_back(pos3[j] - pos3[pos2[pos1[index]]]);
        }
    }

	tile_pos3.push_back(pos3[pos2[pos1[index + 1]]] - pos3[pos2[pos1[index]]]);

    for(int i = pos1[index]; i < pos1[index + 1]; i++) {
        for(int j = pos2[i]; j < pos2[i + 1]; j++) {
            for(int k = pos3[j]; k < pos3[j + 1]; k++) {
				tile_pos4.push_back(pos4[k] - pos4[pos3[pos2[pos1[index]]]]);
            }
        }
    }

	tile_pos4.push_back(pos4[pos3[pos2[pos1[index + 1]]]] - pos4[pos3[pos2[pos1[index]]]]);

	extents_mode_0.push_back(0);
	extents_mode_1.push_back(0);
	extents_mode_vals.push_back(0);

	int *ptrs[5] = {tile_pos3.data(), tile_crd3.data(), tile_pos4.data(), tile_crd4.data(), tile_vals.data()};

	for(int i = 0; i < tile_crd2.size(); i++) {
        stile_unpack(mode_0, mode_1, mode_vals, extents_mode_0, extents_mode_1, extents_mode_vals, ptrs, i);
	}

	ofstream header_file1;
	header_file1.open("glb_meta_data.h");

	extent_printer(header_file1, "C", "0", extents_mode_0);
	extent_printer(header_file1, "C", "1", extents_mode_1);
	extent_printer(header_file1, "C", "vals", extents_mode_vals);

	pos_crd_printer(header_file1, "C", "1", "pos", tile_pos1);
	pos_crd_printer(header_file1, "C", "1", "crd", tile_crd1);
	pos_crd_printer(header_file1, "C", "2", "pos", tile_pos2);
	pos_crd_printer(header_file1, "C", "2", "crd", tile_crd2);
	
	ofstream header_file2;
	header_file2.open("glb_data.h");

	mode_data_printer(header_file2, "C", "0", mode_0);
	mode_data_printer(header_file2, "C", "1", mode_1);
	mode_data_printer(header_file2, "C", "vals", mode_vals);
	
	return 0;
}

int main(){

    int **B_ptrs;

	B_ptrs = (int**)malloc(sizeof(int*) * (13));

    std::vector<int> B1_pos_vec;
	std::vector<int> B1_crd_vec;
	std::vector<int> B2_pos_vec;
	std::vector<int> B2_crd_vec;
	std::vector<int> B3_pos_vec;
	std::vector<int> B3_crd_vec;
	std::vector<int> B4_pos_vec;
	std::vector<int> B4_crd_vec;
	std::vector<int> B5_pos_vec;
	std::vector<int> B5_crd_vec;
	std::vector<int> B6_pos_vec;
	std::vector<int> B6_crd_vec;
	std::vector<int> B_vals_vec;

    ifstream input_file1("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_0_0.txt");

	int temp; 
	while(input_file1 >> temp) {
		B1_pos_vec.push_back(temp);
	}
	
	ifstream input_file2("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_0_0.txt");
	while(input_file2 >> temp) {
		B1_crd_vec.push_back(temp);
	}

	ifstream input_file3("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_0_1.txt");
	while(input_file3 >> temp) {
		B2_pos_vec.push_back(temp);
	}

	ifstream input_file4("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_0_1.txt");
	while(input_file4 >> temp) {
		B2_crd_vec.push_back(temp);
	}

	ifstream input_file5("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_1_0.txt");
	while(input_file5 >> temp) {
		B3_pos_vec.push_back(temp);
	}
	ifstream input_file6("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_1_0.txt");
	while(input_file6 >> temp) {
		B3_crd_vec.push_back(temp);
	}

	ifstream input_file7("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_1_1.txt");
	while(input_file7 >> temp) {
		B4_pos_vec.push_back(temp);
	}

	ifstream input_file8("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_1_1.txt");
	while(input_file8 >> temp) {
		B4_crd_vec.push_back(temp);
	}

	ifstream input_file9("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_2_0.txt");
	while(input_file9 >> temp) {
		B5_pos_vec.push_back(temp);
	}

	ifstream input_file10("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_2_0.txt");
	while(input_file10 >> temp) {
		B5_crd_vec.push_back(temp);
	}

	ifstream input_file11("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_pos_2_1.txt");
	while(input_file11 >> temp) {
		B6_pos_vec.push_back(temp);
	}

	ifstream input_file12("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_crd_2_1.txt");
	while(input_file12 >> temp) {
		B6_crd_vec.push_back(temp);
	}

	ifstream input_file13("tensors/lego_test_tensors/tiled_CSF_c_jk/tiled_csf_data.txt");

	int temp_val;
	while(input_file13 >> temp_val) {
		B_vals_vec.push_back(temp_val);
	}

	int *B1_pos = B1_pos_vec.data();
	int *B1_crd = B1_crd_vec.data();
	int *B2_pos = B2_pos_vec.data();
	int *B2_crd = B2_crd_vec.data();
	int *B3_pos = B3_pos_vec.data();
	int *B3_crd = B3_crd_vec.data();
	int *B4_pos = B4_pos_vec.data();
	int *B4_crd = B4_crd_vec.data();
	int *B5_pos = B5_pos_vec.data();
	int *B5_crd = B5_crd_vec.data();
	int *B6_pos = B6_pos_vec.data();
	int *B6_crd = B6_crd_vec.data();
	int *B_vals = B_vals_vec.data();

	*(B_ptrs + 0) = B1_pos;
	*(B_ptrs + 1) = B1_crd;
	*(B_ptrs + 2) = B2_pos;
	*(B_ptrs + 3) = B2_crd;
	*(B_ptrs + 4) = B3_pos;
	*(B_ptrs + 5) = B3_crd;
	*(B_ptrs + 6) = B4_pos;
	*(B_ptrs + 7) = B4_crd;
	*(B_ptrs + 8) = B5_pos;
	*(B_ptrs + 9) = B5_crd;
	*(B_ptrs + 10) = B6_pos;
	*(B_ptrs + 11) = B6_crd;
	*(B_ptrs + 12) = B_vals;

	glb_tile_pack(B_ptrs, 1);

	return 0;
	
}




