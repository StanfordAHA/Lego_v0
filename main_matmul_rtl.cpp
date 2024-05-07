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

int subtile_gold(subtile2 subtile_B, subtile2 subtile_C, int curr_subtile_num, ofstream &output_gold_file) {

    int *B1_pos = subtile_B.pos1.data();
    int *B1_crd = subtile_B.crd1.data();
    int *B2_pos = subtile_B.pos2.data();
    int *B2_crd = subtile_B.crd2.data();
    double *B_vals = subtile_B.vals.data();


    int *C1_pos = subtile_C.pos1.data();
    int *C1_crd = subtile_C.crd1.data();
    int *C2_pos = subtile_C.pos2.data();
    int *C2_crd = subtile_C.crd2.data();
    double *C_vals = subtile_C.vals.data();

    int output_subtile_size = 900;

    double *A_vals = (double*)malloc(sizeof(double) * output_subtile_size);

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

    rtl_output_subtile_printer(A_vals, output_subtile_size, curr_subtile_num, output_gold_file);

    return 0;

}

int tile_operate(tile2 tile_B, tile2 tile_C, std::string curr_tile) {

    int *B1_pos = tile_B.pos1.data();
    int *B1_crd = tile_B.crd1.data();
    int *B2_pos = tile_B.pos2.data();
    int *B2_crd = tile_B.crd2.data();
    int *B3_pos = tile_B.pos3.data();
    int *B3_crd = tile_B.crd3.data();
    int *B4_pos = tile_B.pos4.data();
    int *B4_crd = tile_B.crd4.data();
    double *B_vals = tile_B.vals.data();

    subtile2 subtile_B;


    int *C1_pos = tile_C.pos1.data();
    int *C1_crd = tile_C.crd1.data();
    int *C2_pos = tile_C.pos2.data();
    int *C2_crd = tile_C.crd2.data();
    int *C3_pos = tile_C.pos3.data();
    int *C3_crd = tile_C.crd3.data();
    int *C4_pos = tile_C.pos4.data();
    int *C4_crd = tile_C.crd4.data();
    double *C_vals = tile_C.vals.data();

    subtile2 subtile_C;


    int curr_subtile_num = 0;
    std::string out_dir = "lego_scratch/data_files/" + curr_tile;
    const char *data_path = out_dir.c_str();

    std::string output_gold_path = out_dir + "/output_gold.h";
    std::ofstream output_gold_file;
    std::string subtile_path;


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
                    subtile_B = tile_mem_op_2(tile_B, kB);
                    int jC = C2_pos[kC];
                    int pC2_end = C2_pos[kC + 1];
                    while(jC < pC2_end){
                        int jC0 = C2_crd[jC];
                        int j = jC0;
                        if(jC0 == j){
                            subtile_C = tile_mem_op_2(tile_C, jC);
                            mkdir(data_path, 0777);
                            subtile_path = out_dir + "/subtile_pair_" + std::to_string(curr_subtile_num);
                            const char *subtile_path_str = subtile_path.c_str();
                            mkdir(subtile_path_str, 0777);
                            output_gold_path = subtile_path + "/output_gold.h";
                            output_gold_file.open(output_gold_path, std::ios_base::app);
                            subtile_gold(subtile_B, subtile_C, curr_subtile_num, output_gold_file);
                            rtl_subtile2_print(subtile_B, subtile_path, "B", 30, 30);
                            rtl_subtile2_print(subtile_C, subtile_path, "C", 30, 30);
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
    std::vector<double> B_vals;

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
    build_vec_val(B_vals, "lego_scratch/tensor_B/tcsf_vals.txt");

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
    tensor_B[12] = (int *)B_vals.data();

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
    std::vector<double> C_vals;

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
    build_vec_val(C_vals, "lego_scratch/tensor_C/tcsf_vals.txt");

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
    tensor_C[12] = (int *)C_vals.data();

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
