#ifndef ACTIVATION_H
#define ACTIVATION_H
#include <vector>

int apply_output_relu(float *input, int size);
int apply_input_relu(std::vector<float> &input);
void apply_exp(float *input, int size);
void apply_leakyrelu(float *input, int size);
void apply_elu(float *input, int size);

#endif