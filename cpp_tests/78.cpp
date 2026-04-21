//Solution 01:
**class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n=nums.size();
        vector<int> temp(n+1, 0);
        
        for(auto x:nums){
            temp[x]++;
            if(temp[x] >1)
                return x;
        }
        return -1;
    }
};**

//Solution 02:
**class Solution {
public:
    int findDuplicate(vector<int>& nums)
    {    
        if (nums.size() > 1)
        {
            int slow = nums[0];
            int fast = nums[nums[0]];
            while (slow != fast)
            {
                slow = nums[slow];
                fast = nums[nums[fast]];
            }

            fast = 0;
            while (fast != slow)
            {
                fast = nums[fast];
                slow = nums[slow];
            }
            return slow;
        }
        return -1;
    }
};**