# assimp.py - a custom loader for pyassimp.
# The provided loader is a pain.

import os

oldpath = os.environ["PATH"]
os.environ["PATH"] = ".\\dll"
import pyassimp as assimp
os.environ["PATH"] = oldpath

__all__ = ["assimp"]
