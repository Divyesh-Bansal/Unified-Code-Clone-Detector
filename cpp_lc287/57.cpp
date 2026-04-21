class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int start = nums[0];
        int end = nums[0];
        do{
            start = nums[start];
            end = nums[nums[end]];
        }while(start!=end);
        start= nums[0];
        while(end!= start){
            start = nums[start];
            end = nums[end];
        }
        return start;
    }
};