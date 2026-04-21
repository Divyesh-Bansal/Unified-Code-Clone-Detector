#include <vector>
#include <cstring>

class Solution {
    int m[50];
public:
    int search(int n) {
        if (n <= 2) return n;
        if (m[n] != -1) return m[n];
        return m[n] = search(n - 1) + search(n - 2);
    }
    int climbStairs(int n) {
        std::memset(m, -1, sizeof(m));
        return search(n);
    }
};
