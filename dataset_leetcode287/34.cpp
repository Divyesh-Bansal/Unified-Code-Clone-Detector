class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        vector<int>dp(nums.size(), 0);
        for(int i =0 ;i<nums.size();i++){
            if(dp[nums[i]] > 0)return nums[i];
            dp[nums[i]]++;
        }
        return 0;
    }
};