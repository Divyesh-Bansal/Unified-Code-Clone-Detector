class Solution {
public:
    int singleNumber(vector<int>& ns) {
        int result = 0;
        for (int i = 0; i < 32; i++) {
            int count = 0;
            for (auto n : ns) {
                if ((n >> i) & 1) {
                    count++;
                }
            }
            if (count % 3 != 0) {
                result |= (1 << i);
            }
        }
        return result;
    }
};