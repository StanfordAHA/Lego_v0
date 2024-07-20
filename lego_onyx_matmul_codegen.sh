rm -rf lego_scratch/ 
mkdir lego_scratch/ 
rm -rf main.cpp
python3 main.py --mode onyx
sed -i 's/schedule_cgra: \[ikj\]/schedule_cgra: [ijk]/g' input/program.txt 
python3 main.py --mode onyx --no_preprocess yes
sed -i 's/schedule_cgra: \[ijk\]/schedule_cgra: [ikj]/g' input/program.txt 
g++ -o main main.cpp src/data_parser.cpp src/mem_op.cpp 
./main

