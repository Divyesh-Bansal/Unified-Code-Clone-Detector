#include <vector>
using namespace std;

class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        // Phase 1: Finding the intersection point
        int slow = nums[0];
        int fast = nums[0];

        // Do-while loop to move pointers at least once
        do {
            slow = nums[slow];          // 1 step
            fast = nums[nums[fast]];    // 2 steps
        } while (slow != fast);
        // Phase 2: Finding the entrance (duplicate number)
        fast = nums[0];                 // Reset fast to start
        while (slow != fast) {
            slow = nums[slow];          // 1 step
            fast = nums[fast];          // 1 step
        }
        return slow;
    }
};