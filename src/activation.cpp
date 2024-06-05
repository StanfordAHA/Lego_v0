#include "activation.h"

int apply_relu(double *input, int size) {
    for (int i = 0; i < size; i++) {
        if (input[i] < 0) {
            input[i] = 0;
        }
    }

    return 0;
}