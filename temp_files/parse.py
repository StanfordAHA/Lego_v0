from pyparsing import Word, alphas, one_of, alphanums

def file_parser(input_file):
    with open(input_file, 'r') as f:
        data = f.read().splitlines()
    return data

def data_parser(data):

    data = [i for i in data]
    data = [i.replace(" ", "") for i in data]

    arith_op = one_of("+ - * /")

    num_op_rule = Word(alphas) + ":" + Word(alphanums)
    num_op = num_op_rule.parseString(data[0])[2]

    if(num_op == '2'):
        expr_rule = Word(alphas) + ":" + Word(alphas) + '(' + Word(alphas) + ')' +  '=' + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')' 

        expr = expr_rule.parseString(data[1])
        dest = {}
        dest[expr[2]] = list(expr[4])

        op_list =  []
        op_list.append(list(expr[7]))
        op_list.append(list(expr[11]))
        op_list.append(list(expr[12]))

        op = {}
        op[expr[7]] = list(expr[9])
        op[expr[12]] = list(expr[14])
    else:
        expr_rule = Word(alphas) + ":" + Word(alphas) + '(' + Word(alphas) + ')' +  '=' + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')' + \
            arith_op + \
            Word(alphas) + '(' + Word(alphas) + ')'

        expr = expr_rule.parseString(data[1])
        dest = {}
        dest[expr[2]] = list(expr[4])

        op_list = []
        op_list.append(list(expr[7]))
        op_list.append(list(expr[11]))
        op_list.append(list(expr[12]))
        op_list.append(list(expr[16]))
        op_list.append(list(expr[17]))

        op = {}
        op[expr[7]] = list(expr[9])
        op[expr[12]] = list(expr[14])
        op[expr[17]] = list(expr[19])
        

    schedule_rule = Word(alphanums) + "_" + Word(alphanums) + ':' + '[' + Word(alphas) + ']'

    schedule_1 = list((schedule_rule.parseString(data[2]))[5])
    schedule_2 = list((schedule_rule.parseString(data[3]))[5])
    schedule_3 = list((schedule_rule.parseString(data[4]))[5])

    num_ids = len(schedule_1)

    split_factor_rule = Word(alphas) + ':' + "["
        
    for i in range(num_ids):
        split_factor_rule += "[" + Word(alphanums) + "," + Word(alphanums) + "]"
        
    split_factor_rule += "]"

    schedule_split_rule = Word(alpha) + ":" + "[" + Word(alphas) + "]"
    schedule_split = list(schedule_split_rule.parseString(data[6])[3])

    split_factor = {}

    for i in range(num_ids):
        split_factor[schedule_split[i]] = [split_factor_rule.parseString(data[5])[4 + 5 * i]]
        split_factor[schedule_split[i]].append(split_factor_rule.parseString(data[5])[6 + 5 * i])

    
    return num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor

def parse(input_file, level):

    data = file_parser(input_file)
    num_op, dest, op, op_list, schedule_1, schedule_2, schedule_3, split_factor = data_parser(data)

    if(level == "ap"): 
        schedule = schedule_1
    elif(level == "cp"):
        schedule = schedule_2
    else:
        schedule = schedule_3

    dest_id = {}
    dest_map = {}

    source_id = {}
    source_map = {}

    for tensor in op:
        source_id[tensor] = []
        source_map[tensor] = []

    for tensor in dest:
        dest_id[tensor] = []
        dest_map[tensor] = []

    for tensor in op:
        for id in schedule: 
            if id in op[tensor]:
                source_id[tensor].append(id)
                source_map[tensor].append(op[tensor].index(id)) 

    for tensor in dest:
        for id in schedule:
            if id in dest[tensor]:
                dest_id[tensor].append(id)
                dest_map[tensor].append(dest[tensor].index(id))

    if(num_op == "3"):
        expr = "((" + op_list[0][0] + " " + op_list[1][0] + " " + op_list[2][0] + ") " + op_list[3][0] + " " + op_list[4][0] + ")"
    elif(num_op == "2"): 
        expr = "(" + op_list[0][0] + " " + op_list[1][0] + " " + op_list[2][0] + ")"

    return dest_id, dest_map, source_id, source_map, expr, split_factor

if __name__ == "__main__":
    input_file = "program.txt"
    level = "ap"
    dest_id, dest_map, source_id, source_map, expr, split_factor = parse(input_file, level)
