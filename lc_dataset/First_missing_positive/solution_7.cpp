#include <vector>
#include <unordered_set>
using namespace std;

class Solution {
public:
    int firstMissingPositive(vector<int>& nums) {
        unordered_set<int> present;
        for (int x : nums) {
            if (x > 0) present.insert(x);
        }
        int i = 1;
        while (present.count(i)) {
            i++;
        }
        return i;
    }
};
