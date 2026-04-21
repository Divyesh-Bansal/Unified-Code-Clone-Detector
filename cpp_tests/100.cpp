class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        //using cycle detetction method
        int fast=nums[0];
        int slow=nums[0];
        do
        {
            slow=nums[slow]; // 3 2
            fast=nums[nums[fast]]; // 2 2
        }
        while(fast!=slow);

        fast=nums[0];

        while(fast!=slow)
        {
            fast=nums[fast];
            slow=nums[slow];
        }

        return fast;

    }
};