class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n=nums.size();
        vector<int>store(n+1);
        for(int i=0;i<n;i++){
            if(store[nums[i]]){
                return nums[i];
            }
            store[nums[i]]++;
        }
        return 0;
    }
};