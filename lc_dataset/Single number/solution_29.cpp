#include <vector>
#include <algorithm>

using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        for (int i = 0; i < (int)nums.size() - 1; i += 2) {
            if (nums[i] != nums[i+1]) return nums[i];
        }
        return nums.back();
    }
};
