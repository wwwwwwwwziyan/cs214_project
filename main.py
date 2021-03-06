import utils
import config
import sys
#import src.basic_query as basic_query
import src.process_query as pq

def main(argv):
    query_file = config.query_file
    mode = 'd'
    if len(argv) != 0:
        for i in range(len(argv)):
            if argv[i] == '-f':
                query_file = argv[i+1]
            elif argv[i] == '-s':
                mode = 's'
            elif argv[i] == '-d':
                mode = 'd'
    test_query = utils.read_file(query_file)
    utils.write_log_and_console(config.log_file, 'Test SQL query:')
    utils.write_log_and_console(config.log_file, test_query)
    pass1 = pq.Pass1(test_query)
    pass2 = pq.Pass2(pass1)
    pass3 = pq.Pass3(pass2)
    pass4 = pq.Pass4(pass3, mode)
    #print("\npass1:\n",pass1)
    #print("\npass2:\n",pass2)
    #print("\npass3:\n",pass3)
    #print("\npass4:\n",pass4)
    #output = pq.translate(test_query)

    print('\nOutput PySpark code:')
    print(pass4)
    #utils.write_log_and_console(config.log_file, '\nOutput PySpark code:')
    #utils.write_log_and_console(config.log_file, output)
    #utils.write_output(config.out_file, output)

    #utils.write_log_and_console('test_log.txt',output)

    
    return


if __name__ == '__main__':
    main(sys.argv)
