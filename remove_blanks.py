import sys
with open("contacts.csv") as f:
    for line in f:
        if not line.isspace():
            sys.stdout.write(line)