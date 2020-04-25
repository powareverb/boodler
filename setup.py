#!/usr/bin/env python

# Distutils setup script for Boodler.
#
# This has clever logic to build only the driver modules for which
# native libraries are available. (That is, it only builds the LAME
# driver if libmp3lame is installed, and so on.)

import os
import os.path
import re
import sys

from setuptools import setup, Command, Extension

from distutils.command.build_ext import build_ext
from distutils.command.build_scripts import build_scripts
from distutils.errors import *
from distutils.util import convert_path

import distutils.log


def append_if(cond, list1, list2):
    """append_if(cond, list1, list2) -> list

    Return a copy of list1, with list2 appended on if the condition is
    true.
    """

    res = list(list1)
    if (cond):
        res.extend(list2)
    return res


def check_header_available(path):
    """check_header_available(path) -> func(includedirs) -> bool

    Determine whether the given header is available in any of the
    configured include directories. The path should be in the usual
    C format: relative, forward slashes. (E.g.: 'sys/time.h')

    This function is curried. check_header_available(path) does not
    return a result; instead, it returns a function f(ls) which you
    can call when you have a list of include directories to check.
    The f(ls) function is what returns the boolean result.

    Confused? You would use this like this:

    fn = check_header_available('one.h')

    Now fn(ls) tells you whether 'one.h' is in any of the include
    directories listed in ls. It's set up this way because we don't
    know the include directories until compile time.
    """

    pathels = path.split('/')

    def resfunc(ls):
        for dir in ls:
            filename = os.path.join(dir, *pathels)
            if (os.path.isfile(filename)):
                return True
        distutils.log.info("unable to locate header '%s'", path)
        return False

    return resfunc


def check_all_available(*funcs):
    """check_all_available(func1, func2, ...) -> func(includedirs) -> bool

    Determine whether all of the given functions return True. This
    function is curried.

    There's no reason for that to make sense to you. You use it like this:

    fn = check_all_available(
        check_header_available('one.h'),
        check_header_available('two.h') )

    Now fn(ls) is a function that checks to make sure *both* 'one.h' and
    'two.h' are available. You pass a list of include directories to
    fn().
    """

    def resfunc(ls):
        for func in funcs:
            if (not func(ls)):
                return False
        return True
    return resfunc


class BooExtension(Extension):
    """BooExtension: A distutils.Extension class customized for Boodler
    driver extensions.

    Since all the drivers have nearly the same list of source files,
    this class generates the list at init time. You don't need to
    pass the source list in.

        BooExtension(key, available=bool) -- constructor

    The keyword argument 'available', if provided, must indicate
    whether the extension can be built. If not provided, True is
    assumed.
    """

    def __init__(self, key, **opts):
        self.boodler_key = key
        modname = 'boodle.cboodle_'+key

        ls = ['audev-'+key, 'cboodle-'+key, 'noteq', 'sample']
        ls = [('src/cboodle/' + val + '.c') for val in ls]

        avail = opts.pop('available', None)
        if (avail):
            self.ext_available = avail

        Extension.__init__(self, modname, ls, **opts)

    def ext_available(self, headerlist):
        return True


# The list of driver extensions.
all_extensions = [
    BooExtension('stdout'),
]


class local_build_ext(build_ext):
    """local_build_ext: A customization of the distutils build_ext
    command.

    This command understands these additional arguments:

        --with-drivers=LIST (force building these Boodler output drivers)
        --without-drivers=LIST (forbid building these Boodler output drivers)

    You can pass these arguments on the command line, or modify setup.cfg.

    This command also checks each extension before building, to make
    sure the appropriate headers are available. (Or whatever test
    the extension provides.)

    If you list a driver in the --with-drivers argument, the command will
    try to build it without any checking. (This could result in compilation
    errors.) If you list a driver in the --without-drivers argument, it
    will not be built at all. The format of these arguments is a
    comma-separated list of driver names; for example:

        setup.py build_ext --with-drivers=macosx --without-drivers=vorbis,shout
    """

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.with_driver_set = {}
        self.without_driver_set = {}

    def finalize_options(self):
        build_ext.finalize_options(self)

    def build_extension(self, ext):
        # First check whether the extension is buildable. Mostly this
        # involves looking at the available headers, so put together
        # a list of include dirs.
        ls = ['/usr/include', '/usr/local/include']

        if (sys.platform == 'darwin'):
            ls.append('/System/Library/Frameworks')
        ls = ls + self.include_dirs + ext.include_dirs

        use = ext.ext_available(ls)

        if (not use):
            distutils.log.info("skipping '%s' extension", ext.name)
            return

        build_ext.build_extension(self, ext)


class local_generate_pydoc(Command):
    """local_generate_pydoc: A special command to generate pydoc HTML files
    for each module.

    Pydoc is a wonderful thing, but its output is nonoptimal in a lot of
    ways. This runs pydoc on each module (except cboodle), and then massages
    the output. It also generates an index.html file for the doc/pydoc
    directory.

    The generate_pydoc command is not in the "build" or "install" pipeline,
    because I ran it before I distributed the source. You should already
    have a bunch of doc/pydoc/*.html files. If you run this command, they'll
    be rewritten, but they won't be any different.
    """

    description = "generate pydoc HTML (not needed for build/install)"
    user_options = [
        ('build-dir=', 'b', "build directory (.py files)"),
        ('pydoc-dir=', 'd', "output directory"),
        ('index-template=', None, "template for index.html"),
    ]

    def initialize_options(self):
        self.build_dir = None
        self.index_template = None
        self.pydoc_dir = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_dir'))
        if (self.index_template is None):
            self.index_template = 'doc/pydoc_template'
        if (self.pydoc_dir is None):
            self.pydoc_dir = 'doc/pydoc'

    def run(self):
        abs_build_dir = os.path.abspath(self.build_dir)
        abs_index_template = os.path.abspath(self.index_template)

        curdir = os.getcwd()
        try:
            os.chdir(self.pydoc_dir)
            self._generate(abs_build_dir, abs_index_template)
        finally:
            os.chdir(curdir)

    def _generate(self, buildpath, templatepath):
        try:
            import subprocess
        except:
            print('generate_pydoc requires Python 3.7 or later.')
            return

        packages = ['boodle', 'boopak', 'booman']
        PYTHON_DOC_URL = 'http://www.python.org/doc/current/library/'

        sysmodules = [
            '__builtin__', 'aifc', 'bisect', 'codecs',
            'cStringIO', 'errno', 'exceptions',
            'fcntl', 'fileinput',
            'imp', 'inspect', 'keyword', 'logging', 'math',
            'os', 're', 'readline', 'select', 'sets',
            'socket', 'StringIO', 'struct', 'sunau',
            'sys', 'tempfile', 'time', 'traceback', 'types', 'unittest',
            'wave', 'zipfile',
        ]
        sysmodules = dict([(key, True) for key in sysmodules])

        fl = open(templatepath)
        template = fl.read()
        fl.close()

        pos = template.find('<!-- CONTENT -->')

        if (pos < 0):
            raise Exception('template does not contain <!-- CONTENT --> line')

        index_head = template[:pos]
        index_tail = template[pos:]

        modules = []

        for pkg in packages:
            path = os.path.join(buildpath, pkg)
            if (not os.path.isdir(path)):
                raise Exception('package does not exist: ' + path)

            modules.append(pkg)

            files = sorted(os.listdir(path))
            for file in files:
                if (file.startswith('_')):
                    continue
                if (file.startswith('test_')):
                    continue
                if (not file.endswith('.py')):
                    continue
                modules.append(pkg+'.'+file[:-3])

        fileurl_regex = re.compile('href="file:([^"]*)"')
        sysmod_regex = re.compile('href="([a-zA-Z_]*).html(#[a-zA-Z_]*)?"')
        testmod_regex = re.compile('<a href="[a-z]*.test_[a-z]*.html">([a-z_]*)</a>')
        cboodlemod_regex = re.compile('<a href="[a-z]*.cboodle_[a-z]*.html">([a-z_]*)</a>')
        agentinherit_regex = re.compile('Methods inherited from <a href="boodle.agent.html#Agent">boodle.agent.Agent</a>:.*?</td>', re.DOTALL)
        memaddress_regex = re.compile(' at 0x[a-f0-9]*&gt;')
        whitecolor_regex = re.compile('"#fffff"')

        def fileurl_func(match):
            val = match.group(1)
            pos = val.find(buildpath)
            if (pos < 0):
                raise Exception('buildpath not in fileurl')
            srcname = val[ pos+len(buildpath) : ]
            return 'href="../../src%s"' % (srcname,)

        def sysmod_func(match):
            val = match.group(1)
            if (val not in sysmodules):
                if (not (val in packages)):
                    print('Warning: link to "%s.html" unmunged.' % (val,))
                return match.group(0)
            val = val.lower()
            if (val == 'cstringio'):
                val = 'stringio'
            fragment = match.group(2)
            if (fragment is None):
                fragment = ''
            return 'href="%s%s.html%s"' % (PYTHON_DOC_URL, val, fragment)

        newenv = dict(os.environ)
        val = buildpath
        if ('PYTHONPATH' in newenv):
            val = val + ':' + newenv['PYTHONPATH']
        newenv['PYTHONPATH'] = val

        for mod in modules:
            ret = subprocess.call(['pydoc', '-w', mod], env=newenv)
            if (ret):
                print('pydoc failed on', mod, ':', ret)
                sys.exit(1)

            file = mod+'.html'
            fl = open(file)
            dat = fl.read()
            fl.close()

            newdat = dat + '\n'
            newdat = fileurl_regex.sub(fileurl_func, newdat)
            newdat = newdat.replace(buildpath+'/', '')
            newdat = sysmod_regex.sub(sysmod_func, newdat)
            newdat = testmod_regex.sub('\\1', newdat)
            newdat = cboodlemod_regex.sub('\\1', newdat)
            if (mod == 'boodle.builtin'):
                newdat = agentinherit_regex.sub('</td>', newdat)
            newdat = newdat.replace('href="."', 'href="index.html"')
            newdat = memaddress_regex.sub('&gt;', newdat)
            newdat = whitecolor_regex.sub('"#ffffff"', newdat)

            fl = open(file, 'w')
            fl.write(newdat)
            fl.close()

        modsets = []
        for mod in modules:
            if (not ('.' in mod)):
                modsets.append([])
            modsets[-1].append(mod)

        fl = open('index.html', 'w')
        fl.write(index_head)
        for ls in modsets:
            fl.write('<td width="25%" valign=top>\n')
            for mod in ls:
                if (not ('.' in mod)):
                    fl.write('<strong><a href="%s.html">%s</a></strong><br>\n' % (mod, mod))
                else:
                    fl.write('<a href="%s.html">%s</a><br>\n' % (mod, mod))
            fl.write('</td>\n')
        fl.write(index_tail)
        fl.close()
        print('build index.html')


setup(name='Boodler',
      version='2.0.4',
      description='A programmable soundscape tool',
      author='Andrew Plotkin',
      author_email='erkyrath@eblong.com',
      url='http://boodler.org/',
      license='GNU LGPL',
      platforms=['MacOS X', 'POSIX'],
      classifiers=[
          'Topic :: Multimedia :: Sound/Audio :: Mixers',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3',
      ],
      long_description="""
Boodler is a tool for creating soundscapes -- continuous, infinitely
varying streams of sound. Boodler is designed to run in the background
on a computer, maintaining whatever sound environment you desire.

Boodler is extensible, customizable, and modular. Each soundscape is a
small piece of Python code -- typically less than a page. A soundscape
can incorporate other soundscapes; it can combine other soundscapes,
switch between them, fade them in and out. This package comes with
many example soundscapes. You can use these, modify them, combine them
to arbitrary levels of complexity, or write your own.
""",
      install_requires=[
          'packaging',
      ],
      packages=[
          'boodle',
          'boopak',
          'booman',
      ],
      package_dir={
          '': 'src',
      },
      scripts=[
          'script/boodler',
          'script/boodle-mgr',
          'script/boodle-event',
      ],
      ext_modules=list(all_extensions),
      cmdclass={
          'build_ext': local_build_ext,
          'generate_pydoc': local_generate_pydoc,
      })
