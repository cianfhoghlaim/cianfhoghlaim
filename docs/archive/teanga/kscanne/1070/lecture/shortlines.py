# shortlines.py
import sys

if __name__ == "__main__":

    # sys.argv is the list of command-line arguments
    # sys.argv[0] is the name of the program itself
    # sys.argv[1] will be the cutoff length
    cutoff = int(sys.argv[1])

    # for every line passed into the script
    for line in sys.stdin:
        if len(line) < cutoff:
            sys.stdout.write(line)
