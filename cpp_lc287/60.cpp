class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        vector<bool> check(nums.size(), false);
        for (int n : nums) {
            if (check[n]) {
                return n;
            }
            check[n] = true;
        }
        return -1; // Should never happen based on constraints
    }