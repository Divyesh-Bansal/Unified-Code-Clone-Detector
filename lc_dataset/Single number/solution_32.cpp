#include <vector>
#include <unordered_map>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& nums) {
        unordered_map<int, int> counts;
        for (int n : nums) counts[n]++;
        for (auto const& pair : counts) {
            if (pair.second == 1) return pair.first;
        }
        return -1;
    }
};
