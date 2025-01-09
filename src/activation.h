#ifndef ACTIVATION_H
#define ACTIVATION_H

#include "bf16_op.h"
#include "gen_lut.h"
#include <bitset>
#include <cmath>
#include <vector>

void apply_relu(float *input, int size);
void apply_exp(float *input, int size);
void apply_leakyrelu(float *input, int size);
void apply_elu(float *input, int size);

#endif