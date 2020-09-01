# Internal modules
from input_parser.ParamsParser import ParamsParser 

def main():
    params = ParamsParser()
    print(params.key)

    # For the 2nd step, create new timestamped directory into which raw map will
    # be loaded.
    # Then, PIL will take care of it in the second step.
    # To make sure, test for and create new outputs dir everytime this is run.

if __name__ == '__main__':
    main()
