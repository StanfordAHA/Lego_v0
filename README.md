## Lego_v0 

### Setup

On Kiwi clone sam inside the Lego_v0 repository and checkout branch with fixes: 

```
git clone https://github.com/weiya711/sam.git
git checkout mapping_to_cgra
```

Follow read me to install sam (do this in a python 3.8.10 env) might be more steps to get it right

```
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt (idk which one)
pip install -e .
```

Your bashrc should have (you might need to mkdir these as well)

```
export SUITESPARSE_PATH=/nobackup/owhsu/sparse-datasets/suitesparse/
export TACO_TENSOR_PATH=/nobackup/owhsu/sparse-datasets/other
export FROSTT_PATH=/home/avb03/sparse-datasets/tensors/
export SUITESPARSE_FORMATTED_PATH=/nobackup/$(whoami)/sam/SUITESPARSE_FORMATTED
export FROSTT_FORMATTED_TACO_PATH=/nobackup/$(whoami)/sam/FROST_FORMATTED_TACO
export FROSTT_FORMATTED_PATH=/nobackup/$(whoami)/sam/FROST_FORMATTED
```
### Input Language 

#### 
-- program.txt
```
numops: 2                                         // Number of operands
stmt: A(ij) = B(ik) * C(kj)                       // Expression
schedule_ap:   [ikj]                              // Schedule on tile-coordinates
schedule_cp:   [ikj]                              // Schedule on subtile-coordinates
schedule_cgra: [ijk]                              // Schedule on cgra-coordinates
splits: [[240, 30] [240, 30] [240, 30]]           // Splits of the indices i, j, k
ssplit: [ijk]                                     // Mapping for the aforementioned splits 
```

####
-- tensor.txt 
```
B, C              // Tensor name
nemeth01          // App name - B
nemeth02          // App name - C
ss                // App type - B - Suitesparse
ss                // App type - C - Suitesparse
```

####
-- To run: 
```
chmod  +x lego_run.sh
./lego_run.sh rtl // "rtl" is an optional flag for rtl test-outputs
```

####
Output tiles/sub-tiles are available at ```lego_scratch/data_files/```. 


