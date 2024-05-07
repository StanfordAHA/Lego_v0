"""
Inputs: 
- Expression in CIN format. Ex: ((A + B) + C), Parantheses are mandatory. 
- id_dict: Dictionary containing the id's of the variables in the expression.
- id: The id of the variable for which the lattice is to be computed.
"""

class Operation(object):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return self.__str__()

def merge_intersect(lattice1, lattice2):
    lattice = []

    if(len(lattice1) == 0):
        return lattice2
    
    elif(len(lattice2) == 0):
        return lattice1
    
    else: 
        for point1 in lattice1:
            for point2 in lattice2:    
                if(point1 != [] and point2 != []):  
                    lattice.append(point2 + point1)

    return lattice

def merge_union(lattice1, lattice2):
    lattice = []


    for point1 in lattice1:
        if point1 != []:
            lattice.append(point1)
    
    for point2 in lattice2:
        if point2 != []:
            lattice.append(point2)

    if(lattice1 != [] and lattice2 != []):
        lattice.extend(merge_intersect(lattice1, lattice2))

    return lattice

def ispresent(stmt, id_dict, id):
    for i in id_dict[stmt]:
        if i == id:
            return True

def sort_lattice(lattice):
    return sorted(lattice, key=lambda i: len(i), reverse=True)

def get_lattice(stmt, id_dict, id):

    lattice = []

    if not isinstance(stmt.left, str) and not isinstance(stmt.right, str):
        left = get_lattice(stmt.left, id_dict, id)
        right = get_lattice(stmt.right, id_dict, id)
        if(stmt.op == '+'):
            lattice = merge_union(left, right)
            return sort_lattice(lattice)
        if(stmt.op == '*'):
            lattice = merge_intersect(left, right)
            return sort_lattice(lattice)

    elif not isinstance(stmt.left, str):
        left = get_lattice(stmt.left, id_dict, id)
        if(ispresent(stmt.right, id_dict, id)):
            right = [[id + stmt.right]]
        else:
            right = []
        if(stmt.op == '+'):
            lattice = merge_union(left, right)
            return sort_lattice(lattice)
        if(stmt.op == '*'):  
            lattice = merge_intersect(left, right)
            return sort_lattice(lattice)

    elif not isinstance(stmt.right, str):
        right = get_lattice(stmt.right, id_dict, id)
        if(ispresent(stmt.left, id_dict, id)):
            left = [[id + stmt.left]]
        else:
            left =  []
        if(stmt.op == '+'):
            lattice = merge_union(left, right)
            return sort_lattice(lattice)
        if(stmt.op == '*'):
            lattice = merge_intersect(left, right)
            return sort_lattice(lattice)

    else:
        if(ispresent(stmt.left, id_dict, id)):
            left = [[id + stmt.left]]
        else:
            left = []
        if(ispresent(stmt.right, id_dict, id)):
            right = [[id + stmt.right]]
        else:
            right = []
        if(stmt.op == '+'):
            lattice = merge_union(left, right)
            return sort_lattice(lattice)
        if(stmt.op == '*'):
            lattice = merge_intersect(left, right)
            return sort_lattice(lattice)
   
def expr_to_lattice(expr, id_dict, id):
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

    lattice = get_lattice(stmt, id_dict, id)
    return lattice

"""
Test pattern
"""

if __name__ == '__main__':
    expr = "(B + C)"

    id_dict = {}

    id_dict['B'] = ['i', 'k']
    id_dict['C'] = ['k', 'j']
    
    lattice = expr_to_lattice(expr, id_dict, 'i')
    print(lattice)