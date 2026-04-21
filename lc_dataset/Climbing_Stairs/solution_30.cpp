#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> values(n + 1);
        values[1] = 1;
        values[2] = 2;
        for (int iter = 3; iter <= n; iter++) {
            values[iter] = values[iter - 1] + values[iter - 2];
        }
        return values[n];
    }
};
