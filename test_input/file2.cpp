// file2.cpp - Second test file with some duplicates of file1
#include <iostream>
using namespace std;

int addition(int p, int q) {
    return p + q;
}

void displayNumbers(int begin, int finish) {
    for (int j = begin; j <= finish; j++) {
        cout << j << " ";
    }
    cout << endl;
}

int multiply(int a, int b) {
    int result = 0;
    for (int i = 0; i < b; i++) {
        result += a;
    }
    return result;
}
