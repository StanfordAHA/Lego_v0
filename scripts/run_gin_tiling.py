import os
import subprocess
import glob
import argparse
from pathlib import Path

GINConv_layers = ["GINConv_layer0", "GINConv_layer1", "GINConv_layer2", "GINConv_layer3"]
GINConv_kernels = ["aggr_feat", "mlp_layer0_trans", "mlp_layer0_bias", "mlp_layer1_trans", "mlp_layer1_bias"]
prediction_layers = ["prediction_layer0", "prediction_layer1", "prediction_layer2", "prediction_layer3", "prediction_layer4"]
prediction_kernels = ["graph_pool", "linear_trans", "linear_bias", "score_accu"]

parser = argparse.ArgumentParser(
                prog='run_gin',
                description='Tiling & Reduction Automation Script for GIN',)
parser.add_argument("--mode", type=str, help="The mode to run the script in", default=["tiling", "reduce"])
parser.add_argument("--end2end", action="store_true", help="Run the entire gin model end to end")
args = parser.parse_args()

if args.mode == "tiling":
    prev_kernel = None
    for ginconv_layer in GINConv_layers:
        GINConv_layer_path = os.path.join("input/gin", ginconv_layer)
        for kernel in GINConv_kernels:
            print(f"Tiling {ginconv_layer} {kernel}")
            if args.end2end and prev_kernel is not None:
                try:
                    print(f"=== Copying Previous Kernel Output ===")
                    last_kernel_output_dir = glob.glob(f"output/*_{prev_kernel}")
                    last_kernel_output_mat = f"{last_kernel_output_dir[0]}/output.npy"
                    print(last_kernel_output_mat)
                    if kernel == "aggr_feat":
                        dest_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{ginconv_layer}/{kernel}/C_end2end.npy"
                    else:
                        dest_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{ginconv_layer}/{kernel}/B_end2end.npy"
                    dest_file_dir = os.path.dirname(dest_file)
                    Path(dest_file_dir).mkdir(parents=True, exist_ok=True)
                    copy = subprocess.run(["cp", last_kernel_output_mat, dest_file], capture_output=True, text=True)
                    copy.check_returncode()
                except subprocess.CalledProcessError as e:
                    print(e.stderr)
                    raise RuntimeError

            program_file = os.path.join(GINConv_layer_path, kernel + "_program.txt")
            if not args.end2end:
                tensor_file = os.path.join(GINConv_layer_path, kernel + "_tensor.txt")
            else:
                tensor_file = os.path.join(GINConv_layer_path, kernel + "_tensor_end2end.txt")

            try:
                print(f"=== Generating cpp code ===")
                gen = subprocess.run(["python", "main.py", "--program", program_file, 
                                            "--tensor", tensor_file, "--output_dir" , "output",
                                            "--mode", "rtl", "--workspace"], 
                                            capture_output=True, text=True)
                gen.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError

            try: 
                print(f"=== Compiling cpp code ===")
                compile = subprocess.run(["g++", "-o", "main", "main.cpp", "src/data_parser.cpp", "src/mem_op.cpp", "src/activation.cpp", "src/bf16_op.cpp"],
                                        capture_output=True, text=True)   

                compile.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError

            try: 
                print(f"=== Tiling ===")
                tile = subprocess.run(["./main", "tiling"],
                                        capture_output=True, text=True)

                tile.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError

            try: 
                print(f"=== Checking Tiled Results ===")
                output_dir = glob.glob(f"output/*_{ginconv_layer}_{kernel}")
                gold_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{ginconv_layer}/{kernel}/X.npy"
                check_gold_cmd = ["python", "scripts/check_gold.py", "--gold", gold_file, 
                                  "--input", f"{output_dir[0]}/output.txt", "--bf16"]
                if args.end2end:
                    check_gold_cmd.append("--dump_numpy")
                    # check_gold_cmd.append("--skip_check")
                check = subprocess.run(check_gold_cmd, capture_output=True, text=True)
                print(check.stdout)
                check.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError
            
            prev_kernel = f"{ginconv_layer}_{kernel}"

elif args.mode == "reduce":
    for ginconv_layer in GINConv_layers:
        GINConv_layer_path = os.path.join("input/gin", ginconv_layer)
        for kernel in GINConv_kernels:
            print(f"Reducing {ginconv_layer} {kernel}")
            try:
                print("=== Removing Current output.txt ===")
                output_dir = glob.glob(f"output/*_{ginconv_layer}_{kernel}")
                rm = subprocess.run(["rm", f"output/{output_dir[0]}/output.txt"], capture_output=True, text=True)
                rm.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError
            
            try:
                print(f"=== Reducing ===")
                reduce = subprocess.run(["./main", "reduce"],
                                        capture_output=True, text=True)
                reduce.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError
            
            try: 
                print(f"=== Checking Reduced Results ===")
                output_dir = glob.glob(f"output/*_{ginconv_layer}_{kernel}")
                gold_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{ginconv_layer}/{kernel}/X.npy"
                check = subprocess.run(["python", "scripts/check_gold.py", "--gold", gold_file,
                                    "--input", f"{output_dir[0]}/output.txt", "--bf16"],
                                        capture_output=True, text=True)
                print(check.stdout)
                check.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError

if args.mode == "tiling":
    prev_kernel = None
    for prediction_layer in prediction_layers:
        prediction_layer_path = os.path.join("input/gin", prediction_layer)
        for kernel in prediction_kernels:
            if kernel == "score_accu" and prediction_layer == "prediction_layer0":
                continue

            if args.end2end and prev_kernel is not None:
                try:
                    print(f"=== Copying Previous Kernel Output ===")
                    if kernel == "graph_pool":
                        layer_idx = int(prediction_layer[-1])
                        last_kernel_output_dir = glob.glob(f"output/*_GINConv_layer{layer_idx - 1}_mlp_layer1_bias")
                    else:
                        last_kernel_output_dir = glob.glob(f"output/*_{prev_kernel}")
                    last_kernel_output_mat = f"{last_kernel_output_dir[0]}/output.npy"
                    if kernel == "graph_pool":
                        dest_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{prediction_layer}/{kernel}/C_end2end.npy"
                    else:
                        dest_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{prediction_layer}/{kernel}/B_end2end.npy"
                    dest_file_dir = os.path.dirname(dest_file)
                    Path(dest_file_dir).mkdir(parents=True, exist_ok=True)
                    copy = subprocess.run(["cp", last_kernel_output_mat, dest_file], capture_output=True, text=True)
                    copy.check_returncode()
                except subprocess.CalledProcessError as e:
                    print(e.stderr)
                    raise RuntimeError
                
                if kernel == "score_accu":
                    try:
                        print(f"=== Copying Previous Score Accu Kernel Output ===")
                        layer_idx = int(prediction_layer[-1])
                        if layer_idx == 1:
                            last_score_accu_output_dir = glob.glob(f"output/*prediction_layer0_linear_bias")
                        else:
                            last_score_accu_output_dir = glob.glob(f"output/*prediction_layer{layer_idx - 1}_score_accu")
                        last_score_accu_output_mat = f"{last_score_accu_output_dir[0]}/output.npy"
                        dest_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{prediction_layer}/{kernel}/C_end2end.npy"
                        dest_file_dir = os.path.dirname(dest_file)
                        Path(dest_file_dir).mkdir(parents=True, exist_ok=True)
                        copy = subprocess.run(["cp", last_score_accu_output_mat, dest_file], capture_output=True, text=True)
                        copy.check_returncode()
                    except subprocess.CalledProcessError as e:
                        print(e.stderr)
                        raise RuntimeError
                
            print(f"Running {prediction_layer} {kernel}")
            program_file = os.path.join(prediction_layer_path, kernel + "_program.txt")
            if not args.end2end:
                tensor_file = os.path.join(prediction_layer_path, kernel + "_tensor.txt")
            else:
                tensor_file = os.path.join(prediction_layer_path, kernel + "_tensor_end2end.txt")
            try:
                print(f"=== Generating cpp code ===")
                gen = subprocess.run(["python", "main.py", "--program", program_file, 
                                            "--tensor", tensor_file, "--output_dir" , "output",
                                            "--mode", "rtl", "--workspace", 
                                            "--scratch_dir", f"{prediction_layer}_{kernel}_scratch"], 
                                            capture_output=True, text=True)
                gen.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError

            try: 
                print(f"=== Compiling cpp code ===")
                compile = subprocess.run(["g++", "-o", f"{prediction_layer}_{kernel}_main", "main.cpp", "src/data_parser.cpp", "src/mem_op.cpp", "src/activation.cpp", "src/bf16_op.cpp"],
                                        capture_output=True, text=True)   

                compile.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)

            try: 
                print(f"=== Tiling ===")
                tile = subprocess.run([f"./{prediction_layer}_{kernel}_main", "tiling"],
                                        capture_output=True, text=True)

                tile.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
            
            try: 
                print(f"=== Checking Tiled Results ===")
                output_dir = glob.glob(f"output/*_{prediction_layer}_{kernel}")
                gold_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{prediction_layer}/{kernel}/X.npy"
                check_gold_cmd = ["python", "scripts/check_gold.py", "--gold", gold_file, 
                                  "--input", f"{output_dir[0]}/output.txt", "--bf16"]
                if args.end2end:
                    check_gold_cmd.append("--dump_numpy")
                    # check_gold_cmd.append("--skip_check")
                check = subprocess.run(check_gold_cmd, capture_output=True, text=True)
                print(check.stdout)
                check.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)

            prev_kernel = f"{prediction_layer}_{kernel}"
        
elif args.mode == "reduce":
    for prediction_layer in prediction_layers:
        prediction_layer_path = os.path.join("input/gin", prediction_layer)
        for kernel in prediction_kernels:
            if kernel == "score_accu" and prediction_layer == "prediction_layer0":
                continue
            print(f"Reducing {prediction_layer} {kernel}")
            try:
                print("=== Removing Current output.txt ===")
                output_dir = glob.glob(f"output/*_{prediction_layer}_{kernel}")
                rm = subprocess.run(["rm", f"{output_dir[0]}/output.txt"], capture_output=True, text=True)
                rm.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError
            
            try:
                print(f"=== Reducing ===")
                reduce = subprocess.run([f"./{prediction_layer}_{kernel}_main", "reduce"],
                                        capture_output=True, text=True)
                reduce.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError
            
            try: 
                print(f"=== Checking Reduced Results ===")
                output_dir = glob.glob(f"output/*_{prediction_layer}_{kernel}")
                gold_file = f"/nobackup/bwcheng/sparse-datasets/sparse-ml/gin/bf16/COLLAB/{prediction_layer}/{kernel}/X.npy"
                check = subprocess.run(["python", "scripts/check_gold.py", "--gold", gold_file,
                                    "--input", f"{output_dir[0]}/output.txt", "--bf16"], 
                                        capture_output=True, text=True)
                print(check.stdout)
                check.check_returncode()
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                raise RuntimeError