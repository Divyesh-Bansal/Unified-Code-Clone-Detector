#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double val = std::sqrt(5);
        double major = (1 + val) / 2;
        double minor = (1 - val) / 2;
        return (int)((std::pow(major, n + 1) - std::pow(minor, n + 1)) / val);
    }
};
