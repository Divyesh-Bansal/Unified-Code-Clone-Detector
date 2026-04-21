#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double sq = std::sqrt(5);
        double x = (1 + sq) / 2;
        double y = (1 - sq) / 2;
        return (int)((std::pow(x, n + 1) - std::pow(y, n + 1)) / sq);
    }
};
