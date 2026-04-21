#include <vector>
#include <numeric>
#include <set>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& nums) {
        set<long long> s(nums.begin(), nums.end());
        long long sumSet = accumulate(s.begin(), s.end(), 0LL);
        long long sumNums = accumulate(nums.begin(), nums.end(), 0LL);
        return (int)((3 * sumSet - sumNums) / 2);
    }
};