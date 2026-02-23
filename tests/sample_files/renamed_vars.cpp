// renamed_vars.cpp - Functions with renamed variables but same logic
#include <iostream>
using namespace std;

int findMax(int arr[], int n) {
    int maxVal = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > maxVal) {
            maxVal = arr[i];
        }
    }
    return maxVal;
}

int getLargest(int data[], int count) {
    int biggest = data[0];
    for (int j = 1; j < count; j++) {
        if (data[j] > biggest) {
            biggest = data[j];
        }
    }
    return biggest;
}
