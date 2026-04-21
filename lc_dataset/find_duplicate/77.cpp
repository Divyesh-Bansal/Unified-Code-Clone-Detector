class Solution {
private:
    int check(vector<int>& nums, int value) {
        int count = 0;
        // value = mid ; 
        for (auto&num : nums){
            if(num <= value){
                count++;
            }
            //array = [1, 2, 3 , 4, 5] ,  it means no of unique values must(1,2,3,4,5) <= 5, if count > mid we reduce right = mid - 1; 
            // if no of uniquem values <= 5, so the 5 is already in the count(we have 5 as count) , so 5 is not the duplicate
        }
        return count;
        // return count;
    }
public:
    int findDuplicate(vector<int>& nums) {
        int left = 1;
        int right = nums.size() - 1;
        while (left <= right){
            int mid = left + (right - left) / 2;
            if (check(nums, mid) > mid) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
};