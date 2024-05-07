class Operation(object):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return self.__str__()


def get_stmt(stmt, id_dict):

    lower_stmts = []

    if not isinstance(stmt.left, str) and not isinstance(stmt.right, str):
        left = get_stmt(stmt.left, id_dict)
        right = get_stmt(stmt.right, id_dict)
        if(stmt.op == '+'):
            lower_stmts = "(" + left + "+" + right + ")"
            return lower_stmts
        if(stmt.op == '*'):
            lower_stmts = "(" + left + "*" + right + ")"
            return lower_stmts

    elif not isinstance(stmt.left, str):

        left = get_stmt(stmt.left, id_dict)
        if(id_dict[stmt.right] == ['-']):
            right = "0"
        else:
            right = stmt.right + "_vals[" + id_dict[stmt.right][-1] + stmt.right + "]"  
        if(stmt.op == '+'):
            lower_stmts = "(" + left + " + " + right + ")"
            return lower_stmts
        if(stmt.op == '*'):  
            lower_stmts = "(" + left + " * " + right + ")"
            return lower_stmts

    elif not isinstance(stmt.right, str):
        right = get_stmt(stmt.right, id_dict)
        if(id_dict[stmt.left] == ['-']):
            left = "0"
        else:
            left =  stmt.left + "_vals[" + id_dict[stmt.left][-1] + stmt.left + "]"
        if(stmt.op == '+'):
            lower_stmts = "(" + left + " + " + right + ")"
            return lower_stmts
        if(stmt.op == '*'):
            lower_stmts = "(" + left + " * " + right + ")"
            return lower_stmts

    else:
        if(id_dict[stmt.left] == ['-']):
            left = "0"
        else:
            left = stmt.left + "_vals[" + id_dict[stmt.left][-1] + stmt.left + "]"

        if(id_dict[stmt.right] == ['-']):
            right = "0"
        else:
            right = stmt.right + "_vals[" + id_dict[stmt.right][-1] + stmt.right + "]"

        if(stmt.op == '+'):
            lower_stmts = "(" + left + " + " + right + ")"
            return lower_stmts

        if(stmt.op == '*'):
            lower_stmts = "(" + left + " * " + right + ")"
            return lower_stmts

if __name__ == "__main__":

    expr = "((A + B) * C)"

    stack = []
    for c in expr:
        if c == ' ':
            continue
        if c == ')':
            right = stack.pop()
            op = stack.pop()
            left = stack.pop()
            stack.pop()
            stack.append(Operation(op, left, right))
        else:
            stack.append(c)

    stmt = stack[0]

    id_dict = {}
    id_dict['A'] = ['-']
    id_dict['B'] = ['i', 'j']
    id_dict['C'] = ['i', 'j']

    print(get_stmt(stmt, id_dict))