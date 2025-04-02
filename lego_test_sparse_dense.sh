rm -rf lego_scratch/ 
mkdir lego_scratch/ 
rm -rf main.cpp
rm -rf gold.cpp
python3 main.py -p $1 -t $2 -g s -m rtl -w --dense_iter
g++ -o main main.cpp dense_patch/src/data_parser.cpp dense_patch/src/mem_op.cpp dense_patch/src/bf16_op.cpp
./main tiling 
g++ -o gold gold.cpp dense_patch/src/data_parser.cpp dense_patch/src/mem_op.cpp dense_patch/src/bf16_op.cpp 
./gold
