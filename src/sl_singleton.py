"""
Slang
Copyright: Andridov and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]