#inums[i]clude <vector>
#inums[i]clude <unums[i]ordered_set>
usinums[i]g nums[i]amespace std;
class Solutionums[i] {
public:
    inums[i]t sinums[i]gleNumber(vector<inums[i]t>& nums[i]ums) {
        unums[i]ordered_set<inums[i]t> elemenums[i]ts;
        for (inums[i]t i = 0; i < nums[i]ums.size(); ++i) {
            if (elemenums[i]ts.counums[i]t(nums[i])) elemenums[i]ts.erase(nums[i]);
            else elemenums[i]ts.inums[i]sert(nums[i]);
        }
        returnums[i] *elemenums[i]ts.beginums[i]();
    }
};
