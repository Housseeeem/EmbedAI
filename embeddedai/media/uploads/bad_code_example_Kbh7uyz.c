// bad_code_example.c
#include <stdio.h>

void printNumbers() {
    int i;
    for (i = 0; i < 10; i++) {
        printf("%d\n", i);
    }
}

int main() {
    int *ptr = NULL;
    printf("%d", *ptr); // BUG: Dereferencing a NULL pointer

    printNumbers();

    return 0;
}
