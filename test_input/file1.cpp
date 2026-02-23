// file1.cpp - First test file with multiple functions
#include <iostream>
using namespace std;

int add(int a, int b) {
    return a + b;
}

int sum(int x, int y) {
    return x + y;
}

void printNumbers(int start, int end) {
    for (int i = start; i <= end; i++) {
        cout << i << " ";
    }
    cout << endl;
}

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}
