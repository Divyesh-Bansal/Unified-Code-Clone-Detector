class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        unordered_map<int, int> numCount; // Map to store the count of each number

    // Iterate through the array and count the occurrences of each number
        for (int num : nums) {
            if (numCount.find(num) != numCount.end()) {
                return num; // Found the duplicate number
            }
            numCount[num] = 1;
        }

        return -1; // No duplicate found (shouldn't happen for this problem)  
    }
};