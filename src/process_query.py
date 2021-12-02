import re
#from typing import List

class struc:
    def __str__(self):
        strs = [str(y) for x, y in vars(self).items()]
        return self.__class__.__name__ + '(' + ','.join(strs) + ')'
    __repr__ = __str__

class ref(struc):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
    
    def process(self):
        return str(self.obj) + '.' + str(self.attr)


class als(struc):
    def __init__(self, val, alias):
        self.val = val
        self.alias = alias

    def update(self, val):
        self.val = val
    
    def process(self):
        if isinstance(self.val, ref):
            return '"' + str(self.val.process()) + '".alias(' + str(self.alias) + ')'
        else:
            return str(self.val) + '.alias(' + str(self.alias) + ')'

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

class frm(stmt):
    priority = 1

    def process(self):
        ret = ''
        if isinstance(self.vals[0], als) or isinstance(self.vals[0], ref):
            ret += self.vals[0].process()
        else:
            ret += self.vals[0]
        i = 0
        states = set(['inner','outer','left','right'])
        join_state = 'INNER'
        join_flag = 0
        join_obj = ''
        on_flag = 0
        cond = []
        for item in self.vals:
            if isinstance(item, als) or isinstance(item, ref):
                item2 = item.process()
            else:
                item2 = item
            
            if item2.lower() in states:
                join_state = item2.lower()
            elif item2 == 'JOIN':
                if join_flag:
                    ret += '.join(' +join_obj + ', "' + ' '.join(cond) + '", "' +join_state + '")'
                join_flag = 1
                on_flag = 0
                cond = []
            elif item2 == 'ON':
                on_flag = 1
            elif on_flag:
                cond.append(item2)
            else:
                join_obj = item2
                #print(join_obj)
            i += 1
        
        if join_flag:
            ret += '.join(' +join_obj + ', ' + ' '.join(cond) + ', ' + join_state + ')'

        return ret

class whr(stmt):
    priority = 2

    def process(self):
        ret = '.filter('
        for item in self.vals:
            if isinstance(item, ref) or isinstance(item, als):
                ret += item.process()
            elif isinstance(item, list):
                ret += '(' + ' '.join(item) + ')'
            else:
                ret += item + ' '
        ret += ')'
        return ret

class grp(stmt):
    priority = 3

    def process(self):
        ret = '.groupBy("'
        for item in self.vals:
            if isinstance(item, ref) or isinstance(item, als):
                ret += item.process() + ' '
            else:
                ret += item + ' '
        ret += '")'
        return ret

class agg2(stmt):
    priority = 4

    def process(self):
        ret = '.agg('
        for item in self.vals:
            if isinstance(item, agg):
                item = als(item, str(item.typ) + '_' + str(item.val))

            if isinstance(item, als):
                if isinstance(item.val, agg):
                    ret += '{}("{}").alias({})'.format(item.val.typ, item.val.val, item.val)
            elif isinstance(item, agg):
                ret += '{}("{}").alias({})'.format(item.val.typ, item.val.val, item.val)
        ret += ')'
        if ret == '.agg()':
            #nothing to aggregate
            ret = '' 
        return ret

class hav(stmt):
    priority = 5

    def process(self):
        ret = '.filter("'
        for item in self.vals:
            if isinstance(item, ref) or isinstance(item, als):
                ret += item.process()
            elif isinstance(item, list):
                ret += '(' + ' '.join(item) + ')'
            else:
                ret += item + ' '
        ret += '")'
        return ret

class sel(stmt):
    priority = 6

    def process(self):
        ret = '.select('
        for item in self.vals:
            if isinstance(item, agg):
                item = als(item, str(item.typ) + '_' + str(item.val))

            if isinstance(item, als):
                if isinstance(item.val, agg):
                    ret += '"{}", '.format(item.alias)
                else:
                    ret += '{}, '.format(item.process())
            elif isinstance(item, ref):
                ret += '"{}", '.format(item.process())
            else:
                ret += '"{}", '.format(item)
        ret = ret[:-2]
        ret += ')'
        return ret

class ord(stmt):
    priority = 7

    def process(self):
        ret = '.orderBy('
        ord_item = []
        ascending = []
        for item in self.vals[1:]:
            if item != 'asc' or item != 'desc':
                ord_item.append(item)
                if len(ord_item) > len(ascending):
                    ascending.append('asc')
            else:
                ascending.append(item)
        
        if len(ord_item) > len(ascending):
            ascending.append(1)

        for i in range(len(ord_item)):
            ret += ascending[i] + '("' +  +'"), '
        
        ret = ret[:-2]
        return ret
                

class lmt(stmt):
    priority = 8

    def process(self):
        return '.limit(' + self.vals[0] + ')'

agg_func = set(['max','min','count','avg'])

stmt_dict = {'select':sel, 'from':frm, 'where':whr, 'group':grp, 'having':hav, 'order':ord, 'limit':lmt}
stmt_dict2 = {sel: 'select', frm: 'from', whr: 'where', grp:'group', hav:'having', ord: 'order', lmt: 'limit'}

stmt_set = set(stmt_dict.keys())

boolean = ['and', 'or', 'not']

others = ['by', 'as', 'in']

def keyword_lower(token):
    lower = token.lower()
    if lower in agg_func.union(stmt_set, boolean, others):
        return lower
    return token


def Pass1(query):
    tokens = re.findall(r"[-\w']+|[*.,)(=<>]", query)
    tokens = [keyword_lower(tok) for tok in tokens]
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
    elif x == 'order':
        ret = ord()
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

def Pass4(query_dict, mode):
    ret = ''
    change_var = {}
    #process alias of subquery
    for var in query_dict:
        for i in range(len(query_dict[var])):
            for j in range(len(query_dict[var][i].vals)):
                item = query_dict[var][i].vals[j]
                if isinstance(item, als) and isinstance(item.val, list) and item.val[:4] == 'tmp_':
                    change_var[item.val] = item.alias
                    query_dict[var][i].vals[j] = item.alias

    if mode == 'd':
        for var in query_dict:
            if var in change_var:
                ret += change_var[var] + '='
            else:
                ret += var + '='

            # process each statement
            agg_stmt = agg2()
            agg_stmt.add(query_dict[var])
            query_dict[var].append(agg_stmt)
            query_dict[var].sort(key=lambda x: x.priority)

            for stmt in query_dict[var]:
                ret += stmt.process()
            
            ret += '\n'

    elif mode == 's':
        for var in query_dict:
            if var in change_var:
                ret += change_var[var] + '='
            else:
                ret += var + '='

            ret += 'spark.sql("'
            for stmt in query_dict[var]:
                ret += stmt_dict2[type(stmt)] + ' '
                if isinstance(stmt, grp) or isinstance(stmt, ord):
                    stmt.vals = stmt.vals[1:]

                if isinstance(stmt, sel) or isinstance(stmt, grp) or isinstance(stmt, ord):
                    for word in stmt.vals:
                        if isinstance(word, ref):
                            ret += word.process()
                        elif isinstance(word, als):
                            if isinstance(word.val, ref):
                                word.val = word.process()
                            elif isinstance(word.val, agg):
                                word.val = word.val.typ + '(' + word.val.val + ')'
                            ret += word.val + ' as ' + word.alias
                        elif isinstance(word, agg):
                            ret += word.typ + '(' + word.val + ')'
                        elif isinstance(word, list):
                            ret += '('+' '.join(word)+')'
                        else:
                            ret += word
                        ret += ', '
                
                    ret = ret[:-2] + ' '
                
                else:
                    for word in stmt.vals:
                        if isinstance(word, ref):
                            ret += word.process()
                        elif isinstance(word, als):
                            if isinstance(word.val, ref):
                                word.val = word.process()
                            elif isinstance(word.val, agg):
                                word.val = word.val.typ + '(' + word.val.val + ')'
                            ret += word.val + ' as ' + word.alias
                        elif isinstance(word, agg):
                            ret += word.typ + '(' + word.val + ')'
                        elif isinstance(word, list):
                            ret += '('+' '.join(word)+')'
                        else:
                            ret += word
                        ret += ' '
            ret += '")\n'
            

    return ret

def translate(query, mode):
    pass1 = Pass1(query)
    pass2 = Pass2(pass1)
    pass3 = Pass3(pass2)
    pass4 = Pass4(pass3, mode)
    return pass4