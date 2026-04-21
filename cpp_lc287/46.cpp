class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        // slow pointer approach // floyds cycle

        int slow = nums[0], fast = nums[0];

        do{
            slow = nums[slow];  //update by +1
            fast = nums[nums[fast]];  //update by +2
        }while(slow != fast);

        slow = nums[0]; //reinitilize slow when both gets equal 
        while(slow != fast) {
            slow = nums[slow];  //update by +1
            fast = nums[fast]; //update by +1
        }

        return fast;
    }
};