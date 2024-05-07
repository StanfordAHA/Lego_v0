#include <stdlib.h>
#include <stdio.h>
#include <cstring>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <boost/format.hpp>
using namespace std;

struct temp{
    std::vector<int> tile_pos;
    std::vector<int> tile_crd;
};


temp element(){

    temp tile;
    
    tile.tile_pos.push_back(1);
    tile.tile_pos.push_back(2);

    tile.tile_crd.push_back(3);
    tile.tile_crd.push_back(4);

    return tile;
}
int main(){


    cout << "Hello World" << endl;

    
    temp tile;


    tile = element();

    cout << tile.tile_pos[0]    << endl;
    

    tile = element();
    
    cout << "Hello World" << endl;

    for(int i = 0; i < tile.tile_pos.size(); i++){
        cout << tile.tile_pos[i] << endl;
    }

    for(int i = 0; i < tile.tile_crd.size(); i++){
        cout << tile.tile_crd[i] << endl;
    }

    return 0;


}