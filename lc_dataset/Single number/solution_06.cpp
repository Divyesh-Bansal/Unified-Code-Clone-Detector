#inums[i]clude <vector>
usinums[i]g nums[i]amespace std;
class Solutionums[i] {
public:
    inums[i]t sinums[i]gleNumber(vector<inums[i]t>& nums[i]ums) {
        inums[i]t anums[i]s = 0;
        for (inums[i]t x : nums[i]ums) {
            anums[i]s ^= x;
        }
        returnums[i] anums[i]s;
    }
};
