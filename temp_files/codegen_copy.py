from pyparsing import Word, alphas, one_of, alphanums

def file_parser(input_file):
    with open(input_file, 'r') as f:
        data = f.read().splitlines()
    return data

def data_parser(data):
    data = [i for i in data]

    if(len(data) == 1):
        print("Schedule or Expr not specified!")

    data = [i.replace(" ", "") for i in data]

    arith_op = one_of("+ - * /")

    expr_rule = Word(alphas) + ":" + \
            Word(alphas) + '(' + Word(alphas) + ')' +  '=' + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')'

    expr = expr_rule.parseString(data[0])

    dest = {}
    dest[expr[2]] = list(expr[4])

    op1 = {}
    op2 = {}

    op1[expr[7]] = list(expr[9])
    op2[expr[12]] = list(expr[14])
    op = expr[11]

    schedule_rule = Word(alphas) + ':' + '(' + Word(alphas) + ')'
    schedule = list((schedule_rule.parseString(data[1]))[3])

    format_rule = Word(alphas) + ':' + Word(alphas)
    tformat = format_rule.parseString(data[2])[2]

    format_rule = Word(alphas) + ':' + '(' + Word(alphanums) + ',' + Word(alphanums) + ')'
    tsize1 = format_rule.parseString(data[3])[3]
    tsize2 = format_rule.parseString(data[3])[5]

    format_rule = Word(alphas) + ':' + '(' + Word(alphanums) + ',' + Word(alphanums) + ')'
    stsize1 = format_rule.parseString(data[4])[3]
    stsize2 = format_rule.parseString(data[4])[5]
    
    return dest, op1, op2, op, schedule, tformat, tsize1, tsize2, stsize1, stsize2
   
def make_lattice(idx, op1, op2, op):
    idx_lattice = []

    is_present1 = False
    is_present2 = False

    if(len(op1) != 0):
        for arr_read in op1:    
            arr1 = arr_read

        for idx_arr1 in op1[arr1]:
            if(idx_arr1 == idx): 
                is_present1 = True

    if(len(op2) != 0):
        for arr_read in op2:
            arr2 = arr_read

        for idx_arr2 in op2[arr2]:
            if(idx_arr2 == idx): 
                is_present2 = True

    if(is_present1 and is_present2):
        idx_lattice.append([arr1 + idx,  arr2 + idx])
        if(op == '+'):
            idx_lattice.append([arr1 + idx])
            idx_lattice.append([arr2 + idx])
    elif(is_present1):
        idx_lattice.append([arr1 + idx])
    elif(is_present2):
        idx_lattice.append([arr2 + idx])
    else:
        idx_lattice.append(['phi'])

    return idx_lattice
               
def while_node(cond, stmts, op1, op2):
    stmt_list = []
    if(len(cond) == 2):
        arr_idx1 = cond[0][-1]
        arr_read1 = cond[0][:-1]

        arr_idx2 = cond[1][-1]
        arr_read2 = cond[1][:-1]

        if(len(op1) != 0):
            if(arr_read1 in op1):
                idx_arr1 = op1[arr_read1].index(arr_idx1)
                idx_arr1 += 1
                while_cond1 = arr_idx1 + arr_read1 + " < " + "p" + arr_read1 + str(idx_arr1) + "_end"

            if(arr_read2 in op1):
                idx_arr2 = op1[arr_read2].index(arr_idx2)
                idx_arr2 += 1
                while_cond2 = arr_idx2 + arr_read2 + " < " + "p" + arr_read2 + str(idx_arr2) + "_end"

        if(len(op2) != 0):
            if(arr_read1 in op2):
                idx_arr1 = op2[arr_read1].index(arr_idx1)
                idx_arr1 += 1
                while_cond1 = arr_idx1 + arr_read1 + " < " + "p" + arr_read1 + str(idx_arr1) + "_end"

            if(arr_read2 in op2):
                idx_arr2 = op2[arr_read2].index(arr_idx2)
                idx_arr2 += 1
                while_cond2 = arr_idx2 + arr_read2 + " < " + "p" + arr_read2 + str(idx_arr2) + "_end"

        stmt_list.append(["while(" + while_cond1 + " && " + while_cond2 + ") {"])

    elif(len(cond) == 1):

        arr_idx1 = cond[0][-1]
        arr_read1 = cond[0][:-1]

        if(len(op1) != 0):
            if(arr_read1 in op1):
                idx_arr1 = op1[arr_read1].index(arr_idx1)
                idx_arr1 += 1
                while_cond1 = arr_idx1 + arr_read1 + " < " + "p" + arr_read1 + str(idx_arr1) + "_end"
        
        if(len(op2) != 0):
            if(arr_read1 in op2):
                idx_arr1 = op2[arr_read1].index(arr_idx1)
                idx_arr1 += 1
                while_cond1 = arr_idx1 + arr_read1 + " < " + "p" + arr_read1 + str(idx_arr1) + "_end"

        stmt_list.append(["while(" + while_cond1 + ") {"])
        
    for s in stmts:
        stmt_list.append(s)
    stmt_list.append(["}"])
    return stmt_list

def bound_idx_def1(op1, arr_read, arr_idx):
    stmt_list = []
    if(len(op1) != 0): 
        if(arr_read in op1):
            idx_arr = op1[arr_read].index(arr_idx)
            new_idx = op1[arr_read][idx_arr]
            if(idx_arr == 0):
                stmt_list.append(["\t" + "int " + new_idx + arr_read + " = " + arr_read + str(idx_arr + 1) + "_pos[" + "0" + "];"])
                stmt_list.append(["\t" + "int " + "p" + arr_read + str(idx_arr + 1) + "_end" + " = " + arr_read + str(idx_arr + 1) + "_pos[" + "1" + "];"])
            else:
                new_arr_idx = op1[arr_read][idx_arr - 1]
                stmt_list.append(["\t" + "int " + new_idx + arr_read + " = " + arr_read + str(idx_arr + 1) + "_pos[" + new_arr_idx + arr_read + "];"])
                stmt_list.append(["\t" + "int " + "p" + arr_read + str(idx_arr + 1) + "_end" + " = " + arr_read + str(idx_arr + 1) + "_pos[" + new_arr_idx + arr_read + " + 1" + "];"])
            
    return stmt_list

def mem_cpy_def1(op1, arr_read, arr_idx, level):
    stmt_list = []
    if(len(op1) != 0): 
        if(arr_read in op1):
            idx_arr = op1[arr_read].index(arr_idx)
            idx_arr += 1
            
            if(len(op1[arr_read]) == idx_arr):
                if(level == "cp"):
                    stmt = "cp_cgra_mem_cpy_sparse(tile_" + arr_read + "_ptrs, "
                elif(level == "ap"):
                    stmt = "ap_cp_mem_cpy_sparse(tile_" + arr_read + "_ptrs, "

                stmt += arr_read + "_ptrs, "                
                stmt += arr_idx + arr_read + ");"

                stmt_list.append(["\t" + "\t" + stmt])

    return stmt_list

def bound_idx_def2(op1, arr_read1, arr_idx1, arr_read2, arr_idx2):
    stmt_list = []

    if(len(op1) != 0):
        if(arr_read1 in op1):
            idx_arr1 = op1[arr_read1].index(arr_idx1)
            new_idx = op1[arr_read1][idx_arr1]
            if(idx_arr1 == 0):
                stmt_list.append(["int " + new_idx + arr_read1 + " = " + arr_read1 + str(idx_arr1 + 1) + "_pos[" + "0" + "];"])
                stmt_list.append(["int " + "p" + arr_read1 + str(idx_arr1 + 1) + "_end" + " = " + arr_read1 + str(idx_arr1 + 1) + "_pos[" + "1" + "];"])
            else:
                new_arr_idx = op1[arr_read1][idx_arr1 - 1]
                stmt_list.append(["\t" + "int " + new_idx + arr_read1 + " = " + arr_read1 + str(idx_arr1 + 1) + "_pos[" + new_arr_idx + arr_read1 + "];"])
                stmt_list.append(["\t" + "int " + "p" + arr_read1 + str(idx_arr1 + 1) + "_end" + " = " + arr_read1 + str(idx_arr1 + 1) + "_pos[" + new_arr_idx + arr_read1 + " + 1" + "];"])
       
        if(arr_read2 in op1):
            idx_arr2 = op1[arr_read2].index(arr_idx2)
            new_idx = op1[arr_read2][idx_arr2]
            if(idx_arr2 == 0):
                stmt_list.append(["int " + new_idx + arr_read2 + " = " + arr_read2 + str(idx_arr2 + 1) + "_pos[" + "0" + "];"])
                stmt_list.append(["int " + "p" + arr_read2 + str(idx_arr2 + 1) + "_end" + " = " + arr_read2 + str(idx_arr2 + 1) + "_pos[" + "1" + "];"])
            else:
                new_arr_idx = op1[arr_read2][idx_arr2 - 1]
                stmt_list.append(["\t" + "int " + new_idx + arr_read2 + " = " + arr_read2 + str(idx_arr2 + 1) + "_pos[" + new_arr_idx + arr_read2 + "];"])
                stmt_list.append(["\t" + "int " + "p" + arr_read2 + str(idx_arr2 + 1) + "_end" + " = " + arr_read2 + str(idx_arr2 + 1) + "_pos[" + new_arr_idx + arr_read2 + " + 1" + "];"])

    return stmt_list

def assemble_begin(arr_read, idx_arr, arr_idx): 
    return [["\t"*2 + "int " + "p" + arr_read + str(idx_arr + 1) + "_begin" + " = " + arr_idx + arr_read + ";"]]

def assemble_increment(arr_read, arr_idx, dest, op, tformat):
    stmt_list = []

    idx_arr = dest[arr_read].index(arr_idx)

    if(len(dest[arr_read]) == idx_arr + 1):
        if(op == '*' and tformat == 'S'):
            stmt_list.append(["\t"*2 + "if(is_nz) {"])
            stmt_list.append(["\t"*2 + "\t" + arr_read + str(idx_arr + 1) + "_crd[" + arr_idx + arr_read + "] " + "= " + arr_idx + ";"])
            stmt_list.append(["\t"*2 + "\t" + arr_idx + arr_read + "++;"])
            stmt_list.append(["\t"*2 + "}"])
        else: 
            stmt_list.append(["\t"*2 + arr_read + str(idx_arr + 1) + "_crd[" + arr_idx + arr_read + "] " + "= " + arr_idx + ";"])
            stmt_list.append(["\t"*2 + arr_idx + arr_read + "++;"])
    else:
        new_arr_idx = dest[arr_read][idx_arr + 1]
        if(op == '*' and tformat == 'S'):
            stmt_list.append(["\t" + "if(is_nz) {"])
            stmt_list.append(["\t"*2 + arr_read + str(idx_arr + 2) + "_pos[" + arr_idx + arr_read + " + 1] = " + new_arr_idx + arr_read + ";"])
            stmt_list.append(["\t"*2 + "if(" + "p" + arr_read + str(idx_arr + 2) + "_begin" + " < " + new_arr_idx + arr_read + ") {"])
            stmt_list.append(["\t"*3 + arr_read + str(idx_arr + 1) + "_crd[" + arr_idx + arr_read + "] " + "= " + arr_idx + ";"])
            stmt_list.append(["\t"*3 + arr_idx + arr_read + "++;"])
            stmt_list.append(["\t"*2 + "}"])
            stmt_list.append(["\t" + "}"])
        else:
            stmt_list.append(["\t"*2 + arr_read + str(idx_arr + 2) + "_pos[" + arr_idx + arr_read + " + 1] = " + new_arr_idx + arr_read + ";"])
            stmt_list.append(["\t"*2 + "if(" + "p" + arr_read + str(idx_arr + 2) + "_begin" + " < " + new_arr_idx + arr_read + ") {"])
            stmt_list.append(["\t"*3 + arr_read + str(idx_arr + 1) + "_crd[" + arr_idx + arr_read + "] " + "= " + arr_idx + ";"])
            stmt_list.append(["\t"*3 + arr_idx + arr_read + "++;"])
            stmt_list.append(["\t"*2 + "}"])

    return stmt_list 

def mem_cpy_def2(op1, arr_read1, arr_idx1, arr_read2, arr_idx2, level):
    stmt_list = []

    if(len(op1) != 0):
        if(arr_read1 in op1):
            idx_arr1 = op1[arr_read1].index(arr_idx1)
            idx_arr1 += 1
            if(len(op1[arr_read1]) == idx_arr1):

                if(level == "cp"):
                    stmt = "cp_cgra_mem_cpy_sparse(tile_" + arr_read1 + "_ptrs, "
                elif(level == "ap"):
                    stmt = "ap_cp_mem_cpy_sparse(tile_" + arr_read1 + "_ptrs, "

                stmt += arr_read1 + "_ptrs, "
                stmt += arr_idx1 + arr_read1 + ");"

                stmt_list.append(["\t" + "\t" + stmt])

        if(arr_read2 in op1):
            idx_arr2 = op1[arr_read2].index(arr_idx2)
            idx_arr2 += 1
            if(len(op1[arr_read2]) == idx_arr2):

                if(level == "cp"):
                    stmt = "cp_cgra_mem_cpy_sparse(tile_" + arr_read2 + "_ptrs, "
                elif(level == "ap"):
                    stmt = "ap_cp_mem_cpy_sparse(tile_" + arr_read2 + "_ptrs, "

                stmt += arr_read2 + "_ptrs,"
                stmt += arr_idx2 + arr_read2 + ");"

                stmt_list.append(["\t" + "\t" + stmt])

    return stmt_list   

def if_node(conds, stmts, op1, op2, dest, tformat):

    stmt_list = []
    for i in range(len(conds)):
        if(i == 0):
            if(len(conds[i]) == 1):
                arr_idx = conds[i][0][-1]
                arr_read = conds[i][0][:-1]
                stmt_list.append((["\t" + "if(" + arr_idx + arr_read + "0" + " == " + arr_idx + ") {"]))
                
                for out_arr in dest:
                    out_arr_read = out_arr

                if(tformat == 'S'):

                    idx_arr = dest[out_arr_read].index(arr_idx)
                    new_idx_arr = idx_arr + 1
                    
                    if(len(dest[out_arr_read]) != new_idx_arr):
                        new_arr_idx = dest[out_arr_read][idx_arr + 1]
                        stmt_list.extend(assemble_begin(out_arr_read, new_idx_arr, new_arr_idx))

                stmt_list.extend(mem_cpy_def1(op1, arr_read, arr_idx, level))
                stmt_list.extend(mem_cpy_def1(op2, arr_read, arr_idx, level))

            elif(len(conds[i]) == 2):
                arr_idx1 = conds[i][0][-1]
                arr_read1 = conds[i][0][:-1]
                arr_idx2 = conds[i][1][-1]
                arr_read2 = conds[i][1][:-1]
                stmt_list.append((["\t" + "if(" + arr_idx1 + arr_read1 + "0" + " == " + arr_idx1 + " && " + arr_idx2 + arr_read2 + "0" + " == " + arr_idx2 + ") {"]))
               
                for out_arr in dest:
                    out_arr_read = out_arr

                if(tformat == 'S'):

                    idx_arr = dest[out_arr_read].index(arr_idx1)
                    new_idx_arr = idx_arr + 1
                   

                    if(len(dest[out_arr_read]) != new_idx_arr):
                        new_arr_idx = dest[out_arr_read][idx_arr + 1]
                        stmt_list.extend(assemble_begin(out_arr_read, new_idx_arr, new_arr_idx))

                stmt_list.extend(mem_cpy_def2(op1, arr_read1, arr_idx1, arr_read2, arr_idx2, level))
                stmt_list.extend(mem_cpy_def2(op2, arr_read1, arr_idx1, arr_read2, arr_idx2, level))

            stmt_list.append(stmts[i])

            arr_idx = conds[i][0][-1]

            if(tformat == 'S'):
                idx_arr = dest[out_arr_read].index(arr_idx)
                stmt_list.extend(assemble_increment(out_arr_read, arr_idx, dest, op, tformat))

            stmt_list.append(["\t" + "}"])
        else:   
            if(len(conds[i]) == 1):
                arr_idx = conds[i][0][-1]
                arr_read = conds[i][0][:-1]
                stmt_list.append((["\t" + "else if(" + arr_idx + arr_read + "0" + " == " + arr_idx + ") {"]))

                for out_arr in dest:
                    out_arr_read = out_arr

                if(tformat == 'S'):

                    idx_arr = dest[out_arr_read].index(arr_idx)
                    new_idx_arr = idx_arr + 1
                    new_arr_idx = dest[out_arr_read][idx_arr]

                    if(len(dest[out_arr_read]) != new_idx_arr):
                        new_arr_idx = dest[out_arr_read][idx_arr + 1]
                        stmt_list.extend(assemble_begin(out_arr_read, new_idx_arr, new_arr_idx))

                stmt_list.extend(mem_cpy_def1(op1, arr_read, arr_idx, level))
                stmt_list.extend(mem_cpy_def1(op2, arr_read, arr_idx, level))


            elif(len(conds[i]) == 2):
                arr_idx1 = conds[i][0][-1]
                arr_read1 = conds[i][0][:-1]
                arr_idx2 = conds[i][1][-1]
                arr_read2 = conds[i][1][:-1]
                stmt_list.append((["\t" + "else if(" + arr_idx1 + arr_read1 + "0" + " == " + arr_idx1 + " && " + arr_idx2 + arr_read2 + "0" + " == " + arr_idx2 + ") {"]))
                
                for out_arr in dest:
                    out_arr_read = out_arr

                if(tformat == 'S'):

                    idx_arr = dest[out_arr_read].index(arr_idx1)
                    new_idx_arr = idx_arr + 1
                    new_arr_idx = dest[out_arr_read][idx_arr]

                    if(len(dest[out_arr_read]) != new_idx_arr):
                        new_arr_idx = dest[out_arr_read][idx_arr + 1]
                        stmt_list.extend(assemble_begin(out_arr_read, new_idx_arr, new_arr_idx))

                stmt_list.extend(mem_cpy_def2(op1, arr_read1, arr_idx1, arr_read2, arr_idx2, level))
                stmt_list.extend(mem_cpy_def2(op2, arr_read1, arr_idx1, arr_read2, arr_idx2, level))

                if(tformat == 'S'):
                    idx_arr = dest[out_arr_read].index(arr_idx1)
                    stmt_list.extend(assemble_increment(out_arr_read, arr_idx1, dest, op, tformat))

            stmt_list.append(stmts[i])

            arr_idx = conds[i][0][-1]
            if(tformat == 'S'):
                idx_arr = dest[out_arr_read].index(arr_idx)
                stmt_list.extend(assemble_increment(out_arr_read, arr_idx, dest, op, tformat))

            stmt_list.append(["\t" + "}"])

    return stmt_list

def index_def(idx, op1, op2):
    
    arr_read = idx[:-1]
    arr_idx = idx[-1]

    if(len(op1) != 0):
        if(arr_read in op1):
            idx_arr1 = op1[arr_read].index(arr_idx)
            idx_arr1 += 1
            return ["\t" + "int " + arr_idx + arr_read + "0 " + "= " + arr_read + str(idx_arr1) + "_crd[" + arr_idx + arr_read + "];"] 

    if(len(op2) != 0): 
        if(arr_read in op2):
            idx_arr1 = op2[arr_read].index(arr_idx)
            idx_arr1 += 1
            return ["\t" + "int " + arr_idx + arr_read + "0 " + "= " + arr_read + str(idx_arr1) + "_crd[" + arr_idx + arr_read + "];"] 

    return ["def CI " + idx + ';']

def logical_def(idx):
    if(len(idx) == 1):
        arr_read = idx[0][:-1]
        arr_idx = idx[0][-1]
        return ["\t" + "int " + arr_idx + " = " + arr_idx + arr_read + "0;"] 
    elif(len(idx) == 2):
        arr_read1 = idx[0][:-1]
        arr_idx1 = idx[0][-1]
        arr_read2 = idx[1][:-1]
        arr_idx2 = idx[1][-1]
        return ["\t" + "int " + arr_idx1 + " = " + "min(" + arr_idx1 + arr_read1 + "0" + ", " + arr_idx2 + arr_read2 + "0" + ");"]  

def increment(idx):
    arr_read = idx[:-1]
    arr_idx = idx[-1]

    return ["\t" + arr_idx + arr_read + " += " + "(int)" + "(" + arr_idx + arr_read + "0" + " == " + arr_idx + ")" + ";"]

def start_idx_def(op1, op2):

    temp_stmt_list = []
    
    for arr_read in op1:
        arr_read1 = arr_read
        arr_idx1 = op1[arr_read][0]
        temp_stmt_list.append(["int " + arr_idx1 + arr_read1 + " = " + arr_read1 + "1_pos[0]" +  ";"])
        temp_stmt_list.append(["int " + "p" + arr_read1 + "1_end" + " = " + arr_read1 + "1_pos[1]" +  ";"])

    for arr_read in op2:
        arr_read2 = arr_read
        arr_idx2 = op2[arr_read][0]
        temp_stmt_list.append(["int " + arr_idx2 + arr_read2 + " = " + arr_read2 + "1_pos[0]" +  ";"])
        temp_stmt_list.append(["int " + "p" + arr_read2 + "1_end" + " = " + arr_read2 + "1_pos[1]" +  ";"])

    return temp_stmt_list        

def compute_block(op1, op2, dest, tformat, op, level):
    stmt_list = []

    for arr_read in dest:
        dest_read = arr_read
    
    for arr_read in op1:
        op1_read = arr_read

    for arr_read in op2:
        op2_read = arr_read

    dest_idx = dest[dest_read][-1]

    if(tformat == 'S'):
        if(op == '+'):
            if(level == "cp"):
                stmt_list.append(["\t" + "cgra_elemadd(tile_" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, tile_" + op2_read + "_ptrs);"])
                stmt_list.append(["\t" + "cgra_cp_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + dest_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])
            elif(level == "ap"):
                stmt_list.append(["\t" + "cp_elemadd(tile_" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, tile_" + op2_read + "_ptrs);"])
                stmt_list.append(["\t" + "cp_ap_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + dest_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])

        if(op == '*'): 
            if(level == "cp"):
                stmt_list.append(["\t" + "cgra_elemmul(tile_" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, tile_" + op2_read + "_ptrs);"])
                stmt_list.append(["\t" + "is_nz = tile_" + dest_read + "_pos1_ptr[1];"])
                stmt_list.append(["\t" + "if(is_nz) {"])
                stmt_list.append(["\t" + "\t" + "cgra_cp_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + dest_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])
                stmt_list.append(["\t" + "}"])
            elif(level == "ap"):
                stmt_list.append(["\t" + "cp_elemmul(tile_" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, tile_" + op2_read + "_ptrs);"])
                stmt_list.append(["\t" + "is_nz = tile_" + dest_read + "_pos1_ptr[1];"])
                stmt_list.append(["\t" + "if(is_nz) {"])
                stmt_list.append(["\t" + "\t" + "cp_ap_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + dest_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])
                stmt_list.append(["\t" + "}"])
    else: 
        if(op == '*'):
            # FIX this properly - No hacking
            stmt_list.append(["\t" + "cgra_matmul(tile_" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, tile_" + op2_read + "_ptrs)"])
            stmt = "cgra_cp_mem_cpy_dense(" + dest_read + "_ptrs, tile_" + dest_read + "_ptrs"; 

            dest_arr_dim = len(dest[dest_read])
            for i in range(dest_arr_dim):
                stmt += (", " + dest[dest_read][i])
            stmt += ");"

            stmt_list.append(["\t" + stmt])

                 
    return stmt_list

def add_copy_block(point, dest, tformat, op, level):

    stmt_list = []

    for dest_read in dest:
        dest_read = dest_read
    
    dest_idx = dest[dest_read][-1]
    op1_read = point[0][:-1]
    
    if(tformat == 'S'):
        if(op == '+'):
            if(level == "cp"):
                stmt_list.extend(["\t" + "\t" +  "cgra_cp_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])
            elif(level == "ap"):
                stmt_list.extend(["\t" + "\t" + "cp_ap_mem_cpy_sparse(" + dest_read + "_ptrs, tile_" + op1_read + "_ptrs, " + dest_idx + dest_read + ")" + ";"])

    return stmt_list

def make_stmts(schedule, op1, op2, op, dest, tformat, level):

    stmt_list = []

    lattice = make_lattice(schedule[0], op1, op2, op)

    if(len(lattice[0]) == 2):
        arr_read1 = lattice[0][0][:-1]
        arr_idx1 = lattice[0][0][-1]
        arr_read2 = lattice[0][1][:-1]
        arr_idx2 = lattice[0][1][-1]
        bound_idx_def1_stmts = bound_idx_def2(op1, arr_read1, arr_idx1, arr_read2, arr_idx2)
        stmt_list.extend(bound_idx_def1_stmts)
        bound_idx_def2_stmts = bound_idx_def2(op2, arr_read1, arr_idx1, arr_read2, arr_idx2)
        stmt_list.extend(bound_idx_def2_stmts)
    else: 
        arr_read = lattice[0][0][:-1]
        arr_idx = lattice[0][0][-1]
        bound_idx_def1_stmts = bound_idx_def1(op1, arr_read, arr_idx)
        stmt_list.extend(bound_idx_def1_stmts)
        bound_idx_def2_stmts = bound_idx_def1(op2, arr_read, arr_idx)
        stmt_list.extend(bound_idx_def2_stmts)
                
    for lattice_point in make_lattice(schedule[0], op1, op2, op): 
        if(len(lattice_point) == 2): 

            sub_points = []
            sub_points.append([lattice_point[0], lattice_point[1]])
            
            if(op == '+'):
                sub_points.append([lattice_point[0]])
                sub_points.append([lattice_point[1]])

            while_node_cond = [lattice_point[0], lattice_point[1]]
            while_stmt_list = []

            while_stmt_list.append(index_def(lattice_point[0], op1, op2))
            while_stmt_list.append(index_def(lattice_point[1], op1, op2))
            while_stmt_list.append(logical_def([lattice_point[0], lattice_point[1]]))

            conds_list = []
            stmts_list = []
            for point in sub_points:
                conds_list.append(point) 


                if(len(point) == 2):
                    if(len(schedule) == 1):
                        
                        compute_block_stmts = compute_block(op1, op2, dest, tformat, op, level)
                        stmts_list.append(compute_block_stmts)
                    else:
                        new_schedule = schedule[1:]
                        stmts_list.append(make_stmts(new_schedule, op1, op2, op, dest, tformat, level))
                elif(len(point) == 1):
                    
                    if(len(schedule) == 1):
                        add_copy_block_stmts = add_copy_block(point, dest, tformat, op, level)
                        stmts_list.append(add_copy_block_stmts)
                    else:
                        new_schedule = schedule[1:]
                        temp_idx = point[0][-1]
                        temp_arr = point[0][:-1]

                        new_op1 = op1
                        new_op2 = op2          

                        if(temp_arr not in op2):
                            is_present2 = False
                            for arr_read in op2:
                                for idx_arr2 in op2[arr_read]:
                                    if(idx_arr2 == temp_idx):
                                        is_present2 = True

                            if(is_present2):
                                new_op2 = {}
                        
                        if(temp_arr not in op1):
                            is_present1 = False
                            for arr_read in op1:
                                for idx_arr1 in op1[arr_read]:
                                    if(idx_arr1 == temp_idx):
                                        is_present1 = True

                            if(is_present1):
                                new_op1 = {}

                        stmts_list.append(make_stmts(new_schedule, new_op1, new_op2, op, dest, tformat, level))

            while_stmt_list.extend(if_node(conds_list, stmts_list, op1, op2, dest, tformat))
            while_stmt_list.append(increment(lattice_point[0]))
            while_stmt_list.append(increment(lattice_point[1]))

            stmt_list.extend((while_node(while_node_cond, while_stmt_list, op1, op2)))

        elif(len(lattice_point) == 1):

            while_node_cond = [lattice_point[0]]
            while_stmt_list = []
            while_stmt_list.append(index_def(lattice_point[0], op1, op2))
            while_stmt_list.append(logical_def([lattice_point[0]]))
            
            sub_points = []
            sub_points.append([lattice_point[0]])

            conds_list = []
            stmts_list = []
            for point in sub_points:
                conds_list.append(point) 

                if(len(point) == 2):
                    if(len(schedule) == 1):
                        
                        compute_block_stmts = compute_block(op1, op2, dest, tformat, op, level)
                        stmts_list.append(compute_block_stmts)
                    else:
                        new_schedule = schedule[1:]
                        stmts_list.append(make_stmts(new_schedule, op1, op2, op, dest, tformat, level))
                elif(len(point) == 1):
                    if(len(schedule) == 1):
                        if(tformat == 'S'):                
                            add_copy_block_stmts = add_copy_block(point, dest, tformat, op, level)
                            stmts_list.append(add_copy_block_stmts)
                        else:
                            compute_block_stmts = compute_block(op1, op2, dest, tformat, op, level)
                            stmts_list.append(compute_block_stmts)
                    else:
                        new_schedule = schedule[1:]
                        temp_idx = point[0][1]
                        temp_arr = point[0][:-1]

                        new_op1 = op1
                        new_op2 = op2

                        if(temp_arr not in op2):
                            is_present2 = False
                            for arr_read in op2:
                                for idx_arr2 in op2[arr_read]:
                                    if(idx_arr2 == temp_idx):
                                        is_present2 = True

                            if(is_present2):
                                new_op2 = {}

                        if(temp_arr not in op1):
                            is_present1 = False
                            for arr_read in op1:
                                for idx_arr1 in op1[arr_read]:
                                    if(idx_arr1 == temp_idx):
                                        is_present1 = True

                            if(is_present1):
                                new_op1 = {}

                        stmts_list.append(make_stmts(new_schedule, new_op1, new_op2, op, dest, tformat, level))
                    
            while_stmt_list.extend(if_node(conds_list, stmts_list, op1, op2, dest, tformat))
            while_stmt_list.append(increment(lattice_point[0]))
            
            stmt_list.extend((while_node(while_node_cond, while_stmt_list, op1, op2)))

    return stmt_list
  
def unroll_ptrs_cp(dest, op1, op2, tformat, level):

    stmt_list = []
    
    for arr_read in dest:
        dest_read = arr_read
    
    for arr_read in op1:
        op1_read = arr_read
    
    for arr_read in op2:
        op2_read = arr_read

    if(tformat == 'S'):

        dest_arr_dim = len(dest[dest_read])

        if(level == "cp"):
            for i in range(2 * dest_arr_dim):
                stmt_list.append(["int *" + dest_read + str(i + 1) + "_pos" + " = " + "(int*)" + dest_read + "_ptrs[" + str(2 * i) + "];"])
                stmt_list.append(["int *" + dest_read + str(i + 1) + "_crd" + " = " + "(int*)" + dest_read + "_ptrs[" + str(2 * i + 1) + "];"]) 

            stmt_list.append(["double *" + dest_read + "_vals" + " = " + "(double*)" + dest_read + "_ptrs[" + str(4 * dest_arr_dim) + "];"])
        
        elif(level == "ap"):
            for i in range(3 * dest_arr_dim):
                stmt_list.append(["int *" + dest_read + str(i + 1) + "_pos" + " = " + "(int*)" + dest_read + "_ptrs[" + str(2 * i) + "];"])
                stmt_list.append(["int *" + dest_read + str(i + 1) + "_crd" + " = " + "(int*)" + dest_read + "_ptrs[" + str(2 * i + 1) + "];"]) 

            stmt_list.append(["double *" + dest_read + "_vals" + " = " + "(double*)" + dest_read + "_ptrs[" + str(6 * dest_arr_dim) + "];"])

    elif(tformat == 'D'):

        stmt_list.append(["double *" + dest_read + "_vals" + " = " + "(double*)" + dest_read + "_ptrs[" + str(0) + "];"])

    stmt_list.append(["\n"])

    op1_arr_dim = len(op1[op1_read])

    if(level == "cp"):
        for i in range(2 * op1_arr_dim):
            stmt_list.append(["int *" + op1_read + str(i + 1) + "_pos" + " = " + "(int*)" + op1_read + "_ptrs[" + str(2 * i) + "];"])
            stmt_list.append(["int *" + op1_read + str(i + 1) + "_crd" + " = " + "(int*)" + op1_read + "_ptrs[" + str(2 * i + 1) + "];"])

        stmt_list.append(["double *" + op1_read + "_vals" + " = " + "(double*)" + op1_read + "_ptrs[" + str(4 * op1_arr_dim) + "];"])

    elif(level == "ap"):
        for i in range(3 * op1_arr_dim):
            stmt_list.append(["int *" + op1_read + str(i + 1) + "_pos" + " = " + "(int*)" + op1_read + "_ptrs[" + str(2 * i) + "];"])
            stmt_list.append(["int *" + op1_read + str(i + 1) + "_crd" + " = " + "(int*)" + op1_read + "_ptrs[" + str(2 * i + 1) + "];"])

        stmt_list.append(["double *" + op1_read + "_vals" + " = " + "(double*)" + op1_read + "_ptrs[" + str(6 * op1_arr_dim) + "];"])

    stmt_list.append(["\n"])

    op2_arr_dim = len(op2[op2_read])

    if(level == "cp"):

        for i in range(2 * op2_arr_dim):
            stmt_list.append(["int *" + op2_read + str(i + 1) + "_pos" + " = " + "(int*)" + op2_read + "_ptrs[" + str(2 * i) + "];"])
            stmt_list.append(["int *" + op2_read + str(i + 1) + "_crd" + " = " + "(int*)" + op2_read + "_ptrs[" + str(2 * i + 1) + "];"])

        stmt_list.append(["double *" + op2_read + "_vals" + " = " + "(double*)" + op2_read + "_ptrs[" + str(4 * op2_arr_dim) + "];"])

    elif(level == "ap"):
        for i in range(3 * op2_arr_dim):
            stmt_list.append(["int *" + op2_read + str(i + 1) + "_pos" + " = " + "(int*)" + op2_read + "_ptrs[" + str(2 * i) + "];"])
            stmt_list.append(["int *" + op2_read + str(i + 1) + "_crd" + " = " + "(int*)" + op2_read + "_ptrs[" + str(2 * i + 1) + "];"])

        stmt_list.append(["double *" + op2_read + "_vals" + " = " + "(double*)" + op2_read + "_ptrs[" + str(6 * op2_arr_dim) + "];"])

    return stmt_list

def tile_mem_stmts(dest, op1, op2, tformat, level): 

    for arr_read in dest:
        dest_read = arr_read

    for arr_read in op1:
        op1_read = arr_read

    for arr_read in op2:
        op2_read = arr_read


    stmt_list = []
    if(level == "cp"):
        # FIX this properly - No hacking
        stmt_list.append(["\n"])
        stmt_list.append(["int tile_size = TILE_SIZE1 * TILE_SIZE2;"])
    elif(level == "ap"):
        # FIX this properly - No hacking
        stmt_list.append(["\n"])
        stmt_list.append(["int tile_size = BIG_TILE_SIZE1 * BIG_TILE_SIZE2;"])

    stmt_list.append(["\n"])

    if(tformat == 'S'):
        dest_arr_dim = len(dest[dest_read])

        stmt_list.append(['int **tile_' + dest_read + '_ptrs;'])

        if(level == "cp"):

            for i in range(dest_arr_dim):
                stmt_list.append(["int *tile_" + dest_read + "_pos" + str(i + 1) + "_ptr" + ";"])
                stmt_list.append(["int *tile_" + dest_read + "_crd" + str(i + 1) + "_ptr" + ";"])
            
            stmt_list.append(["double *tile_" + dest_read + "_vals" + "_ptr" + ";"])
            stmt_list.append(["\n"])

            for i in range(dest_arr_dim):
                stmt_list.append(["tile_" + dest_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
                stmt_list.append(["tile_" + dest_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

            stmt_list.append(["tile_" + dest_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])
            stmt_list.append(["\n"])

            stmt_list.append(["tile_" + dest_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(2 * dest_arr_dim + 1) + "));"])
            stmt_list.append(["\n"])

            for i in range(dest_arr_dim):
                stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(2 * i) + ") = tile_" + dest_read + "_pos" + str(i + 1) + "_ptr;"])
                stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + dest_read + "_crd" + str(i + 1) + "_ptr;"])

            stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(2 * dest_arr_dim) + ") = (int *) tile_" + dest_read + "_vals" + "_ptr;"])
            stmt_list.append(["\n"])
        
        elif(level == "ap"):

            for i in range(2 * dest_arr_dim):
                stmt_list.append(["int *tile_" + dest_read + "_pos" + str(i + 1) + "_ptr" + ";"])
                stmt_list.append(["int *tile_" + dest_read + "_crd" + str(i + 1) + "_ptr" + ";"])
            
            stmt_list.append(["double *tile_" + dest_read + "_vals" + "_ptr" + ";"])
            stmt_list.append(["\n"])

            for i in range(2 * dest_arr_dim):
                stmt_list.append(["tile_" + dest_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
                stmt_list.append(["tile_" + dest_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

            stmt_list.append(["tile_" + dest_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])
            stmt_list.append(["\n"])

            stmt_list.append(["tile_" + dest_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(4 * dest_arr_dim + 1) + "));"])
            stmt_list.append(["\n"])

            for i in range(2 * dest_arr_dim):
                stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(2 * i) + ") = tile_" + dest_read + "_pos" + str(i + 1) + "_ptr;"])
                stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + dest_read + "_crd" + str(i + 1) + "_ptr;"])

            stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(4 * dest_arr_dim) + ") = (int*) tile_" + dest_read + "_vals" + "_ptr;"])
            stmt_list.append(["\n"])

    else: 
        stmt_list.append(["int **tile_" + dest_read + "_ptrs;"])
        stmt_list.append(["\n"])

        # Memeory allocate statements

        stmt_list.append(["tile_" + dest_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])
        stmt_list.append(["\n"])

        stmt_list.append(["tile_" + dest_read + "_ptrs = (int**)malloc(sizeof(int*) * 1);"])
        stmt_list.append(["\n"])

        stmt_list.append(["*(tile_" + dest_read + "_ptrs + " + str(0) + ") = (int*) tile_" + dest_read + "_vals" + "_ptr;"])
        stmt_list.append(["\n"])

    if(level == "cp"):

        op1_arr_dim = len(op1[op1_read])

        stmt_list.append(["int **tile_" + op1_read + "_ptrs;"])
        stmt_list.append(["\n"])

        for i in range(op1_arr_dim):
            stmt_list.append(["int *tile_" + op1_read + "_pos" + str(i + 1) + "_ptr" + ";"])
            stmt_list.append(["int *tile_" + op1_read + "_crd" + str(i + 1) + "_ptr" + ";"])
            
        stmt_list.append(["double *tile_" + op1_read + "_vals" + "_ptr" + ";"])
        stmt_list.append(["\n"])

        # Memeory allocate statements
        for i in range(op1_arr_dim):
            stmt_list.append(["tile_" + op1_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
            stmt_list.append(["tile_" + op1_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

        stmt_list.append(["tile_" + op1_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])
        stmt_list.append(["\n"])

        stmt_list.append(["tile_" + op1_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(2 * op1_arr_dim + 1) + "));"])
        stmt_list.append(["\n"])

        for i in range(op1_arr_dim):
            stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(2 * i) + ") = tile_" + op1_read + "_pos" + str(i + 1) + "_ptr;"])
            stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + op1_read + "_crd" + str(i + 1) + "_ptr;"])

        stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(2 * op1_arr_dim) + ") = (int*) tile_" + op1_read + "_vals" + "_ptr;"])
        stmt_list.append(["\n"])

        op2_arr_dim = len(op2[op2_read])

        stmt_list.append(["int **tile_" + op2_read + "_ptrs;"])
        stmt_list.append(["\n"])

        for i in range(op2_arr_dim):
            stmt_list.append(["int *tile_" + op2_read + "_pos" + str(i + 1) + "_ptr" + ";"])
            stmt_list.append(["int *tile_" + op2_read + "_crd" + str(i + 1) + "_ptr" + ";"])

        stmt_list.append(["double *tile_" + op2_read + "_vals" + "_ptr" + ";"])

        stmt_list.append(["\n"])

        # Memeory allocate statements
        for i in range(op2_arr_dim):
            stmt_list.append(["tile_" + op2_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
            stmt_list.append(["tile_" + op2_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

        stmt_list.append(["tile_" + op2_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])

        stmt_list.append(["\n"])

        stmt_list.append(["tile_" + op2_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(2 * op2_arr_dim + 1) + "));"])
        stmt_list.append(["\n"])

        for i in range(op2_arr_dim):
            stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(2 * i) + ") = tile_" + op2_read + "_pos" + str(i + 1) + "_ptr;"])
            stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + op2_read + "_crd" + str(i + 1) + "_ptr;"])

        stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(2 * op2_arr_dim) + ") = (int*) tile_" + op2_read + "_vals" + "_ptr;"])
        stmt_list.append(["\n"])
    
    elif(level == "ap"):
        op1_arr_dim = len(op1[op1_read])

        stmt_list.append(["int **tile_" + op1_read + "_ptrs;"])
        stmt_list.append(["\n"])

        for i in range(2 * op1_arr_dim):
            stmt_list.append(["int *tile_" + op1_read + "_pos" + str(i + 1) + "_ptr" + ";"])
            stmt_list.append(["int *tile_" + op1_read + "_crd" + str(i + 1) + "_ptr" + ";"])
            
        stmt_list.append(["double *tile_" + op1_read + "_vals" + "_ptr" + ";"])
        stmt_list.append(["\n"])

        # Memeory allocate statements
        for i in range(2 * op1_arr_dim):
            stmt_list.append(["tile_" + op1_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
            stmt_list.append(["tile_" + op1_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

        stmt_list.append(["tile_" + op1_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])
        stmt_list.append(["\n"])

        stmt_list.append(["tile_" + op1_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(4 * op1_arr_dim + 1) + "));"])
        stmt_list.append(["\n"])

        for i in range(2 * op1_arr_dim):
            stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(2 * i) + ") = tile_" + op1_read + "_pos" + str(i + 1) + "_ptr;"])
            stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + op1_read + "_crd" + str(i + 1) + "_ptr;"])

        stmt_list.append(["*(tile_" + op1_read + "_ptrs + " + str(4 * op1_arr_dim) + ") = (int*) tile_" + op1_read + "_vals" + "_ptr;"])
        stmt_list.append(["\n"])

        op2_arr_dim = len(op2[op2_read])

        stmt_list.append(["int **tile_" + op2_read + "_ptrs;"])
        stmt_list.append(["\n"])

        for i in range(2 * op2_arr_dim):
            stmt_list.append(["int *tile_" + op2_read + "_pos" + str(i + 1) + "_ptr" + ";"])
            stmt_list.append(["int *tile_" + op2_read + "_crd" + str(i + 1) + "_ptr" + ";"])

        stmt_list.append(["double *tile_" + op2_read + "_vals" + "_ptr" + ";"])

        stmt_list.append(["\n"])

        # Memeory allocate statements
        for i in range(2 * op2_arr_dim):
            stmt_list.append(["tile_" + op2_read + "_pos" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])
            stmt_list.append(["tile_" + op2_read + "_crd" + str(i + 1) + "_ptr = (int*)malloc(sizeof(int) * tile_size);"])

        stmt_list.append(["tile_" + op2_read + "_vals" + "_ptr = (double*)malloc(sizeof(double) * tile_size);"])

        stmt_list.append(["\n"])

        stmt_list.append(["tile_" + op2_read + "_ptrs = (int**)malloc(sizeof(int*) * (" + str(4 * op2_arr_dim + 1) + "));"])
        stmt_list.append(["\n"])

        for i in range(2 * op2_arr_dim):
            stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(2 * i) + ") = tile_" + op2_read + "_pos" + str(i + 1) + "_ptr;"])
            stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(2 * i + 1) + ") = tile_" + op2_read + "_crd" + str(i + 1) + "_ptr;"])

        stmt_list.append(["*(tile_" + op2_read + "_ptrs + " + str(4 * op2_arr_dim) + ") = (int*) tile_" + op2_read + "_vals" + "_ptr;"])
        stmt_list.append(["\n"])

    return stmt_list

def dest_idx_def(dest, tformat):
    for arr_read in dest:
        dest_read = arr_read

    dest_arr_dim = len(dest[dest_read])

    stmt_list = []

    stmt_list.append(["int is_nz;"])

    if(tformat == 'S'):
        for i in range(dest_arr_dim):
            stmt_list.append(['int ' + dest[dest_read][i] + dest_read + ' = 0;'])

        for i in range(dest_arr_dim):
            stmt_list.append([dest_read + str(i + 1) + '_pos[0] = 0;'])

        stmt_list.append(["\n"])

    else:
        stmt_list.append(["\n"])

    return stmt_list

def end_stms(dest, tformat): 

    for arr_read in dest:
        dest_read = arr_read

    dest_arr_dim = len(dest[dest_read])

    stmt_list = []

    stmt_list.append(["\n"])

    if(tformat == 'S'):
        stmt_list.append([dest_read + "1" + "_pos[1] = " + dest[dest_read][0] + dest_read + ";"])

    stmt_list.append(["\n"])
    stmt_list.append(["return 0;"]) 

    return stmt_list

def cp_header(dest, op1, op2, TILE_SIZE1, TILE_SIZE2, level): 

        
        for arr_read in dest:
            dest_read = arr_read
    
        for arr_read in op1:
            op1_read = arr_read
    
        for arr_read in op2:
            op2_read = arr_read
    
        stmt_list = []

        if(level == "cp"):
    
            stmt_list.append(["#define TILE_SIZE1 " + str(TILE_SIZE1)])
            stmt_list.append(["#define TILE_SIZE2 " + str(TILE_SIZE2)])
            stmt_list.append(["\n"])
    
            stmt_list.append(["int cp_evaluate(int **" + dest_read + "_ptrs" + ", int **" + op1_read + "_ptrs" + ", int **" + op2_read + "_ptrs" + ") {"])
            stmt_list.append(["\n"])
        
        elif(level == "ap"):

            stmt_list.append(["#define BIG_TILE_SIZE1 " + str(TILE_SIZE1)])
            stmt_list.append(["#define BIG_TILE_SIZE2 " + str(TILE_SIZE2)])
            stmt_list.append(["\n"])
    
            stmt_list.append(["int ap_evaluate(int **" + dest_read + "_ptrs" + ", int **" + op1_read + "_ptrs" + ", int **" + op2_read + "_ptrs" + ") {"])
            stmt_list.append(["\n"])
    
        return stmt_list 

def cp_footer():

    stmt_list = []
    stmt_list.append(["}"])

    return stmt_list

def print_stmts(stmt_list, i):
    for stmt in stmt_list:
        if(len(stmt) > 1):
            print_stmts(stmt, i + 1)
        else:
            print("\t" * i + stmt[0])

if __name__ == '__main__':

    data = file_parser('input.txt')

    [dest, op1, op2, op, schedule, tformat, tsize1, tsize2, stsize1, stsize2] = data_parser(data)

    level = "cp"

    if(level == "cp"):
        cp_header_stmts = cp_header(dest, op1, op2, stsize1, stsize2, level)
    else:
        cp_header_stmts = cp_header(dest, op1, op2, tsize1, tsize2, level)
    cp_unroll_ptrs_list = unroll_ptrs_cp(dest, op1, op2, tformat, level)
    cp_tile_mem_stmts = tile_mem_stmts(dest, op1, op2, tformat, level)
    cp_dest_idx_def = dest_idx_def(dest, tformat)
    cp_stmt_list = make_stmts(schedule, op1, op2, op, dest, tformat, level)
    cp_end_stmts = end_stms(dest, tformat)
    cp_footer_stmts = cp_footer()

    print_stmts(cp_header_stmts, 0)
    print_stmts(cp_unroll_ptrs_list, 1)
    print_stmts(cp_tile_mem_stmts, 1)
    print_stmts(cp_dest_idx_def, 1)
    print_stmts(cp_stmt_list, 1)
    print_stmts(cp_end_stmts, 1)
    print_stmts(cp_footer_stmts, 0)


