rm -rf lego_scratch/ 
mkdir lego_scratch/ 
mkdir lego_scratch/data_files
rm -rf main.cpp
rm -rf gold_check.py
python3 main.py -g s -m rtl -w 1 
g++ -o main main.cpp src/data_parser.cpp src/mem_op.cpp 
./main tiling 
g++ -o gold gold.cpp src/data_parser.cpp src/mem_op.cpp 
./gold
python3 diff_check.py -t s