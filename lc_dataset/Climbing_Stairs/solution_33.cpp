#include <vector>

class Solution {
public:
    std::vector<std::vector<long>> matmul(std::vector<std::vector<long>>& a, std::vector<std::vector<long>>& b) {
        std::vector<std::vector<long>> c(2, std::vector<long>(2, 0));
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                for (int k = 0; k < 2; k++)
                    c[i][j] += a[i][k] * b[k][j];
        return c;
    }
    int climbStairs(int n) {
        if (n <= 2) return n;
        std::vector<std::vector<long>> matrix = {{1, 1}, {1, 0}};
        std::vector<std::vector<long>> result = {{1, 0}, {0, 1}};
        int p = n - 1;
        while (p > 0) {
            if (p % 2 == 1) result = matmul(result, matrix);
            matrix = matmul(matrix, matrix);
            p /= 2;
        }
        return (int)(result[0][0] + result[0][1]);
    }
};
