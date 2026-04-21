#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> table(n + 1);
        table[1] = 1;
        table[2] = 2;
        for (int j = 3; j <= n; j++) {
            table[j] = table[j - 1] + table[j - 2];
        }
        return table[n];
    }
};
