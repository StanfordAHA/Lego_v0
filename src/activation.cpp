#include "activation.h"

int apply_output_relu(float *input, int size) {
    for (int i = 0; i < size; i++) {
        if (input[i] < 0) {
            input[i] = 0;
        }
    }

    return 0;
}

int apply_input_relu(std::vector<float> &input) {
    for (int i = 0; i < input.size(); i++) {
        if (input[i] < 0) {
            input[i] = 0;
        }
    }

    return 0;
}