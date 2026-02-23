// simple_duplicate.cpp - Contains near-duplicate functions
#include <iostream>
using namespace std;

void printArray(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;
}

void displayArray(int data[], int size) {
    for (int j = 0; j < size; j++) {
        cout << data[j] << " ";
    }
    cout << endl;
}

int sumArray(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}

int addElements(int data[], int count) {
    int sum = 0;
    for (int j = 0; j < count; j++) {
        sum += data[j];
    }
    return sum;
}
