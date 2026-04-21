#include <vector>
#include <cstring>

class Solution {
    int cache[50];
public:
    int solve(int n) {
        if (n <= 2) return n;
        if (cache[n] != -1) return cache[n];
        return cache[n] = solve(n - 1) + solve(n - 2);
    }
    int climbStairs(int n) {
        std::memset(cache, -1, sizeof(cache));
        return solve(n);
    }
};
