import os


def recursive_chmod(path, mode_files, mode_dirs):
    """Recursively change folder and file permissions

    mode_files/mode dirs can be given in octal notation e.g. 0o777
    flags from the stats module.

    Reference: https://docs.python.org/3/library/os.html#os.chmod"""
    # os.walk will loop through all dirs in dirpath (including top-level dir)
    # filenames are just that: list of filenames for each dir
    for dirpath, _, filenames in os.walk(path):
        os.chmod(dirpath, mode_dirs)
        for filename in filenames:
            os.chmod(os.path.join(dirpath, filename), mode_files)
