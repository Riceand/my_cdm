import os

def is_windows():
  return os.name == 'nt'

def exist_path(path_name):
  return os.path.exists(path_name)

def mkdir(path_name):
  if exist_path(path_name):
    return False
  os.mkdir(path_name, 0o755)
  return True

def mkdirs(path_name):
  if exist_path(path_name):
    return False
  os.makedirs(path_name, 0o755)
  return True

def rmdir(path_name):
  return os.rmdir(path_name)

def rmdirs(path_name):
  return os.removedirs(path_name)