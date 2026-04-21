#include <vector>
#include <cstring>

class Solution {
    int values[50];
public:
    int compute(int n) {
        if (n <= 2) return n;
        if (values[n] != -1) return values[n];
        return values[n] = compute(n - 1) + compute(n - 2);
    }
    int climbStairs(int n) {
        std::memset(values, -1, sizeof(values));
        return compute(n);
    }
};
