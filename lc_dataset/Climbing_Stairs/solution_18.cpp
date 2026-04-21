#include <vector>
#include <cstring>

class Solution {
    int lookup[50];
public:
    int climb(int n) {
        if (n <= 2) return n;
        if (lookup[n] != -1) return lookup[n];
        return lookup[n] = climb(n - 1) + climb(n - 2);
    }
    int climbStairs(int n) {
        std::memset(lookup, -1, sizeof(lookup));
        return climb(n);
    }
};
