if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from aims.command_line import CommandLine
    else:
        from ..aims.command_line import CommandLine

data = CommandLine().execute("dkjfakl")

print(data)
