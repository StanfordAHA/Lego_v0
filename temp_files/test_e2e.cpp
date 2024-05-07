#include <stdlib.h>
#include <stdio.h>
#include <cstring>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <boost/format.hpp>
#include <sys/types.h>
#include <sys/stat.h>
using namespace std;

#include "src/data_parser.h"
#include "src/mem_op.h"


int subtile_gold(subtile2 B_ptrs, subtile2 C_ptrs, int curr_subtile_num, ofstream &output_gold_file) {

    int *B1_pos = B_ptrs.pos1.data();
    int *B1_crd = B_ptrs.crd1.data();
    int *B2_pos = B_ptrs.pos2.data();
    int *B2_crd = B_ptrs.crd2.data();
    int *B_vals = B_ptrs.vals.data();

    int *C1_pos = C_ptrs.pos1.data();
    int *C1_crd = C_ptrs.crd1.data();
    int *C2_pos = C_ptrs.pos2.data();
    int *C2_crd = C_ptrs.crd2.data();
    int *C_vals = C_ptrs.vals.data();

    int output_subtile_size = 900; 
    int *A_vals = (int*)malloc(sizeof(int) * output_subtile_size);
  
    for (int pA = 0; pA < output_subtile_size; pA++) {
        A_vals[pA] = 0;
    }

    int pA; 

    int iB = B1_pos[0];
    int pB1_end = B1_pos[1];
    while(iB < pB1_end){
        int iB0 = B1_crd[iB];
        int i = iB0;
        if(iB0 == i){
            int jC = C1_pos[0];
            int pC1_end = C1_pos[1];
            while(jC < pC1_end){
                int jC0 = C1_crd[jC];
                int j = jC0;
                if(jC0 == j){
                    int kB = B2_pos[iB];
                    int pB2_end = B2_pos[iB + 1];
                    int kC = C2_pos[jC];
                    int pC2_end = C2_pos[jC + 1];
                    while(kC < pC2_end && kB < pB2_end){
                        int kC0 = C2_crd[kC];
                        int kB0 = B2_crd[kB];
                        int k = min(kC0, kB0);
                        if(kC0 == k && kB0 == k){
                            pA = i * 30 + j;
                            A_vals[pA] += B_vals[kB] * C_vals[kC]; 
                        }
                        kC += (int)(kC0 == k);
                        kB += (int)(kB0 == k);
                    }
                }
                jC += (int)(jC0 == j);
            }
        }
        iB += (int)(iB0 == i);
    }

    output_subtile_printer(A_vals, output_subtile_size, curr_subtile_num, output_gold_file);

    return 0;
}


/**
int subtile_gold(subtile2 subtile_B, subtile2 subtile_C, int curr_subtile_num, ofstream &output_gold_file) {

    int *B1_pos = subtile_B.pos1.data();
    int *B1_crd = subtile_B.pos1.data();
    int *B2_pos = subtile_B.pos2.data();
    int *B2_crd = subtile_B.pos2.data();
    int *B_vals = subtile_B.vals.data();


    int *C1_pos = subtile_C.pos1.data();
    int *C1_crd = subtile_C.pos1.data();
    int *C2_pos = subtile_C.pos2.data();
    int *C2_crd = subtile_C.pos2.data();
    int *C_vals = subtile_C.vals.data();

    int output_subtile_size = 900;

    int *A_vals = (int*)malloc(sizeof(int) * output_subtile_size);

    for (int pA = 0; pA < output_subtile_size; pA++) {
        A_vals[pA] = 0;
    }

    int pA;
    int iB = B1_pos[0];
    int pB1_end = B1_pos[1];
    while(iB < pB1_end){
        int iB0 = B1_crd[iB];
        int i = iB0;
        if(iB0 == i){
            int jC = C1_pos[0];
            int pC1_end = C1_pos[1];
            while(jC < pC1_end){
                int jC0 = C1_crd[jC];
                int j = jC0;
                if(jC0 == j){
                    int kB = B2_pos[iB];
                    int pB2_end = B2_pos[iB + 1];
                    int kC = C2_pos[jC];
                    int pC2_end = C2_pos[jC + 1];
                    while(kC < pC2_end && kB < pB2_end){
                        int kC0 = C2_crd[kC];
                        int kB0 = B2_crd[kB];
                        int k = min(kC0, kB0);
                        if(kC0 == k && kB0 == k){
                            pA = j + i * 30;
                            A_vals[pA] += (B_vals[kB] * C_vals[kC]);

                        }
                        kC += (int)(kC0 == k);
                        kB += (int)(kB0 == k);
                    }
                }
                jC += (int)(jC0 == j);
            }
        }
        iB += (int)(iB0 == i);
    }

    output_subtile_printer(A_vals, output_subtile_size, curr_subtile_num, output_gold_file);

    return 0;
}
**/

int tile_operate(tile2 tile_B, tile2 tile_C, string curr_tile) {
    
    int *B1_pos = tile_B.pos1.data();
    int *B1_crd = tile_B.crd1.data();
    int *B2_pos = tile_B.pos2.data();
    int *B2_crd = tile_B.crd2.data();
    int *B3_pos = tile_B.pos3.data();
    int *B3_crd = tile_B.crd3.data();
    int *B4_pos = tile_B.pos4.data();
    int *B4_crd = tile_B.crd4.data();
    int *B_vals = tile_B.vals.data();

    subtile2 subtile_B;

    int store_size_B = 64;
    int id_store_B;

    bool *store_B = (bool *) calloc((store_size_B + 1), sizeof(bool));
    int *B_mode0_start = (int*)malloc((store_size_B + 1) * sizeof(int));
    int *B_mode0_end = (int*)malloc((store_size_B + 1) * sizeof(int));
    int *B_mode1_start = (int*)malloc((store_size_B + 1) * sizeof(int));
    int *B_mode1_end = (int*)malloc((store_size_B + 1) * sizeof(int));
    int *B_mode_vals_start = (int*)malloc((store_size_B + 1) * sizeof(int));
    int *B_mode_vals_end = (int*)malloc((store_size_B + 1) * sizeof(int));

    int **store_subtile_B;
    store_subtile_B = (int**)malloc(sizeof(int*) * (6));
    store_subtile_B[0] = B_mode0_start;
    store_subtile_B[1] = B_mode0_end;
    store_subtile_B[2] = B_mode1_start;
    store_subtile_B[3] = B_mode1_end;
    store_subtile_B[4] = B_mode_vals_start;
    store_subtile_B[5] = B_mode_vals_end;

    cg_subtile2 cg_subtile_B;
    cg_extents2 cg_extents_B;

    int *C1_pos = tile_C.pos1.data();
    int *C1_crd = tile_C.crd1.data();
    int *C2_pos = tile_C.pos2.data();
    int *C2_crd = tile_C.crd2.data();
    int *C3_pos = tile_C.pos3.data();
    int *C3_crd = tile_C.crd3.data();
    int *C4_pos = tile_C.pos4.data();
    int *C4_crd = tile_C.crd4.data();
    int *C_vals = tile_C.vals.data();

    subtile2 subtile_C;

    int store_size_C = 64;
    int id_store_C;

    bool *store_C = (bool *) calloc((store_size_C + 1), sizeof(bool));
    int *C_mode0_start = (int*)malloc((store_size_C + 1) * sizeof(int));
    int *C_mode0_end = (int*)malloc((store_size_C + 1) * sizeof(int));
    int *C_mode1_start = (int*)malloc((store_size_C + 1) * sizeof(int));
    int *C_mode1_end = (int*)malloc((store_size_C + 1) * sizeof(int));
    int *C_mode_vals_start = (int*)malloc((store_size_C + 1) * sizeof(int));
    int *C_mode_vals_end = (int*)malloc((store_size_C + 1) * sizeof(int));

    int **store_subtile_C;
    store_subtile_C = (int**)malloc(sizeof(int*) * (6));
    store_subtile_C[0] = C_mode0_start;
    store_subtile_C[1] = C_mode0_end;
    store_subtile_C[2] = C_mode1_start;
    store_subtile_C[3] = C_mode1_end;
    store_subtile_C[4] = C_mode_vals_start;
    store_subtile_C[5] = C_mode_vals_end;

    cg_subtile2 cg_subtile_C;
    cg_extents2 cg_extents_C;

    int curr_subtile_num = 0;

    string out_dir = "lego_scratch/data_files/" + curr_tile;
    const char *data_path = out_dir.c_str();

    string input_data_path = out_dir + "/input_data.h";
    ofstream input_data_file;

    string input_meta_data_path = out_dir + "/input_meta_data.h";
    ofstream input_meta_data_file;
    
    string output_gold_path = out_dir + "/output_gold.h";
    ofstream output_gold_file;
    
    int iB = B1_pos[0];
    int pB1_end = B1_pos[1];

    while(iB < pB1_end){
        int iB0 = B1_crd[iB];
        int i = iB0;
        if(iB0 == i){
            int kB = B2_pos[iB];
            int pB2_end = B2_pos[iB + 1];
            int kC = C1_pos[0];
            int pC1_end = C1_pos[1];
            while(kC < pC1_end && kB < pB2_end){
                int kC0 = C1_crd[kC];
                int kB0 = B2_crd[kB];
                int k = min(kC0, kB0);
                if(kC0 == k && kB0 == k){
                    id_store_B = i * 8 + k;
                    if(!store_B[id_store_B]){
                        store_B[id_store_B] = 1;
                        cg_subtile_B = cg_tile_mem_op_2(cg_subtile_B, store_subtile_B, tile_B, kB, id_store_B);
                    }
                    subtile_B = tile_mem_op_2(tile_B, kB);
                    int jC = C2_pos[kC];
                    int pC2_end = C2_pos[kC + 1];
                    while(jC < pC2_end){
                        int jC0 = C2_crd[jC];
                        int j = jC0;
                        if(jC0 == j){
                            id_store_C = k * 8 + j;
                            if(!store_C[id_store_C]){
                                store_C[id_store_C] = 1;
                                cg_subtile_C = cg_tile_mem_op_2(cg_subtile_C, store_subtile_C, tile_C, jC, id_store_C);
                            }
                            subtile_C = tile_mem_op_2(tile_C, jC);
                            cg_extents_C = build_extents_2(cg_extents_C, store_subtile_C, id_store_C);
                            cg_extents_B = build_extents_2(cg_extents_B, store_subtile_B, id_store_B);

                            mkdir(data_path, 0777);
                            output_gold_file.open(output_gold_path, std::ios_base::app);
                            subtile_gold(subtile_B, subtile_C, curr_subtile_num, output_gold_file);
                            curr_subtile_num++;
                            output_gold_file.close();
                        }
                        jC += (int)(jC0 == j);
                    }
                }
                kC += (int)(kC0 == k);
                kB += (int)(kB0 == k);
            }
        }
        iB += (int)(iB0 == i);
    }

    if(cg_extents_B.extents_mode_0.size() > 0 && cg_extents_C.extents_mode_0.size() > 0){

        input_data_file.open(input_data_path);
        input_meta_data_file.open(input_meta_data_path);

        mode_data_printer(input_data_file, "B", "0", cg_subtile_B.mode_0);
        mode_data_printer(input_data_file, "B", "1", cg_subtile_B.mode_1);
        mode_data_printer(input_data_file, "B", "vals", cg_subtile_B.mode_vals);

        mode_data_printer(input_data_file, "C", "1", cg_subtile_C.mode_0);
        mode_data_printer(input_data_file, "C", "0", cg_subtile_C.mode_1);
        mode_data_printer(input_data_file, "C", "vals", cg_subtile_C.mode_vals);

        extent_data_printer(input_meta_data_file, "B", "0", cg_extents_B.extents_mode_0);
        extent_data_printer(input_meta_data_file, "B", "1", cg_extents_B.extents_mode_1);
        extent_data_printer(input_meta_data_file, "B", "vals", cg_extents_B.extents_mode_vals);

        extent_data_printer(input_meta_data_file, "C", "1", cg_extents_C.extents_mode_0);
        extent_data_printer(input_meta_data_file, "C", "0", cg_extents_C.extents_mode_1);
        extent_data_printer(input_meta_data_file, "C", "vals", cg_extents_C.extents_mode_vals);

        input_data_file.close();
        input_meta_data_file.close();
    }

    return 0;
}

int main() {

    std::vector<int> B1_pos;
    std::vector<int> B1_crd;
    std::vector<int> B2_pos;
    std::vector<int> B2_crd;
    std::vector<int> B3_pos;
    std::vector<int> B3_crd;
    std::vector<int> B4_pos;
    std::vector<int> B4_crd;
    std::vector<int> B5_pos;
    std::vector<int> B5_crd;
    std::vector<int> B6_pos;
    std::vector<int> B6_crd;
    std::vector<int> B_vals;

    build_vec(B1_pos, "lego_scratch/tensor_B/tcsf_pos1.txt");
    build_vec(B1_crd, "lego_scratch/tensor_B/tcsf_crd1.txt");
    build_vec(B2_pos, "lego_scratch/tensor_B/tcsf_pos2.txt");
    build_vec(B2_crd, "lego_scratch/tensor_B/tcsf_crd2.txt");
    build_vec(B3_pos, "lego_scratch/tensor_B/tcsf_pos3.txt");
    build_vec(B3_crd, "lego_scratch/tensor_B/tcsf_crd3.txt");
    build_vec(B4_pos, "lego_scratch/tensor_B/tcsf_pos4.txt");
    build_vec(B4_crd, "lego_scratch/tensor_B/tcsf_crd4.txt");
    build_vec(B5_pos, "lego_scratch/tensor_B/tcsf_pos5.txt");
    build_vec(B5_crd, "lego_scratch/tensor_B/tcsf_crd5.txt");
    build_vec(B6_pos, "lego_scratch/tensor_B/tcsf_pos6.txt");
    build_vec(B6_crd, "lego_scratch/tensor_B/tcsf_crd6.txt");
    build_vec(B_vals, "lego_scratch/tensor_B/tcsf_vals.txt");

    int **tensor_B;
    tensor_B = (int**)malloc(sizeof(int*) * (13));

    tensor_B[0] = B1_pos.data();
    tensor_B[1] = B1_crd.data();
    tensor_B[2] = B2_pos.data();
    tensor_B[3] = B2_crd.data();
    tensor_B[4] = B3_pos.data();
    tensor_B[5] = B3_crd.data();
    tensor_B[6] = B4_pos.data();
    tensor_B[7] = B4_crd.data();
    tensor_B[8] = B5_pos.data();
    tensor_B[9] = B5_crd.data();
    tensor_B[10] = B6_pos.data();
    tensor_B[11] = B6_crd.data();
    tensor_B[12] = B_vals.data();

    tile2 tile_B;

    std::vector<int> C1_pos;
    std::vector<int> C1_crd;
    std::vector<int> C2_pos;
    std::vector<int> C2_crd;
    std::vector<int> C3_pos;
    std::vector<int> C3_crd;
    std::vector<int> C4_pos;
    std::vector<int> C4_crd;
    std::vector<int> C5_pos;
    std::vector<int> C5_crd;
    std::vector<int> C6_pos;
    std::vector<int> C6_crd;
    std::vector<int> C_vals;

    build_vec(C1_pos, "lego_scratch/tensor_C/tcsf_pos1.txt");
    build_vec(C1_crd, "lego_scratch/tensor_C/tcsf_crd1.txt");
    build_vec(C2_pos, "lego_scratch/tensor_C/tcsf_pos2.txt");
    build_vec(C2_crd, "lego_scratch/tensor_C/tcsf_crd2.txt");
    build_vec(C3_pos, "lego_scratch/tensor_C/tcsf_pos3.txt");
    build_vec(C3_crd, "lego_scratch/tensor_C/tcsf_crd3.txt");
    build_vec(C4_pos, "lego_scratch/tensor_C/tcsf_pos4.txt");
    build_vec(C4_crd, "lego_scratch/tensor_C/tcsf_crd4.txt");
    build_vec(C5_pos, "lego_scratch/tensor_C/tcsf_pos5.txt");
    build_vec(C5_crd, "lego_scratch/tensor_C/tcsf_crd5.txt");
    build_vec(C6_pos, "lego_scratch/tensor_C/tcsf_pos6.txt");
    build_vec(C6_crd, "lego_scratch/tensor_C/tcsf_crd6.txt");
    build_vec(C_vals, "lego_scratch/tensor_C/tcsf_vals.txt");

    int **tensor_C;
    tensor_C = (int**)malloc(sizeof(int*) * (13));

    tensor_C[0] = C1_pos.data();
    tensor_C[1] = C1_crd.data();
    tensor_C[2] = C2_pos.data();
    tensor_C[3] = C2_crd.data();
    tensor_C[4] = C3_pos.data();
    tensor_C[5] = C3_crd.data();
    tensor_C[6] = C4_pos.data();
    tensor_C[7] = C4_crd.data();
    tensor_C[8] = C5_pos.data();
    tensor_C[9] = C5_crd.data();
    tensor_C[10] = C6_pos.data();
    tensor_C[11] = C6_crd.data();
    tensor_C[12] = C_vals.data();

    tile2 tile_C;

    std::string tile_name;

    int iB = B1_pos[0];
    int pB1_end = B1_pos[1];
    while(iB < pB1_end){
        int iB0 = B1_crd[iB];
        int i = iB0;
        if(iB0 == i){
            int kB = B2_pos[iB];
            int pB2_end = B2_pos[iB + 1];
            int kC = C1_pos[0];
            int pC1_end = C1_pos[1];
            while(kC < pC1_end && kB < pB2_end){
                int kC0 = C1_crd[kC];
                int kB0 = B2_crd[kB];
                int k = min(kC0, kB0);
                if(kC0 == k && kB0 == k){
                    tile_B = tensor_mem_op_2(tensor_B, kB);
                    int jC = C2_pos[kC];
                    int pC2_end = C2_pos[kC + 1];
                    while(jC < pC2_end){
                        int jC0 = C2_crd[jC];
                        int j = jC0;
                        if(jC0 == j){
                            tile_C = tensor_mem_op_2(tensor_C, jC);
                            tile_name = "tile_";
                            tile_name += "iB_" + std::to_string(i) + "_";
                            tile_name += "kB_" + std::to_string(k) + "_"; 
                            tile_name += "kC_" + std::to_string(k) + "_";
                            tile_name += "jC_" + std::to_string(j) + "_";
                            tile_operate(tile_B, tile_C, tile_name);
                        }
                        jC += (int)(jC0 == j);
                    }
                }
                kC += (int)(kC0 == k);
                kB += (int)(kB0 == k);
            }
        }
        iB += (int)(iB0 == i);
    }

    return 0;
}
