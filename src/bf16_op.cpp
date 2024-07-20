#include "bf16_op.h"
#include <stdint.h> 
#include <cassert>
#include <iostream>
#include <bitset>

float bf16_add(float input1, float input2) {
    
    std::bitset<32> bf16_mask(0x0000FFFF);
    std::bitset<32> input1_bin(*reinterpret_cast<unsigned int*>(&input1));
    std::bitset<32> input2_bin(*reinterpret_cast<unsigned int*>(&input2));
    // first check the float is in bfloat16 format, i.e. the lower 16 bits are all zeros
    assert((input1_bin & bf16_mask) == std::bitset<32>(0x00000000));
    assert((input2_bin & bf16_mask) == std::bitset<32>(0x00000000));
    
    // add the float numbers
    float result = input1 + input2;

    // rounding to bfloat16 with IEEE 754 round to nearest even
    // convert the results float to binary
    std::bitset<32> result_bin(*reinterpret_cast<unsigned int*>(&result));

    // extract sign, exponent, and mantissa
    unsigned long exp = ((result_bin & std::bitset<32>(0x7F800000)) >> 23).to_ulong();
    unsigned long lfrac = ((result_bin & std::bitset<32>(0x007F0000)) >> 16).to_ulong();
    unsigned long hfrac = (result_bin & std::bitset<32>(0x0000FFFF)).to_ulong();
    std::bitset<1> sign_bit = std::bitset<1>(result_bin[31]);
    std::bitset<8> exp_bit(exp);
    std::bitset<7> lfrac_bit(lfrac);
    std::bitset<16> hfrac_bit(hfrac);

    // rounding logic
    if (hfrac_bit.to_ulong() == 32768) {
        // tie, round to even 
        if (lfrac_bit[0] == 1) {
            if (lfrac_bit == std::bitset<7>(0x7F)) {
                // roll over mantissa and increase exponent
                exp = exp + 1;
            }
            lfrac = lfrac + 1;
        }
        
    } else if (hfrac_bit.to_ulong() > 32768) {
        // round up
        if (lfrac_bit == std::bitset<7>(0x7F)) {
                // roll over mantissa and increase exponent
                exp = exp + 1;
            }
        lfrac = lfrac + 1;
    }
    
    // recombine rounded sign, exponent, and mantissa
    std::bitset<8> exp_rounded_bit(exp);
    std::bitset<7> lfrac_rounded_bit(lfrac);
    std::bitset<32> result_bf16_bit(sign_bit.to_string() + exp_rounded_bit.to_string() + lfrac_rounded_bit.to_string() + "0000000000000000");

    // convert to float
    unsigned int tmp_result_bf16 =static_cast<unsigned int>(result_bf16_bit.to_ulong());
    float result_bf16 = *reinterpret_cast<float *>(&tmp_result_bf16);

    return result_bf16;
}

float bf16_mul(float input1, float input2) {
    
    std::bitset<32> bf16_mask(0x0000FFFF);
    std::bitset<32> input1_bin(*reinterpret_cast<unsigned int*>(&input1));
    std::bitset<32> input2_bin(*reinterpret_cast<unsigned int*>(&input2));
    // first check the float is in bfloat16 format, i.e. the lower 16 bits are all zeros
    assert((input1_bin & bf16_mask) == std::bitset<32>(0x00000000));
    assert((input2_bin & bf16_mask) == std::bitset<32>(0x00000000));

    // multiply the float numbers
    float result = input1 * input2;

    // rounding to bfloat16 with IEEE 754 round to nearest even
    // convert the results float to binary
    std::bitset<32> result_bin(*reinterpret_cast<unsigned int*>(&result));

    // extract sign, exponent, and mantissa
    unsigned long exp = ((result_bin & std::bitset<32>(0x7F800000)) >> 23).to_ulong();
    unsigned long lfrac = ((result_bin & std::bitset<32>(0x007F0000)) >> 16).to_ulong();
    unsigned long hfrac = (result_bin & std::bitset<32>(0x0000FFFF)).to_ulong();
    std::bitset<1> sign_bit = std::bitset<1>(result_bin[31]);
    std::bitset<8> exp_bit(exp);
    std::bitset<7> lfrac_bit(lfrac);
    std::bitset<16> hfrac_bit(hfrac);

    // rounding logic (please refer to float2bfbin in lassen)
    if ((hfrac_bit[15] == 1 && (hfrac_bit[14] == 1 || hfrac_bit[13] == 1))
            || (lfrac_bit[0] == 1 && hfrac_bit[15] == 1)) {
        // round up
        if (lfrac_bit == std::bitset<7>(0x7F)) {
                // roll over mantissa and increase exponent
                exp = exp + 1;
            }
        lfrac = lfrac + 1;
    }

    // recombine rounded sign, exponent, and mantissa
    std::bitset<8> exp_rounded_bit(exp);
    std::bitset<7> lfrac_rounded_bit(lfrac);
    std::bitset<32> result_bf16_bit(sign_bit.to_string() + exp_rounded_bit.to_string() + lfrac_rounded_bit.to_string() + "0000000000000000");

    // convert to float
    unsigned int tmp_result_bf16 =static_cast<unsigned int>(result_bf16_bit.to_ulong());
    float result_bf16 = *reinterpret_cast<float *>(&tmp_result_bf16);

    return result_bf16;
}
