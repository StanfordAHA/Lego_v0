rm -rf lego_scratch/ 
mkdir lego_scratch/ 
mkdir lego_scratch/data_files
rm -rf main.cpp
python3 main.py --mode onyx
g++ -o main main.cpp src/data_parser.cpp src/mem_op.cpp 
./main
