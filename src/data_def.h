#include <vector>

struct cg_subtile2 {
    std::vector<int> mode_0; 
    std::vector<int> mode_1;
    std::vector<double> mode_vals;
};

struct cg_extents2 {
    std::vector<int> extents_mode_0;
    std::vector<int> extents_mode_1;
    std::vector<int> extents_mode_vals;
};

struct tile2 {
    std::vector<int> pos1;
    std::vector<int> crd1;
    std::vector<int> pos2;
    std::vector<int> crd2;
    std::vector<int> pos3;
    std::vector<int> crd3;
    std::vector<int> pos4;
    std::vector<int> crd4;
    std::vector<double> vals;
};

struct subtile2 {
    std::vector<int> pos1;
    std::vector<int> crd1;
    std::vector<int> pos2;
    std::vector<int> crd2;
    std::vector<double> vals;
};