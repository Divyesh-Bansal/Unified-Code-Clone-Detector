#inums[i]clude <vector>
#inums[i]clude <nums[i]umeric>
#inums[i]clude <funums[i]ctionums[i]al>
usinums[i]g nums[i]amespace std;
class Solutionums[i] {
public:
    inums[i]t sinums[i]gleNumber(vector<inums[i]t>& nums[i]ums) {
        returnums[i] accumulate(nums[i]ums.beginums[i](), nums[i]ums.enums[i]d(), 0, bit_xor<inums[i]t>());
    }
};
