import re

'''
Translate a SQL query (without subquery and join) into Pyspark code
Input: SQL query, str
Output: Pyspark code, str
'''
def translate(query):
    parse = parsing(query)
    full_code = translate_components(parse)
    return full_code

'''
reorder SELECT, FROM ... by the order of 
FROM > WHERE > GROUP BY > AGG > HAVING > SELECT
Input: a SQL query, str
Output: components, List of tuples
    components[i][0]: one of ('from', 'where', 'group', 'agg', 'having', 'select', 'order', 'limit')
    components[i][1]: details of the components, List
'''

class struc:
    def __str__(self):
        strs = [str(y) for x, y in vars(self).items()]
        return self.__class__.__name__ + '(' + ','.join(strs) + ')'
    __repr__ = __str__

class ref(struc):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr


class als(struc):
    def __init__(self, val, alias):
        self.val = val
        self.alias = alias


class agg(struc):
    def __init__(self, typ):
        self.typ = typ

    def set_obj(self, val):
        self.val = val


class stmt(struc):
    def __init__(self):
        self.vals = []

    def add(self, val):
        self.vals.append(val)

class sel(stmt):
    pass

class frm(stmt):
    pass

class whr(stmt):
    pass

class hav(stmt):
    pass

class grp(stmt):
    pass

class lmt(stmt):
    pass

agg_func = set(['max','min','count','avg'])

def Pass1(query):
    tokens = re.findall(r"[-\w']+|[.,)(=<>]", query)
    stack = [[]]
    for tok in tokens:
        if tok == '(':
            stack.append([])
        elif tok == ')':
            body = stack.pop()
            if isinstance(stack[-1][-1], agg):
                stack[-1][-1].set_obj(body[0])
            else:
                stack[-1].append(body)
        elif tok in agg_func:
            stack[-1].append(agg(tok))
        elif stack[-1] and stack[-1][-1] == '.':
                stack[-1].pop()
                obj = stack[-1].pop()
                stack[-1].append(ref(obj, tok))
        elif stack[-1] and stack[-1][-1] == 'as':
                stack[-1].pop()
                val = stack[-1].pop()
                stack[-1].append(als(val, tok))
        elif tok == ',':
            pass
        else:
            stack[-1].append(tok)
    print(stack[0])
    return stack[0]

def Pass2(x):
    print(x)
    if isinstance(x, list):
        xs = x
        stack = []
        for x in xs:
            x = Pass2(x)
            if isinstance(x, stmt):
                stack.append(x)
            elif stack and isinstance(stack[-1], stmt):
                stack[-1].add(x)
            else:
                stack.append(x)
        ret = stack
    elif isinstance(x, als):
        x.val = Pass2(x.val)
        ret = x
    elif x == 'select':
        ret = sel()
    elif x == 'from':
        ret = frm()
    elif x == 'where':
        ret = whr()
    elif x == 'having':
        ret = hav()
    elif x == 'group':
        ret = grp()
    elif x == 'limit':
        ret = lmt()
    else:
        ret = x
    return ret
