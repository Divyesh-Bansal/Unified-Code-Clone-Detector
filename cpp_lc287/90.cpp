class Solution {
public:

// This method modifies the original array so, we cannot use this.

    // int findDuplicate(vector<int>& nums) {
       
    //    // Note that here, the numbers i.e nums[i] are all valid indices i.e nums[i] can be considered as valid indices.

    //    for(int i=0;i<nums.size();i++){

    //     int val=abs(nums[i]);

    //     if(nums[val]<0)  // using val as index.
    //     return val;

    //     nums[val]*=-1;
    //    }

    //    return -1;
    // }



    int findDuplicate(vector<int>& nums) {
       
       // Using slow-fast pointer approach just like in LinkedList.

       // for the 1st test case: 1->3->2->4
                           //          |__|
        
        int slow=nums[0];
        int fast=nums[0];

        slow=nums[slow];  // move slow one step initially.
        fast=nums[nums[fast]]; // move fast 2 steps initially.

        while(slow!=fast){
            slow=nums[slow];
            fast=nums[nums[fast]];
        }

        // now place 'slow' at the starting point and again repeat the same process but now you have to move both 'slow' and 'fast' only one step at a time.

        slow=nums[0];

        while(slow!=fast){
            slow=nums[slow];
            fast=nums[fast];
        }

        return slow;

    }
};