#include <stdlib.h>
#include <stdio.h>
#include <cstring>

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <boost/format.hpp>

using namespace std;

int cp_cgra_mem_cpy_sparse(int **ptrs, int **in_ptrs, int index) {

    int *out_pos1_ptr = (int*)ptrs[0];
    int *out_crd1_ptr = (int*)ptrs[1];
    int *out_pos2_ptr = (int*)ptrs[2];
    int *out_crd2_ptr = (int*)ptrs[3];
    double *out_vals = (double*)ptrs[4];

	int *pos1 = (int*)in_ptrs[4];
	int *crd1 = (int*)in_ptrs[5];
	int *pos2 = (int*)in_ptrs[6];
	int *crd2 = (int*)in_ptrs[7];
	int *vals = (int*)in_ptrs[8];

    out_pos1_ptr[0] = 0;
    out_pos1_ptr[1] = pos1[index + 1] - pos1[index];

    for(int i = pos1[index]; i < pos1[index + 1]; i++) {
        out_crd1_ptr[i - pos1[index]] = crd1[i];
        for(int j = pos2[i]; j < pos2[i + 1]; j++) {
            out_crd2_ptr[j - pos2[pos1[index]]] = crd2[j];
            out_vals[j - pos2[pos1[index]]] = vals[j];
        }
    }

    for(int i = pos1[index]; i <= pos1[index + 1]; i++) {
        out_pos2_ptr[i - pos1[index]] = pos2[i] - pos2[pos1[index]];
    }

	return 0;
    
}

int min(int a, int b){
    if(a < b){
        return a;
    }
    else{
        return b;
    }
}  

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


int cgra_gold(int **B_ptrs, int **C_ptrs, ofstream &header_file) {

  printf("Running now on cgra\n");
  int *B1_pos = (int*)B_ptrs[0];
  int *B1_crd = (int*)B_ptrs[1];
  int *B2_pos = (int*)B_ptrs[2];
  int *B2_crd = (int*)B_ptrs[3];
  double *B_vals = (double*)B_ptrs[4];

  int *C1_pos = (int*)C_ptrs[0];
  int *C1_crd = (int*)C_ptrs[1];
  int *C2_pos = (int*)C_ptrs[2];
  int *C2_crd = (int*)C_ptrs[3];
  double *C_vals = (double*)C_ptrs[4];


  int *A1_vals = (int*)malloc(sizeof(int) * 900);
  

  for (int32_t pA = 0; pA < (30 * 30); pA++) {
    A1_vals[pA] = 0;
  }

  int32_t iB; 


  for (int32_t iB = B1_pos[0]; iB < B1_pos[1]; iB++) {
    int32_t i = B1_crd[iB];
    int32_t kB = B2_pos[iB];
    int32_t pB2_end = B2_pos[(iB + 1)];
    int32_t kC = C1_pos[0];
    int32_t pC1_end = C1_pos[1];

	printf("pC1_end = %d\n", pC1_end);
    while (kB < pB2_end && kC < pC1_end) {
		printf("kC = %d\n", kC);
      int32_t kB0 = B2_crd[kB];
      int32_t kC0 = C1_crd[kC];
      int32_t k = min(kB0,kC0);

      if (kB0 == k && kC0 == k) {
        for (int32_t jC = C2_pos[kC]; jC < C2_pos[(kC + 1)]; jC++) {
            printf("Hi = %d\n", kC);
          int32_t j = C2_crd[jC];
          int32_t jA = i * 30 + j;
          A1_vals[jA] = A1_vals[jA] + 1;
        }
      }
      kB += (int32_t)(kB0 == k);
      kC += (int32_t)(kC0 == k);
    }
  }

  

  header_file << "int A1_vals[900] = {";
  header_file << A1_vals[0];

  for (int32_t pA = 1; pA < (30 * 30); pA++) {
	header_file << ", " << A1_vals[pA];
  }

  header_file << "};";
  header_file << "\n";

  return 0;
}

int subtile_slice(int **tensor_ptrs, int index, 
                    std::vector<int> &mode_0, std::vector<int> &mode_1, std::vector<int> &mode_vals, 
                    std::vector<int> &extents_mode_0, std::vector<int> &extents_mode_1, std::vector<int> &extents_mode_vals){

    int *pos1 = tensor_ptrs[4];
    int *crd1 = tensor_ptrs[5];
    int *pos2 = tensor_ptrs[6];
    int *crd2 = tensor_ptrs[7];
    int *vals = tensor_ptrs[8];

    
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
    
    if(extents_mode_0.size() == 1){
        
        extents_mode_0.push_back(stile_pos1_len + stile_crd1_len + 2);
        extents_mode_1.push_back(stile_pos2_len + stile_crd2_len + 2);
        extents_mode_vals.push_back(stile_vals_len + 1);
    }
    else{
        extents_mode_0[0] = extents_mode_0[1];
        extents_mode_1[0] = extents_mode_1[1];
        extents_mode_vals[0] = extents_mode_vals[1];

        extents_mode_0[1] = extents_mode_0[1] + stile_pos1_len + stile_crd1_len + 2;
        extents_mode_1[1] = extents_mode_1[1] + stile_pos2_len + stile_crd2_len + 2;
        extents_mode_vals[1] = extents_mode_vals[1] + stile_vals_len + 1;
    }

    B_mode0_start[id_store_B] = temp_extent_B[0];
                                B_mode0_end[id_store_B] = cg_extent_B[1];
                                B_mode1_start[id_store_B] = cg_extent_B[0];
                                B_mode1_end[id_store_B] = cg_extent_B[1];
                                B_mode_vals_start[id_store_B] = cg_extent_B[0];
                                B_mode_vals_end[id_store_B] = cg_extent_B[1]; 

	return 0;
}

int mode_data_printer(std::ofstream &header_file, std::string tensor_name, std::string mode_name, std::vector<int> mode_0){

	
	header_file << "const unsigned int app_tensor_" << tensor_name << "_mode_" << mode_name << "_data_size =  " << mode_0.size() << ";";
	header_file << "\n";		
	
	header_file << "uint16_t app_tensor_" << tensor_name << "_mode_" << mode_name << "_data[] " <<  "((section(\".app_tensor_" <<  tensor_name << "_mode_" << mode_name << "_data\"))) = {";
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

int ap_operate(int **B_ptrs, int **C_ptrs){ 

    int *B1_pos = B_ptrs[0];
    int *B1_crd = B_ptrs[1];
    int *B2_pos = B_ptrs[2];
    int *B2_crd = B_ptrs[3];
    int *B3_pos = B_ptrs[4];
    int *B3_crd = B_ptrs[5];
    int *B4_pos = B_ptrs[6];
    int *B4_crd = B_ptrs[7];
    int *B_vals = B_ptrs[8];

    int *C1_pos = C_ptrs[0];
    int *C1_crd = C_ptrs[1];
    int *C2_pos = C_ptrs[2];
    int *C2_crd = C_ptrs[3];
    int *C3_pos = C_ptrs[4];
    int *C3_crd = C_ptrs[5];
    int *C4_pos = C_ptrs[6];
    int *C4_crd = C_ptrs[7];
    int *C_vals = C_ptrs[8];

    printf("Running now on ap\n");

    int **stile_B_ptrs; 
    int **stile_C_ptrs;

    stile_B_ptrs = (int**)malloc(5 * sizeof(int*));
    stile_C_ptrs = (int**)malloc(5 * sizeof(int*));


    int *B1_pos_stile = (int*)malloc(2 * sizeof(int));
    int *B1_crd_stile = (int*)malloc(1000 * sizeof(int));
    int *B2_pos_stile = (int*)malloc(1000 * sizeof(int));
    int *B2_crd_stile = (int*)malloc(1000 * sizeof(int));
    int *B_vals_stile = (int*)malloc(1000 * sizeof(double));

    stile_B_ptrs[0] = B1_pos_stile;
    stile_B_ptrs[1] = B1_crd_stile;
    stile_B_ptrs[2] = B2_pos_stile;
    stile_B_ptrs[3] = B2_crd_stile;
    stile_B_ptrs[4] = B_vals_stile;

    int *C1_pos_stile = (int*)malloc(2 * sizeof(int));
    int *C1_crd_stile = (int*)malloc(1000 * sizeof(int));
    int *C2_pos_stile = (int*)malloc(1000 * sizeof(int));
    int *C2_crd_stile = (int*)malloc(1000 * sizeof(int));
    int *C_vals_stile = (int*)malloc(1000 * sizeof(double));

    stile_C_ptrs[0] = C1_pos_stile;
    stile_C_ptrs[1] = C1_crd_stile;
    stile_C_ptrs[2] = C2_pos_stile;
    stile_C_ptrs[3] = C2_crd_stile;
    stile_C_ptrs[4] = C_vals_stile;    

    std::vector<int> B_mode_0;
    std::vector<int> B_mode_1;
    std::vector<int> B_mode_vals;

    std::vector<int> C_mode_0;
    std::vector<int> C_mode_1;
    std::vector<int> C_mode_vals;

    std::vector<int> B_extents_mode_0;
    std::vector<int> B_extents_mode_1;
    std::vector<int> B_extents_mode_vals;

    std::vector<int> C_extents_mode_0;
    std::vector<int> C_extents_mode_1;
    std::vector<int> C_extents_mode_vals;

    std::vector<int> B_extents_mode_0_run;
    std::vector<int> B_extents_mode_1_run;
    std::vector<int> B_extents_mode_vals_run;

    std::vector<int> C_extents_mode_0_run;
    std::vector<int> C_extents_mode_1_run;
    std::vector<int> C_extents_mode_vals_run;

    B_extents_mode_0.push_back(0);
    B_extents_mode_1.push_back(0);
    B_extents_mode_vals.push_back(0);

    C_extents_mode_0.push_back(0);
    C_extents_mode_1.push_back(0);
    C_extents_mode_vals.push_back(0);

    int store_size = 64; 

    int *B_mode0_start = (int*)malloc(store_size * sizeof(int));
    int *B_mode1_start = (int*)malloc(store_size * sizeof(int));
    int *B_mode_vals_start = (int*)malloc(store_size * sizeof(int));

    int *B_mode0_end = (int*)malloc(store_size * sizeof(int));
    int *B_mode0_end = (int*)malloc(store_size * sizeof(int));
    int *B_mode1_end = (int*)malloc(store_size * sizeof(int));
    int *B_mode_vals_end = (int*)malloc(store_size * sizeof(int));

    int *C_mode0_start = (int*)malloc(store_size * sizeof(int));
    int *C_mode1_start = (int*)malloc(store_size * sizeof(int));
    int *C_mode_vals_start = (int*)malloc(store_size * sizeof(int));

    int *C_mode0_end = (int*)malloc(store_size * sizeof(int));
    int *C_mode1_end = (int*)malloc(store_size * sizeof(int));
    int *C_mode_vals_end = (int*)malloc(store_size * sizeof(int));
    
    bool *store_B = (bool *) calloc(store_size * sizeof(bool));
    bool *store_C = (bool *) calloc(store_size * sizeof(bool));

    ofstream gold_file("gold_file.h");

    cg_subtile_B pack(B_mode_0, B_mode_1, B_mode_vals)

    int iB = B1_pos[0];
    int pB1_end = B1_pos[1];
    while(iB < pB1_end) {
            int iB0 = B1_crd[iB];
            int i = iB0;
            if(iB0 == i) {
                int kC = C1_pos[0];            
                int pC1_end = C1_pos[1];      
                int kB = B2_pos[iB];
                int pB2_end = B2_pos[iB + 1];
                while(kB < pB2_end && kC < pC1_end) {
                        int kB0 = B2_crd[kB];
                        int kC0 = C1_crd[kC];
                        int k = min(kB0, kC0);
                        if(kB0 == k && kC0 == k) {    
                            cp_cgra_mem_cpy_sparse(stile_B_ptrs, B_ptrs, kB);
                            id_store_B = i * 8 + k;
                            if(!store_B[id_store_B]){
                                store_B[id_store_B] = 1;
                                cg_tile_mem_op_2(store_extents_B, cg_subtile_B, tile_B, kB, id_store_B);                                         
                            }
                            int jC = C2_pos[kC];
                            int pC2_end = C2_pos[kC + 1];
                            while(jC < pC2_end) {
                                    int jC0 = C2_crd[jC];
                                    int j = jC0;
                                    cp_cgra_mem_cpy_sparse(stile_C_ptrs, C_ptrs, jC);
                                    
                                    if(jC0 == j) {
                                        id_store_C = k * 8 + j;
                                        if(!store_C[id_store_C]){
                                            store_C[id_store_C] = 1;
                                            cg_tile_mem_op_2(store_subtile_C, cg_subtile_C, tile_C, jC, id_store_C);
                                        }
                                        build_extents_2(cg_extents_B, store_extent_B, id_store_B); 
                                        build_extents_2(cg_extents_C, store_extent_C, id_store_C);
                                        cgra_gold(stile_B_ptrs, stile_C_ptrs, gold_file);
                                    }
                                    jC += (int)(jC0 == j);
                            }
                        }
                        kB += (int)(kB0 == k);
                        kC += (int)(kC0 == k);
                }
            }
            iB += (int)(iB0 == i);
    }

    
    ofstream header_file1("glb_data.h");


    mode_data_printer(header_file1, "B", "0", B_mode_0);
    mode_data_printer(header_file1, "B", "1", B_mode_1);
    mode_data_printer(header_file1, "B", "vals", B_mode_vals);

    mode_data_printer(header_file1, "C", "0", C_mode_0);
    mode_data_printer(header_file1, "C", "1", C_mode_1);
    mode_data_printer(header_file1, "C", "vals", C_mode_vals);

    ofstream header_file2("glb_meta_data.h");

    extent_data_printer(header_file2, "B", "0", B_extents_mode_0_run);
    extent_data_printer(header_file2, "B", "1", B_extents_mode_1_run);
    extent_data_printer(header_file2, "B", "vals", B_extents_mode_vals_run);

    extent_data_printer(header_file2, "C", "0", C_extents_mode_0_run);
    extent_data_printer(header_file2, "C", "1", C_extents_mode_1_run);
    extent_data_printer(header_file2, "C", "vals", C_extents_mode_vals_run);

    return 0; 
}

int main(){

    std::vector<int> B1_pos;
    std::vector<int> B1_crd;
    std::vector<int> B2_pos;
    std::vector<int> B2_crd;
    std::vector<int> B3_pos;
    std::vector<int> B3_crd;
    std::vector<int> B4_pos;
    std::vector<int> B4_crd;
    std::vector<int> B_vals;

    std::vector<int> C1_pos;
    std::vector<int> C1_crd;
    std::vector<int> C2_pos;
    std::vector<int> C2_crd;
    std::vector<int> C3_pos;
    std::vector<int> C3_crd;
    std::vector<int> C4_pos;
    std::vector<int> C4_crd;
    std::vector<int> C_vals;
    
    ifstream input_file1("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_pos_0_0.txt");
    load_vector(B1_pos, input_file1);

    ifstream input_file2("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_crd_0_0.txt");
    load_vector(B1_crd, input_file2);

    ifstream input_file3("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_pos_0_1.txt");
    load_vector(B2_pos, input_file3);

    ifstream input_file4("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_crd_0_1.txt");
    load_vector(B2_crd, input_file4);

    ifstream input_file5("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_pos_1_0.txt");
    load_vector(B3_pos, input_file5);

    ifstream input_file6("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_crd_1_0.txt");
    load_vector(B3_crd, input_file6);

    ifstream input_file7("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_pos_1_1.txt");
    load_vector(B4_pos, input_file7);

    ifstream input_file8("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_crd_1_1.txt");
    load_vector(B4_crd, input_file8);

    ifstream input_file9("tensors/lego_test_tiles/tiled_CSF_b/tile_tiled_csf_data.txt");
    load_vector(B_vals, input_file9);

    ifstream input_file10("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_pos_0_0.txt");
    load_vector(C1_pos, input_file10);

    ifstream input_file11("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_crd_0_0.txt");
    load_vector(C1_crd, input_file11);

    ifstream input_file12("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_pos_0_1.txt");
    load_vector(C2_pos, input_file12);

    ifstream input_file13("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_crd_0_1.txt");
    load_vector(C2_crd, input_file13);

    ifstream input_file14("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_pos_1_0.txt");
    load_vector(C3_pos, input_file14);

    ifstream input_file15("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_crd_1_0.txt");
    load_vector(C3_crd, input_file15);

    ifstream input_file16("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_pos_1_1.txt");
    load_vector(C4_pos, input_file16);

    ifstream input_file17("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_crd_1_1.txt");
    load_vector(C4_crd, input_file17);

    ifstream input_file18("tensors/lego_test_tiles/tiled_CSF_c_kj/tile_tiled_csf_data.txt");
    load_vector(C_vals, input_file18);

    int **B_ptrs = (int**)malloc(9 * sizeof(int*));

    B_ptrs[0] = &B1_pos[0];
    B_ptrs[1] = &B1_crd[0];
    B_ptrs[2] = &B2_pos[0];
    B_ptrs[3] = &B2_crd[0];
    B_ptrs[4] = &B3_pos[0];
    B_ptrs[5] = &B3_crd[0];
    B_ptrs[6] = &B4_pos[0];
    B_ptrs[7] = &B4_crd[0];
    B_ptrs[8] = &B_vals[0];

    int **C_ptrs = (int**)malloc(9 * sizeof(int*));

    C_ptrs[0] = &C1_pos[0];
    C_ptrs[1] = &C1_crd[0];
    C_ptrs[2] = &C2_pos[0];
    C_ptrs[3] = &C2_crd[0];
    C_ptrs[4] = &C3_pos[0];
    C_ptrs[5] = &C3_crd[0];
    C_ptrs[6] = &C4_pos[0];
    C_ptrs[7] = &C4_crd[0];
    C_ptrs[8] = &C_vals[0];

    ap_operate(B_ptrs, C_ptrs);

    return 0;
}