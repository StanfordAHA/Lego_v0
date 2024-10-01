#include "activation.h"
#include "bf16_op.h"
#include <bitset>

void apply_relu(float *input, int size) {
    for (int i = 0; i < size; i++) {
        if (input[i] < 0) {
            input[i] = 0;
        }
    }
}

void apply_exp(float *input, int size) {
    // this is implemented according to the composition of complex ops in our cgra
    // please refer to the amber paper https://ieeexplore.ieee.org/document/10258121 
    // for more details

    // generate the rom content for the exp function
    float exp_rom[256] = {0};
    int index = 0;
    for (int i = -128; i < 0; i ++) {
        exp_rom[index] = bfbin2float(float2bfbin((2, float(i) / 128.0), false, true));
        index ++;
    }
    for (int i = 0; i < 128; i ++) {
        exp_rom[index] = bfbin2float(float2bfbin((2, float(i) / 128.0), false, true));
        index ++;
    }

    for (int i = 0; i < size; i++) {
        float _1_div_ln2_mul = 0;
        int frac = 0;
        int integer = 0;
        _1_div_ln2_mul = bf16_mul(input[i], bfbin2float(float2bfbin(1.442695, false, true)));
        frac= bf16_getfr(_1_div_ln2_mul);
        integer = bf16_f2int(_1_div_ln2_mul);
        float rom_out = exp_rom[frac + 128];
        input[i] = bf16_faddiexp(rom_out, integer);
    }
}

void apply_leakyrelu(float *input, int size) {

    // TODO: parameterize the leaky relu slope
    for (int i = 0; i < size; i++) {
        if (input[i] < 0) {
            input[i] = bf16_mul(input[i], bfbin2float(float2bfbin(0.2, false, true)));
        }
    }
}
