#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> result(n + 1);
        result[1] = 1;
        result[2] = 2;
        for (int it = 3; it <= n; it++) {
            result[it] = result[it - 1] + result[it - 2];
        }
        return result[n];
    }
};
