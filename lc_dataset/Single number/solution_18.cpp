#include <vector>
#include <numeric>
#include <functional>
using namespace std;
class LeetCodeSolution {
public:
    int singleNumber(vector<int>& nums) {
        return accumulate(nums.begin(), nums.end(), 0, bit_xor<int>());
    }
};
