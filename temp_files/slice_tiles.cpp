#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <boost/format.hpp>

using namespace std;

int load_vector(std::vector<int> &vec, ifstream &input_file){
    int val;
    while(input_file >> val){
        vec.push_back(val);
    }
    return 0;
}

int write_vector(std::vector<int> &vec, ofstream &output_file){
    for(int i = 0; i < vec.size(); i++){
        output_file << vec[i] << "\n";
    }
    return 0;
}

int tile_pack(int **in_ptrs, int index){

    

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
					tile_vals.push_back(crd4[l]);
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

    ofstream output_file1("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_pos_0_0.txt");
    write_vector(tile_pos1, output_file1);

    ofstream output_file2("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_crd_0_0.txt");
    write_vector(tile_crd1, output_file2);

    ofstream output_file3("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_pos_0_1.txt");
    write_vector(tile_pos2, output_file3);

    ofstream output_file4("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_crd_0_1.txt");
    write_vector(tile_crd2, output_file4);

    ofstream output_file5("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_pos_1_0.txt");
    write_vector(tile_pos3, output_file5);

    ofstream output_file6("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_crd_1_0.txt");
    write_vector(tile_crd3, output_file6);

    ofstream output_file7("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_pos_1_1.txt");
    write_vector(tile_pos4, output_file7);

    ofstream output_file8("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_crd_1_1.txt");
    write_vector(tile_crd4, output_file8);

    ofstream output_file9("tensors/lego_test_tiles/tiled_CSF_c_jk/tile_tiled_csf_data.txt");
    write_vector(tile_vals, output_file9);
	
	return 0;
}

int main(){

    std::vector<int> T1_pos; 
    std::vector<int> T1_crd;
    std::vector<int> T2_pos;
    std::vector<int> T2_crd;
    std::vector<int> T3_pos;
    std::vector<int> T3_crd;
    std::vector<int> T4_pos;
    std::vector<int> T4_crd;
    std::vector<int> T5_pos;
    std::vector<int> T5_crd;
    std::vector<int> T6_pos;
    std::vector<int> T6_crd;
    std::vector<int> T_vals;

    ifstream input_file1("lego_scratch/tensor_C/tcsf_pos1.txt");
    load_vector(T1_pos, input_file1);

    ifstream input_file2("lego_scratch/tensor_C/tcsf_crd1.txt");
    load_vector(T1_crd, input_file2);

    ifstream input_file3("lego_scratch/tensor_C/tcsf_pos2.txt");
    load_vector(T2_pos, input_file3);

    ifstream input_file4("lego_scratch/tensor_C/tcsf_crd2.txt");
    load_vector(T2_crd, input_file4);

    ifstream input_file5("lego_scratch/tensor_C/tcsf_pos3.txt");
    load_vector(T3_pos, input_file5);

    ifstream input_file6("lego_scratch/tensor_C/tcsf_crd3.txt");
    load_vector(T3_crd, input_file6);

    ifstream input_file7("lego_scratch/tensor_C/tcsf_pos4.txt");
    load_vector(T4_pos, input_file7);

    ifstream input_file8("lego_scratch/tensor_C/tcsf_crd4.txt");
    load_vector(T4_crd, input_file8);

    ifstream input_file9("lego_scratch/tensor_C/tcsf_pos5.txt");
    load_vector(T5_pos, input_file9);

    ifstream input_file10("lego_scratch/tensor_C/tcsf_crd5.txt");
    load_vector(T5_crd, input_file10);

    ifstream input_file11("lego_scratch/tensor_C/tcsf_pos6.txt");
    load_vector(T6_pos, input_file11);

    ifstream input_file12("lego_scratch/tensor_C/tcsf_crd6.txt");
    load_vector(T6_crd, input_file12);

    ifstream input_file13("lego_scratch/tensor_C/tcsf_vals.txt");
    load_vector(T_vals, input_file13);

    int **tensor_ptrs = (int**)malloc(13 * sizeof(int*));

    

    int *T1_pos_ptr = T1_pos.data();
    int *T1_crd_ptr = T1_crd.data();
    int *T2_pos_ptr = T2_pos.data();
    int *T2_crd_ptr = T2_crd.data();
    int *T3_pos_ptr = T3_pos.data();
    int *T3_crd_ptr = T3_crd.data();
    int *T4_pos_ptr = T4_pos.data();
    int *T4_crd_ptr = T4_crd.data();
    int *T5_pos_ptr = T5_pos.data();
    int *T5_crd_ptr = T5_crd.data();
    int *T6_pos_ptr = T6_pos.data();
    int *T6_crd_ptr = T6_crd.data();
    int *T_vals_ptr = T_vals.data();

    *(tensor_ptrs + 0) = T1_pos_ptr;
    *(tensor_ptrs + 1) = T1_crd_ptr;
    *(tensor_ptrs + 2) = T2_pos_ptr;
    *(tensor_ptrs + 3) = T2_crd_ptr;
    *(tensor_ptrs + 4) = T3_pos_ptr;
    *(tensor_ptrs + 5) = T3_crd_ptr;
    *(tensor_ptrs + 6) = T4_pos_ptr;
    *(tensor_ptrs + 7) = T4_crd_ptr;
    *(tensor_ptrs + 8) = T5_pos_ptr;
    *(tensor_ptrs + 9) = T5_crd_ptr;
    *(tensor_ptrs + 10) = T6_pos_ptr;
    *(tensor_ptrs + 11) = T6_crd_ptr;
    *(tensor_ptrs + 12) = T_vals_ptr;

    tile_pack(tensor_ptrs, 1);

    return 0; 
}