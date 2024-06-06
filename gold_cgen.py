def einsum_expr(sub_stmt, op_list, op_dict, dest_dict):

    sub_op_list = []
    for char in sub_stmt: 
        if(char in op_list):
            sub_op_list.append(char)

    if(len(sub_op_list) > 1):
        stmt = []
        stmt.extend("np.einsum('")

        for char in sub_op_list:
            stmt.extend("".join(op_dict[char]))
            stmt.extend(",")
        stmt = stmt[:-1]

        

        dest_keys = list(dest_dict.keys())
        dest_list = dest_dict[dest_keys[0]]

        if(dest_list != ['0']):
            stmt.extend("->")
            stmt.extend("".join(dest_list))

        stmt.extend("'")
        stmt.extend(",")

        for char in sub_op_list:
            stmt.extend(char)
            stmt.extend(",")

        stmt = stmt[:-1]
        stmt.extend(")")
        stmt = "".join(stmt)
    else:
        stmt = sub_op_list[0]

    return stmt


def dense(expr, op_list, op_dict, dest_dict, output_dir_path):
    
    stmt = []
    stmt.append("import numpy as np")
    stmt.append("\n")

    for op in op_list:
        stmt.append("\n")
        stmt.append(op + " = np.load(\"" + output_dir_path + "tensor_" + op + "/numpy_array.npz\")['array1']")

    stmt.append("\n")
    stmt.append("\n")

    if("+" in expr):
        sub_stmts = expr.split("+")
    else:
        sub_stmts = [expr]

    sub_stmt1 = sub_stmts[0]

    np_einsum_expr = einsum_expr(sub_stmt1, op_list, op_dict, dest_dict)
    stmt.append("out = " + np_einsum_expr)

    for sub_stmt in sub_stmts[1:]:
        stmt.append("\n")
        stmt.append("temp = " + einsum_expr(sub_stmt, op_list, op_dict, dest_dict))
        stmt.append("\n")
        stmt.append("out = np.add(out, temp)")  
        
    stmt.append("\n")
    stmt.append("\n")

    stmt.append("out = out.reshape(-1)") 
    stmt.append("\n")
    stmt.append("out_path = \"" + output_dir_path + "gold_output.npz\"")
    stmt.append("\n")
    stmt.append("np.savez(out_path, array1 = out)")
    stmt.append("\n")

    return stmt


if __name__ == "__main__":
    expr = "B * C * D"
    op_list = ["B", "C", "D"]
    op_dict = {"B": ['i', 'k'], "C": ['k', 'j'], "D": ['i', 'j']}
    dest_dict = {"A": ['i', 'j']}

    stmt = dense(expr, op_list, op_dict, dest_dict, "lego_scratch/")

    print("".join(stmt))