#!/usr/bin/env python

from setuptools import Extension, setup


class StdoutExtension(Extension):
    """StdoutExtension: A distutils.Extension class customized for
    Boodler driver extensions.
    """

    def __init__(self, **opts):
        modname = 'boodle.cboodle_stdout'

        ls = ['audev-stdout', 'cboodle-stdout', 'noteq', 'sample']
        ls = [('src/cboodle/' + val + '.c') for val in ls]

        super().__init__(modname, ls, **opts)


with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='boodler-redux',
    version='3.0.0',
    description='A programmable soundscape tool',
    author='Beau Gunderson',
    author_email='beau@beaugunderson.com',
    url='https://github.com/beaugunderson/boodler-redux',
    license='GNU LGPL',
    platforms=['MacOS X', 'POSIX'],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio :: Mixers',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        ('License :: OSI Approved :: GNU Library or '
         'Lesser General Public License (LGPL)'),
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'packaging',
    ],
    tests_require=[
        'tox',
    ],
    packages=[
        'boodle',
        'booman',
        'boopak',
    ],
    package_dir={
        '': 'src',
    },
    scripts=[
        'script/boodler',
        'script/boodle-mgr',
        'script/boodle-event',
    ],
    ext_modules=[StdoutExtension()],
)
