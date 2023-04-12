def clean_foldername(lib_path: str, folder: str) -> str:
    _folder = folder.removeprefix(lib_path)
    _folder = remove_leading_slash(remove_trailing_slash(_folder))
    return _folder

def ensure_trailing_slash(path: str) -> str:
    _path = path
    if not _path.endswith('/'):
        _path = _path + '/'
    return _path

def remove_trailing_slash(path: str) -> str:
    _path = path.removesuffix('/')
    return _path

def remove_leading_slash(path: str) -> str:
    _path = path.removeprefix('/')
    return _path
