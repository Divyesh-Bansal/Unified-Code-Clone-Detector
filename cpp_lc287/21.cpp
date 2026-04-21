class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        sort(nums.begin(), nums.end());

        // Iterate through the sorted array
        for (int i = 1; i < nums.size(); i++) {
            // Check if adjacent elements are equal
            if (nums[i] == nums[i - 1]) {
                return nums[i]; // Found the duplicate number
            }
        }

        return -1; // No duplicate found (shouldn't happen for this problem)
    }
};