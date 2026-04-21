#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double dev = std::sqrt(5);
        double up = (1 + dev) / 2;
        double down = (1 - dev) / 2;
        return (int)((std::pow(up, n + 1) - std::pow(down, n + 1)) / dev);
    }
};
