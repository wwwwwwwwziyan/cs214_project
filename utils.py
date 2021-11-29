def read_file(filename):
    ret = ''
    with open(filename, 'r') as f:
        for line in f.readlines():
            ret += line
    ret.replace('\n',' ')

    return ret

def write_output(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def write_log_and_console(filename, content):
    print(content)
    with open(filename, 'w+') as f:
        f.write(content)
