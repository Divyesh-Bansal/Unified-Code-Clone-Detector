#include <iostream>

class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        int steps_1 = 1, steps_2 = 2;
        for (int i = 3; i <= n; ++i) {
            int total = steps_1 + steps_2;
            steps_1 = steps_2;
            steps_2 = total;
        }
        return steps_2;
    }
};
