#include <vector>

class Solution {
public:
    std::vector<std::vector<long>> multiply(std::vector<std::vector<long>>& a, std::vector<std::vector<long>>& b) {
        std::vector<std::vector<long>> c(2, std::vector<long>(2, 0));
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                for (int k = 0; k < 2; k++)
                    c[i][j] += a[i][k] * b[k][j];
        return c;
    }
    int climbStairs(int n) {
        if (n <= 2) return n;
        std::vector<std::vector<long>> T = {{1, 1}, {1, 0}};
        std::vector<std::vector<long>> res = {{1, 0}, {0, 1}};
        int p = n - 1;
        while (p > 0) {
            if (p % 2 == 1) res = multiply(res, T);
            T = multiply(T, T);
            p /= 2;
        }
        return (int)(res[0][0] + res[0][1]);
    }
};
