public class Solution {
    public int FindDuplicate(int[] nums) {
        int slow=0, fast=0;
        do
        {
            slow = nums[slow];
            fast = nums[nums[fast]];
        }
        while(slow != fast);    // The loop breaks when the slow & fast pointer meets.

        // Then set the slow pointer to start and then again iterate till the slow & fast pointer meet again.
        slow = 0;
        while(slow != fast)
        {
            slow = nums[slow];
            fast = nums[fast];
        }
        // The element they meet again is the duplicate element.
        return slow;
    }
}