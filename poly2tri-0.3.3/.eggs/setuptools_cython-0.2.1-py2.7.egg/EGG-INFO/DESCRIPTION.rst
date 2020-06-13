Allows compiling Cython extensions in setuptools
by putting setuptools_cython in your setup_requires.

Usage
=====

Use setuptools, add setuptools_cython to your setup_requires.

Some verbatim code is required to make Extension behave as expected.

Usage example
=============

setup.py::

    #!/usr/bin/env python

    from setuptools import setup
    from distutils.extension import Extension

    # setuptools DWIM monkey-patch madness
    # http://mail.python.org/pipermail/distutils-sig/2007-September/thread.html#8204
    import sys
    if 'setuptools.extension' in sys.modules:
        m = sys.modules['setuptools.extension']
        m.Extension.__dict__ = m._Extension.__dict__

    setup(
            name = "example",
            version = "0.1",
            description="setuptools_cython example",
            setup_requires=[
                'setuptools_cython',
                ],
            ext_modules=[
                Extension('example', ['example.pyx']),
                ],
            )



