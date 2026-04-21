class Solution {
public:
    int findDuplicate(vector<int>& nums) 
    {
        int n=nums.size();
        // Sort the array to bring duplicates next to each other
        sort(nums.begin(),nums.end());
        int x=nums[0],i;
        for(i=1;i<n;i++)
        {
            x=x^nums[i]; // XOR the current element with x
            if(x==0) break; // If x becomes 0, it means we found a duplicate
            else x=nums[i];
        }
        return nums[i]; // Return the duplicate number
    }
};