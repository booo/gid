import sys
from os import path

_srcPath = path.join(path.dirname(path.abspath(__file__)), '..', 'src')
sys.path.insert(0, _srcPath)
