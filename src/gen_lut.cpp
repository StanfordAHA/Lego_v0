#include "gen_lut.h"

std::vector<float> gen_exp_lut() {
    
    std::vector<float> exp_rom(256, 0);
    int index = 0;
    for (int i = -128; i < 0; i ++) {
        exp_rom[index] = bfbin2float(float2bfbin(pow(2, float(i) / 128.0), false, true));
        index ++;
    }
    for (int i = 0; i < 128; i ++) {
        exp_rom[index] = bfbin2float(float2bfbin(pow(2, float(i) / 128.0), false, true));
        index ++;
    }

    return exp_rom;
}

std::vector<float> gen_div_lut() {

    std::vector<float> div_rom(128, 0);
    for (int i = 0; i < 128; i ++) {
        div_rom[i] = bfbin2float(float2bfbin(1.0 / (1.0 + float(i) /128.0), false, true));
    }
    return div_rom;
}

