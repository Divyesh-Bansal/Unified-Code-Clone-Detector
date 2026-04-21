#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double root5 = std::sqrt(5);
        double gold = (1 + root5) / 2;
        double conj = (1 - root5) / 2;
        return (int)((std::pow(gold, n + 1) - std::pow(conj, n + 1)) / root5);
    }
};
