# vim: set fileencoding=utf-8 sw=4 ts=4 et :

# Parts of Cython are unusable if setuptools just built it.
import sys
if 'Cython' in sys.modules:
    del sys.modules['Cython']

import Cython.Distutils.build_ext

def ext_modules_hack(dist, attr, value):
    dist.cmdclass['build_ext'] = Cython.Distutils.build_ext

def validate_cython_ext_modules(dist, attr, value):
    build_cython(dist).check_extensions_list(value)
    build_cls = dist.get_command_class('build')
    sc = dict(build_cls.sub_commands)
    if 'build_cython' not in sc:
        sc['build_cython'] = None
        build_cls.sub_commands = sc.items()

class build_cython(Cython.Distutils.build_ext, object):
    def finalize_options(self):
        super(build_cython, self).finalize_options()
        self.extensions = self.distribution.cython_ext_modules

