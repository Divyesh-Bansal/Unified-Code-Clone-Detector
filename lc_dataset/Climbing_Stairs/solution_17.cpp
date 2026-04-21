#include <vector>
#include <cstring>

class Solution {
    int data[50];
public:
    int rec(int n) {
        if (n <= 2) return n;
        if (data[n] != -1) return data[n];
        return data[n] = rec(n - 1) + rec(n - 2);
    }
    int climbStairs(int n) {
        std::memset(data, -1, sizeof(data));
        return rec(n);
    }
};
