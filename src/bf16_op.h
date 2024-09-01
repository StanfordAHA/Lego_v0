#ifndef BF16_OP_H
#define BF16_OP_H
#include <string>

float bf16_add(float input1, float input2);
float bf16_mul(float input1, float input2);
float float2bfbin(float input, bool return_hex);

#endif