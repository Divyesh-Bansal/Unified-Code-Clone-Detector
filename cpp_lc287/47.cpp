class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int ans = -1;
        int n = nums.size();
        for (int i = 0; i < n; i++) {
            int x = abs(nums[i]);
            if (nums[x] < 0) {
                ans = x;
                break;
            } else {
                nums[x] = -nums[x];
            }
        }
        return ans;
    }
};