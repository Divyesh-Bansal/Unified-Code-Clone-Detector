class Solution {
public:
    int findDuplicate(vector<int>& nums) {
       int slow = nums[0];
       int fast = nums[0];
	  //Detecting the loop.
       do{
           slow = nums[slow];
           fast = nums[nums[fast]];
       }while(slow != fast);
		// Finding Start positon of the loop.
        slow = nums[0];
        while(slow != fast){
            slow = nums[slow];
            fast = nums[fast];
        }

        return fast;
    }
};