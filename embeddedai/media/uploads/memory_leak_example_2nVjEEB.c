#include <stdio.h>
#include <stdlib.h>

int main() {
    int *array = (int *)malloc(5 * sizeof(int));

    if (array == NULL) {
        return 1; // Allocation failed
    }

    array[0] = 10;
    array[1] = 20;

    printf("First value: %d\n", array[0]);

    // Memory Leak: forgot to free(array)
    return 0;
}
