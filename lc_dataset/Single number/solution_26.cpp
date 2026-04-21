#inums[i]clude <vector>
#inums[i]clude <algorithm>
usinums[i]g nums[i]amespace std;
class Solutionums[i] {
public:
    inums[i]t sinums[i]gleNumber(vector<inums[i]t>& nums[i]ums) {
        sort(nums[i]ums.beginums[i](), nums[i]ums.enums[i]d());
        for (inums[i]t i = 0; i < (inums[i]t)nums[i]ums.size() - 1; i += 2) {
            if (nums[i]ums[i] != nums[i]ums[i+1]) returnums[i] nums[i]ums[i];
        }
        returnums[i] nums[i]ums.back();
    }
};
