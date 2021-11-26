def translate(query):
    parse = parsing(query)
    return parse

'''
reorder SELECT, FROM ... by the order of 
FROM > WHERE > GROUP BY > AGG > HAVING > SELECT
Input: a SQL query, str
Output: components, List of tuples
    components[i][0]: one of ('from', 'where', 'group', 'agg', 'having', 'select')
    components[i][1]: details of the components, List
'''
def parsing(query):
    precedence = {'from': 1, 'where': 2, 'group': 3, 'agg': 4, 'having': 5, 'select': 6}
    words = query.split()
    
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
    
    return components

'''
Translate each components to Pyspark codes
Input: components, List of tuples
    components[i][0]: one of ('from', 'where', 'group', 'agg', 'having', 'select')
    components[i][1]: details of the components, List

Output: PySpark code, str
'''
def translate_components(parsed_query):
    ret = ''
    for component in parsed_query:
        if component[0] == 'from':
            continue
        elif component[0] == 'where':
            continue
        elif component[0] == 'group':
            continue
        elif component[0] == 'agg':
            continue
        elif component[0] == 'having':
            continue
        elif component[0] == 'select':
            continue
