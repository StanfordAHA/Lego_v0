#include "bf16_op.h"
#include <cmath>

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

int bf16_f2int(float input) {

    // check if input is in bfloat16 format
    std::bitset<32> input_bin(*reinterpret_cast<unsigned int*>(&input));
    assert((input_bin & std::bitset<32>(0x0000FFFF)) == std::bitset<32>(0x00000000));

    // extract sign, exponent, and fraction
    unsigned long sign = ((input_bin & std::bitset<32>(0x80000000)) >> 31).to_ulong();
    unsigned long exp = ((input_bin & std::bitset<32>(0x7F800000)) >> 23).to_ulong();
    unsigned long frac = (input_bin & std::bitset<32>(0x007F0000) >> 16).to_ulong();
    std::bitset<23> frac_bin(frac);
    
    // add back the implicit 1
    frac_bin = frac_bin | std::bitset<23>(0x0080);
    
    // unbias of the exponent
    long exp_unbias = exp - 127;

    // shift the fraction according to the exponent
    if (exp_unbias >= 0) {
        frac_bin = frac_bin << exp_unbias;
    } else {
        frac_bin = frac_bin >> -exp_unbias;
    }

    // retreive the integer part by shifting out the fraction
    frac_bin = frac_bin >> 7;
    std::bitset<16> res(frac_bin.to_string());

    // sign conversion acoording to the sign bit
    if (sign == 1) {
        return -1 * frac_bin.to_ulong();
    } else {
        return frac_bin.to_ulong();
    }
}

int bf16_getfr(float input) {

    // check if input is in bfloat16 format
    std::bitset<32> input_bin(*reinterpret_cast<unsigned int*>(&input));
    assert((input_bin & std::bitset<32>(0x0000FFFF)) == std::bitset<32>(0x00000000));

    // extract sign, exponent, and fraction
    unsigned long sign = ((input_bin & std::bitset<32>(0x80000000)) >> 31).to_ulong();
    unsigned long exp = ((input_bin & std::bitset<32>(0x7F800000)) >> 23).to_ulong();
    unsigned long frac = (input_bin & std::bitset<32>(0x007F0000) >> 16).to_ulong();
    
    // extract the fraction and add the implicit 1
    std::bitset<16> frac_bin(frac);
    
    // add back the implicit 1
    frac_bin = frac_bin | std::bitset<16>(0x0080);

    // unbias of the exponent
    long exp_unbias = exp - 127;

    // shift the fraction according to the exponent
    if (exp_unbias >= 0) {
        frac_bin = frac_bin << exp_unbias;
    } else {
        frac_bin = frac_bin >> -exp_unbias;
    }

    // mask out the unwanted bits
    frac_bin = frac_bin & std::bitset<16>(0x007F);

    // sign conversion acoording to the sign bit
    if (sign == 1) {
        return -1 * frac_bin.to_ulong();
    } else {
        return frac_bin.to_ulong();
    }
}

float bf16_faddiexp(float input1, int input2) { 

    // check if input is in bfloat16 format
    std::bitset<32> input_bin(*reinterpret_cast<unsigned int*>(&input1));
    assert((input_bin & std::bitset<32>(0x0000FFFF)) == std::bitset<32>(0x00000000));

    // extract sign, exponent, and mantissa
    std::bitset<1> sign_bit = std::bitset<1>(input_bin[31]);
    unsigned long exp = ((input_bin & std::bitset<32>(0x7F800000)) >> 23).to_ulong();
    unsigned long lfrac = ((input_bin & std::bitset<32>(0x007F0000)) >> 16).to_ulong();

    // add the exponent
    exp = exp + input2;

    // recombine sign, exponent, and mantissa
    std::bitset<8> exp_bit(exp);
    std::bitset<7> lfrac_bit(lfrac);
    std::bitset<32> result_bin(sign_bit.to_string() + exp_bit.to_string() + lfrac_bit.to_string() + "0000000000000000");

    // convert to float
    unsigned int tmp_result_bf16 =static_cast<unsigned int>(result_bin.to_ulong());
    float result_bf16 = *reinterpret_cast<float *>(&tmp_result_bf16);

    return result_bf16;
}

std::string float2bfbin(float input, bool return_hex) {

    // convert the input float to binary
    std::bitset<32> input_bin(*reinterpret_cast<unsigned int*>(&input));
    std::bitset<32> conversion_mask(0xFFFF0000);

    // convert to bf16 by masking the lower 16 bits and shifting right 
    std::bitset<32> bfbin = (input_bin & conversion_mask) >> 16;
    
    if (return_hex) {
        std::stringstream ss;
        ss << std::hex << bfbin.to_ulong();
        return ss.str();
    } else {
        return std::to_string(bfbin.to_ulong());
    }
}

float bfbin2float(std::string input) { 

    // convert the input binary string to bitset
    std::bitset<16> bfbin(input);
    std::bitset<32> fbin(bfbin.to_string() + "0000000000000000");

    //convert to float
    unsigned int tmp_result =static_cast<unsigned int>(fbin.to_ulong());
    float result = *reinterpret_cast<float *>(&tmp_result);

    return result;
}