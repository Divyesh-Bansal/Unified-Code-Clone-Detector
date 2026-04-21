class Solution {
    public int findDuplicate(int[] nums) {
        /** 
         Imagine the index is pointing to the next elment in the linked list.
         In case of duplicate number, two different indexes point to the same duplicate number
          [3,   1,   3,   4,   2]
           ↑    ↑    ↑    ↑    ↑
           0    1    2    3    4
         */
        // Phase 1: Finding the intersection point
        int slow = 0;
        int fast = 0;
       
        while (true) {
            slow = nums[slow];
            fast = nums[fast];
            fast = nums[fast];

            if (slow == fast) {
                // loop detected, 
                // Phase 2: Now find the starting point of the loop.
                // reset the slow pointer i.e. move it to the 0-th index of the nums array 
                slow = 0;
                while (slow != fast) {
                    slow = nums[slow];
                    fast = nums[fast];
                }
                return slow;   
            }
        }
    }
}