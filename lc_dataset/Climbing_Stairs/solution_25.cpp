#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> storage(n + 1);
        storage[1] = 1;
        storage[2] = 2;
        for (int pos = 3; pos <= n; pos++) {
            storage[pos] = storage[pos - 1] + storage[pos - 2];
        }
        return storage[n];
    }
};
