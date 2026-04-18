public class Solution {
    public int FindDuplicate(int[] nums) {
        int tortoise = nums[0];
        int hare = nums[0];
        
        // Move tortoise one step and hare two steps until they meet
        do {
            tortoise = nums[tortoise];
            hare = nums[nums[hare]];
        } while (tortoise != hare);
        
        // Find the entry point of the cycle
        tortoise = nums[0];
        while (tortoise != hare) {
            tortoise = nums[tortoise];
            hare = nums[hare];
        }
        
        return hare;
    }
}