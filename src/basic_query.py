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
def parsing(query):
    precedence = {'from': 1, 'where': 2, 'group': 3, 'agg': 4, 'having': 5, 'select': 6, 'order': 7, 'limit': 8}
    #split words and punctuation
    words = re.findall(r"[-\w']+|[,)(=<>]", query)

    components = []
    curr = []
    for word in words:
        if word in precedence:
            if len(curr) != 0:
                components.append((curr[0], curr))
                if curr[0] == 'select': #agg is also contained in select
                    components.append(('agg', curr))
            curr = []
        curr.append(word)

    components.append((curr[0], curr))
    components.sort(key=lambda x: precedence[x[0]])
    
    #print(components)
    return components

'''
Translate each components to Pyspark codes
Input: components, List of tuples
    components[i][0]: one of ('from', 'where', 'group', 'agg', 'having', 'select')
    components[i][1]: details of the components, List

Output: PySpark code, str
'''
def translate_components(parsed_query):
    agg_func = set(['max','min','count','avg'])

    ret = ''
    for component in parsed_query:
        if component[0] == 'from':
            ret += component[1][1]
        elif component[0] == 'where':
            ret += '.filter("' + ' '.join(component[1][1:]) + '")'
        elif component[0] == 'group':
            ret += '.groupBy("' + ' '.join(component[1][2:]) + '")'
        elif component[0] == 'agg':
            to_add = '.agg('
            add_flag = 0
            i = 1
            while i < len(component[1]):
                curr_word = component[1][i]
                if curr_word in agg_func:
                    add_flag = 1
                    to_add += curr_word + '(col(' + component[1][i+2] + '))' + '.alias("' + component[1][i+5] +'"),'
                    i += 5
                i += 1

            to_add = to_add[:-1]
            print()
            to_add += ')'
            if add_flag == 1:
                ret += to_add
        elif component[0] == 'having':
            ret += '.filter("' + ' '.join(component[1][1:]) + '")'
        elif component[0] == 'select':
            agg_flag = 0
            ret += '.select('
            i = 1
            while i < len(component[1]):
                curr_word = component[1][i]
                
                if curr_word in agg_func:
                    agg_flag = 1
                    i += 1

                elif curr_word == 'as':
                    if agg_flag:
                        agg_flag = 0
                        i += 1
                    else:
                        ret += '.alias("{}"), '.format(component[1][i+1])
                        i += 2
                elif curr_word == ',':
                    ret += ', '
                    i += 1
                elif curr_word != '(' and curr_word != ')':
                    if agg_flag == 0:
                        ret += '"{}"'.format(curr_word)
                    i += 1
                else:
                    i += 1

            ret += ')'
        elif component[0] == 'order':
            # need to be implemented
            continue
        elif component[0] == 'limit':
            ret += '.limit(' + component[1][1] + ')'

    return ret