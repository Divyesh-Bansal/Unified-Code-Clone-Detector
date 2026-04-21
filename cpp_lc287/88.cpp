class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int slow = nums[0], fast = nums[0];

        // Step 1: Detect cycle using Floyd's Tortoise and Hare algorithm
        do {
            slow = nums[slow];        // Move slow one step
            fast = nums[nums[fast]]; // Move fast two steps
        } while (slow != fast);

        // Step 2: Find the start of the cycle
        slow = nums[0]; // Reset slow to the start
        while (slow != fast) {
            slow = nums[slow];
            fast = nums[fast];
        }

        // The meeting point is the duplicate number
        return slow;
    }
};