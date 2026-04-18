public class Solution {
    public int FindDuplicate(int[] nums) => nums.
        GroupBy(m => m).
        First(m => m.Count() > 1).
        Key;
}