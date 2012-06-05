from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os
import numpy as np

include_dirs = [np.get_include()]

extensions = [
    Extension("hashvtable", ["hashvtable.pyx", "hashvtable_c_code.c"],
              include_dirs=include_dirs,
              libraries=['rt'])
    ]

setup(cmdclass={'build_ext': build_ext},
      ext_modules=extensions)
