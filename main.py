import utils
import config
import src.basic_query as basic_query

def main():
    test_query = utils.read_file(config.query_file)
    utils.write_log_and_console(config.log_file, 'Test SQL query:')
    utils.write_log_and_console(config.log_file, test_query)
    output = basic_query.translate(test_query)
    #utils.write_log_and_console(config.log_file, '\nOutput PySpark code:')
    #utils.write_log_and_console(config.log_file, output)
    #utils.write_output(config.out_file, output)

    #utils.write_log_and_console('test_log.txt',output)

    
    return


if __name__ == '__main__':
    main()