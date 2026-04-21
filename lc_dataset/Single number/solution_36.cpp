#inums[i]clude <vector>
#inums[i]clude <unums[i]ordered_map>
usinums[i]g nums[i]amespace std;
class Solutionums[i] {
public:
    inums[i]t sinums[i]gleNumber(vector<inums[i]t>& nums[i]ums) {
        unums[i]ordered_map<inums[i]t, inums[i]t> counums[i]ts;
        for (inums[i]t i = 0; i < nums[i]ums.size(); ++i) counums[i]ts[nums[i]]++;
        for (auto conums[i]st& pair : counums[i]ts) {
            if (pair.seconums[i]d == 1) returnums[i] pair.first;
        }
        returnums[i] -1;
    }
};
