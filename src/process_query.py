import re

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

    def update(self, val):
        self.val = val

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
    
    def update(self, idx, val):
        self.vals[idx] = val

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
    tokens = re.findall(r"[-\w']+|[*.,)(=<>]", query)
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
    return stack[0]

def Pass2(x):
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


def Pass3(x):
    tag_idx = 0
    flatten = {}
    def tag():
        nonlocal tag_idx
        tag_idx += 1
        return 'tmp_' + str(tag_idx)
    
    def func(struc):
        nonlocal flatten
        if isinstance(struc, list) and isinstance(struc[0], sel):
            ls = []
            for sub_struc in struc:
                sub_struc = func(sub_struc)
                ls.append(sub_struc)
            new_tag = tag()
            flatten[new_tag] = ls
            return new_tag
        elif isinstance(struc, stmt):
            for idx, val in enumerate(struc.vals):
                struc.update(idx, func(val))
            return struc
        elif isinstance(struc, als):
            struc.update(func(struc.val))
            return struc
        else:
            return struc
    func(x)
    return flatten
