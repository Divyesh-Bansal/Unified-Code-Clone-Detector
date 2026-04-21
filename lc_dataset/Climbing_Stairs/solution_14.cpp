#include <vector>
#include <cstring>

class Solution {
    int store[50];
public:
    int f(int n) {
        if (n <= 2) return n;
        if (store[n] != -1) return store[n];
        return store[n] = f(n - 1) + f(n - 2);
    }
    int climbStairs(int n) {
        std::memset(store, -1, sizeof(store));
        return f(n);
    }
};
