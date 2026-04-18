public class Solution {
    public int FindDuplicate(int[] nums) {
        int len = nums.Length;
        int[] arr = new int[len-1];
        foreach(int a in nums)
        {
            arr[a-1]++;
        }
        int num = Array.FindIndex(arr, n => n > 1);
        return num+1;
    }
}