class Solution {
public:
    int singleNumber(vector<int>& input_data) {
        int ones = 0, twos = 0;
        for (int num : input_data) {
            ones = (ones ^ num) & ~twos;
            twos = (twos ^ num) & ~ones;
        }
        return ones;
    }
};