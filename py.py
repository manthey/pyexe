#!/usr/bin/python
#
# This is a small stub that is intended to be built into an executable with a
# setup.py file using "python setup.py py2exe".  This results in an executable
# called py.exe.  This can be used to run an arbitrary python script on Windows
# (XP and later) via py.exe (name of script).
#
# Changes:
#  2.7.4.1:
#   * initial release
#  2.7.4.2:
#   * fixed an issue with __file__ and __name__
#  2.7.4.3:
#   * Added the program path to sys.path when running a program, and "" to
# sys.path when running direct or interpretted.
#  2.7.5.4:
#   * Upgraded to python 2.7.5
#  2.7.5.5:
#   * Imported submodules, such as logging.handlers, since they weren't
# included implicitly.
#  2.7.8.6:
#   * Added support for multiprocessing forking
#   * Added support for non-ttty direct usage (input and output pipes, for
# instance)
#   * Added support for -i option and PYTHONINSPECT environment variable.
#   * Turned off "frozen" flag in py.exe
#   * Upgraded pywin32 to build 219 (was 218).
#   * Upgraded to python 2.7.8
#   * Added import site to interactive prompts to get help and other commands
# added to the builtins.
#   * Added support for unbuffered -u option and PYTHONUNBUFFERED environment
# variable.
#  2.7.8.7:
#   * Added support for -E, -x, and --version options.
#   * Changed how the globals / locals dictionaries are used for greater
# consistency in different execution modes.
#   * Accept multiple single letter command line options grouped together.
#  2.7.8.8:
#   * Fixed a bug I introduced in the last version when renaming the variable
# "loc".
#  2.7.8.9:
#   * My change to make globals dictionaries more consistent broke
# multiprocessing forking.  I've reverted some of the changes.
#  2.7.9.10:
#   * Upgraded to python 2.7.9
#   * Added psutil 2.1.3 win32
#   * Added support for the -m option.
#   * Turned off the optimization flag when building py.exe.  Having it on
# interferes with some modules (such as sympy) which rely on docstring
# manipulation.

AllModules = False

import os
import sys

if len(sys.argv)==1 and not hasattr(sys, "frozen"):
   AllModules = True
if not AllModules and sys.argv[:2][-1]!="--all":
   pass
else:
   # I think this is the complete list of modules in the Python 2.7
   # installation on Windows XP.  This was the default 2.7 installation without
   # any options, plus pywin32-219, psutil 2.1.3, setuptools, and py2exe.  I
   # generated the list of modules with help("modules").  I then commented out
   # anything that wouldn't import.  Further, there are some submodules that
   # don't automatically import with the base module.  help("modules .") lists
   # these.  Any module that isn't present with its base but can be imported
   # was then added.
   import BaseHTTPServer
   import Bastion
   import CGIHTTPServer
   import ConfigParser
   import Cookie
   import DocXMLRPCServer
   import HTMLParser
   import MimeWriter
   import Queue
   import SimpleHTTPServer
   import SimpleXMLRPCServer
   import SocketServer
   import StringIO
   import UserDict
   import UserList
   import UserString
   import _LWPCookieJar
   import _MozillaCookieJar
   import __builtin__
   import __future__
   import _abcoll
   import _ast
   import _bisect
   import _bsddb
   import _codecs
   import _codecs_cn
   import _codecs_hk
   import _codecs_iso2022
   import _codecs_jp
   import _codecs_kr
   import _codecs_tw
   import _collections
   import _csv
   import _ctypes
   import _ctypes_test
   import _elementtree
   import _functools
   import _hashlib
   import _heapq
   import _hotshot
   import _io
   import _json
   import _locale
   import _lsprof
   import _md5
   import _markerlib
   import _memimporter
   import _msi
   import _multibytecodec
   import _multiprocessing
   import _osx_support
   import _pyio
   import _random
   import _sha
   import _sha256
   import _sha512
   import _socket
   import _sqlite3
   import _sre
   import _ssl
   import _strptime
   import _struct
   import _subprocess
   import _symtable
   import _testcapi
   import _threading_local
   import _warnings
   import _weakref
   import _weakrefset
   import _win32sysloader
   import _winreg
   import _winxptheme
   import abc
   import afxres
   import aifc
   import anydbm
   import argparse
   import array
   import ast
   import asynchat
   import asyncore
   import atexit
   import audiodev
   import audioop
   import base64
   import bdb
   import binascii
   import binhex
   import bisect
   import bsddb
   import bsddb.dbobj
   import bsddb.dbrecio
   import bsddb.dbshelve
   import bsddb.dbtables
   import bz2
   import cPickle
   import cProfile
   import cStringIO
   import calendar
   import cgi
   import cgitb
   import chunk
   import cmath
   import cmd
   import code
   import codecs
   import codeop
   import collections
   import colorsys
   import commands
   import commctrl
   import compileall
   import compiler
   import contextlib
   import cookielib
   import copy
   import copy_reg
   import csv
   import ctypes
   import ctypes.macholib
   import ctypes.macholib.dyld
   import ctypes.util
   import ctypes.wintypes
   import datetime
   import dbhash
   import dbi
   import decimal
   import difflib
   import dircache
   import dis
   import distutils
   import distutils.archive_util
   import distutils.bcppcompiler
   import distutils.cmd
   import distutils.command
   import distutils.command.bdist
   import distutils.command.bdist_dumb
   import distutils.command.bdist_msi
   import distutils.command.bdist_rpm
   import distutils.command.bdist_wininst
   import distutils.command.build
   import distutils.command.build_clib
   import distutils.command.build_ext
   import distutils.command.build_py
   import distutils.command.build_scripts
   import distutils.command.check
   import distutils.command.clean
   import distutils.command.config
   import distutils.command.install
   import distutils.command.install_data
   import distutils.command.install_egg_info
   import distutils.command.install_headers
   import distutils.command.install_lib
   import distutils.command.install_scripts
   import distutils.command.register
   import distutils.command.sdist
   import distutils.command.upload
   import distutils.cygwinccompiler
   import distutils.emxccompiler
   import distutils.versionpredicate
   import doctest
   import dumbdbm
   import dummy_thread
   import dummy_threading
   import easy_install
   import email
   import email._parseaddr
   import email.base64mime
   import email.charset
   import email.feedparser
   import email.generator
   import email.mime.application
   import email.mime.audio
   import email.mime.image
   import email.mime.message
   import email.mime.multipart
   import email.mime.text
   import email.parser
   import encodings
   import encodings.base64_codec
   import encodings.big5
   import encodings.big5hkscs
   import encodings.bz2_codec
   import encodings.charmap
   import encodings.cp037
   import encodings.cp1006
   import encodings.cp1026
   import encodings.cp1140
   import encodings.cp1250
   import encodings.cp1251
   import encodings.cp1253
   import encodings.cp1254
   import encodings.cp1255
   import encodings.cp1256
   import encodings.cp1257
   import encodings.cp1258
   import encodings.cp424
   import encodings.cp437
   import encodings.cp500
   import encodings.cp720
   import encodings.cp737
   import encodings.cp775
   import encodings.cp850
   import encodings.cp852
   import encodings.cp855
   import encodings.cp856
   import encodings.cp857
   import encodings.cp858
   import encodings.cp860
   import encodings.cp861
   import encodings.cp862
   import encodings.cp863
   import encodings.cp864
   import encodings.cp865
   import encodings.cp866
   import encodings.cp869
   import encodings.cp874
   import encodings.cp875
   import encodings.cp932
   import encodings.cp949
   import encodings.cp950
   import encodings.euc_jis_2004
   import encodings.euc_jisx0213
   import encodings.euc_jp
   import encodings.euc_kr
   import encodings.gb18030
   import encodings.gb2312
   import encodings.gbk
   import encodings.hex_codec
   import encodings.hp_roman8
   import encodings.hz
   import encodings.idna
   import encodings.iso2022_jp
   import encodings.iso2022_jp_1
   import encodings.iso2022_jp_2
   import encodings.iso2022_jp_2004
   import encodings.iso2022_jp_3
   import encodings.iso2022_jp_ext
   import encodings.iso2022_kr
   import encodings.iso8859_1
   import encodings.iso8859_10
   import encodings.iso8859_11
   import encodings.iso8859_13
   import encodings.iso8859_14
   import encodings.iso8859_15
   import encodings.iso8859_16
   import encodings.iso8859_2
   import encodings.iso8859_3
   import encodings.iso8859_4
   import encodings.iso8859_5
   import encodings.iso8859_6
   import encodings.iso8859_7
   import encodings.iso8859_8
   import encodings.iso8859_9
   import encodings.johab
   import encodings.koi8_r
   import encodings.koi8_u
   import encodings.latin_1
   import encodings.mac_arabic
   import encodings.mac_centeuro
   import encodings.mac_croatian
   import encodings.mac_cyrillic
   import encodings.mac_farsi
   import encodings.mac_greek
   import encodings.mac_iceland
   import encodings.mac_latin2
   import encodings.mac_roman
   import encodings.mac_romanian
   import encodings.mac_turkish
   import encodings.mbcs
   import encodings.palmos
   import encodings.ptcp154
   import encodings.punycode
   import encodings.quopri_codec
   import encodings.raw_unicode_escape
   import encodings.rot_13
   import encodings.shift_jis
   import encodings.shift_jis_2004
   import encodings.shift_jisx0213
   import encodings.string_escape
   import encodings.tis_620
   import encodings.undefined
   import encodings.unicode_escape
   import encodings.unicode_internal
   import encodings.utf_16
   import encodings.utf_16_be
   import encodings.utf_16_le
   import encodings.utf_32
   import encodings.utf_32_be
   import encodings.utf_32_le
   import encodings.utf_7
   import encodings.utf_8
   import encodings.utf_8_sig
   import encodings.uu_codec
   import encodings.zlib_codec
   import ensurepip
   import ensurepip.__main__
   import ensurepip._uninstall
   import errno
   import exceptions
   import filecmp
   import fileinput
   import fnmatch
   import formatter
   import fpformat
   import fractions
   import ftplib
   import functools
   import future_builtins
   import gc
   import genericpath
   import getopt
   import getpass
   import gettext
   import glob
   import gzip
   import hashlib
   import heapq
   import hmac
   import hotshot
   import hotshot.log
   import hotshot.stats
   import htmlentitydefs
   import htmllib
   import httplib
   import ihooks
   import imageop
   import imaplib
   import imghdr
   import imp
   import importlib
   import imputil
   import inspect
   import io
   import isapi
   import isapi.install
   import isapi.isapicon
   import isapi.simple
   import isapi.threaded_extension
   import itertools
   import json
   import json.decoder
   import json.encoder
   import json.scanner
   import json.tool
   import keyword
   #import lib2to3 # I've also exclude all submodules of lib2to3
   import linecache
   import locale
   import logging
   import logging.config
   import macpath
   import macurl2path
   import mailbox
   import mailcap
   import markupbase
   import marshal
   import math
   import md5
   import mhlib
   import mimetools
   import mimetypes
   import mimify
   import mmap
   import mmapfile
   import mmsystem
   import modulefinder
   import msilib
   import msvcrt
   import multifile
   import multiprocessing
   import multiprocessing.connection
   import multiprocessing.dummy
   import multiprocessing.heap
   import multiprocessing.managers
   import multiprocessing.pool
   import multiprocessing.queues
   import multiprocessing.reduction
   import multiprocessing.sharedctypes
   import mutex
   import netbios
   import netrc
   import new
   import nntplib
   import nt
   import ntpath
   import ntsecuritycon
   import nturl2path
   import numbers
   import odbc
   import opcode
   import operator
   import optparse
   import os
   import os2emxpath
   import parser
   import pdb
   import perfmon
   import pickle
   import pickletools
   import pip
   import pip.__main__
   import pip._vendor._markerlib
   import pip._vendor.distlib._backport.misc
   import pip._vendor.distlib._backport.sysconfig
   import pip._vendor.distlib.database
   import pip._vendor.distlib.index
   import pip._vendor.distlib.locators
   import pip._vendor.distlib.manifest
   import pip._vendor.html5lib.filters
   import pip._vendor.html5lib.filters._base
   import pip._vendor.html5lib.filters.alphabeticalattributes
   import pip._vendor.html5lib.filters.inject_meta_charset
   import pip._vendor.html5lib.filters.lint
   import pip._vendor.html5lib.filters.optionaltags
   import pip._vendor.html5lib.filters.sanitizer
   import pip._vendor.html5lib.filters.whitespace
   import pip._vendor.html5lib.ihatexml
   import pip._vendor.html5lib.treeadapters
   import pip._vendor.html5lib.treeadapters.sax
   import pip._vendor.html5lib.treebuilders.dom
   import pip._vendor.html5lib.treebuilders.etree
   import pip._vendor.html5lib.treewalkers._base
   import pip._vendor.html5lib.treewalkers.dom
   import pip._vendor.html5lib.treewalkers.etree
   import pip._vendor.html5lib.treewalkers.pulldom
   import pip._vendor.requests.packages.chardet.big5freq
   import pip._vendor.requests.packages.chardet.big5prober
   import pip._vendor.requests.packages.chardet.charsetgroupprober
   import pip._vendor.requests.packages.chardet.cp949prober
   import pip._vendor.requests.packages.chardet.escprober
   import pip._vendor.requests.packages.chardet.eucjpprober
   import pip._vendor.requests.packages.chardet.euckrprober
   import pip._vendor.requests.packages.chardet.euctwprober
   import pip._vendor.requests.packages.chardet.gb2312prober
   import pip._vendor.requests.packages.chardet.hebrewprober
   import pip._vendor.requests.packages.chardet.langbulgarianmodel
   import pip._vendor.requests.packages.chardet.langcyrillicmodel
   import pip._vendor.requests.packages.chardet.langgreekmodel
   import pip._vendor.requests.packages.chardet.langhebrewmodel
   import pip._vendor.requests.packages.chardet.langhungarianmodel
   import pip._vendor.requests.packages.chardet.langthaimodel
   import pip._vendor.requests.packages.chardet.latin1prober
   import pip._vendor.requests.packages.chardet.mbcsgroupprober
   import pip._vendor.requests.packages.chardet.sbcharsetprober
   import pip._vendor.requests.packages.chardet.sbcsgroupprober
   import pip._vendor.requests.packages.chardet.universaldetector
   import pip._vendor.requests.packages.urllib3.packages.ssl_match_hostname._implementation
   import pipes
   import pkg_resources
   import pkgutil
   import platform
   import plistlib
   import popen2
   import poplib
   import posixfile
   import posixpath
   import pprint
   import profile
   import pstats
   import psutil
   import py_compile
   import pyclbr
   import pydoc
   import pydoc_data
   import pydoc_data.topics
   import pyexpat
   import pythoncom
   import pywin
   #import pywin.debugger  # requires win32ui
   #import pywin.dialogs   # requires win32ui
   #import pywin.docking   # requires win32ui
   #import pywin.framework # requires win32ui
   import pywin.idle.AutoExpand
   import pywin.idle.CallTips
   import pywin.idle.FormatParagraph
   import pywin.idle.IdleHistory
   #import pywin.mfc       # requires win32ui
   #import pywin.scintilla # requires win32ui
   #import pywin.tools     # requires win32ui
   import pywin32_testutil
   import pywintypes
   import quopri
   import random
   import rasutil
   import re
   import regcheck
   import regutil
   import repr
   import rexec
   import rfc822
   import rlcompleter
   import robotparser
   import runpy
   import sched
   import select
   import servicemanager
   import sets
   import setuptools
   import sgmllib
   import sha
   import shelve
   import shlex
   import shutil
   import signal
   import site
   import smtpd
   import smtplib
   import sndhdr
   import socket
   import sqlite3
   import sqlite3.dump
   import sre
   import sre_compile
   import sre_constants
   import sre_parse
   import ssl
   import sspi
   import sspicon
   import stat
   import statvfs
   import string
   import stringold
   import stringprep
   import strop
   import struct
   import subprocess
   import sunau
   import sunaudio
   import symbol
   import symtable
   import sys
   import sysconfig
   import tabnanny
   import tarfile
   import telnetlib
   import tempfile
   import textwrap
   import thread
   import threading
   import time
   import timeit
   import timer
   import toaiff
   import token
   import tokenize
   import trace
   import traceback
   import types
   import unicodedata
   import unittest
   import urllib
   import urllib2
   import urlparse
   import user
   import uu
   import uuid
   import warnings
   import wave
   import weakref
   import webbrowser
   import whichdb
   #import win2kras # must be after win32ras, but even then it doesn't import
   import win32api
   import win32clipboard
   import win32com
   # Much of win32com is really located in win32comext.  py2exe doesn't attach
   # this properly, and I haven't gotten the work-around working.
   #import win32com.adsi
   #import win32com.adsi.adsicon
   #import win32com.authorization
   #import win32com.authorization.authorization
   #import win32com.axcontrol
   #import win32com.axcontrol.axcontrol
   #import win32com.axdebug
   #import win32com.axdebug.debugger
   #import win32com.axdebug.dump
   #import win32com.axscript.asputil
   #import win32com.axscript.client
   #import win32com.axscript.client.debug
   #import win32com.axscript.client.pydumper
   #import win32com.axscript.client.pyscript_rexec
   #import win32com.axscript.server
   #import win32com.axscript.server.axsite
   #import win32com.axscript.server.error
   #import win32com.bits
   #import win32com.bits.bits
   # import win32com.client.combrowse # requires win32ui
   import win32com.client.genpy
   import win32com.client.makepy
   #import win32com.client.tlbrowse # requires win32ui
   import win32com.decimal_23
   #import win32com.directsound
   #import win32com.directsound.directsound
   #import win32com.ifilter
   #import win32com.ifilter.ifilter
   #import win32com.ifilter.ifiltercon
   #import win32com.internet
   #import win32com.internet.inetcon
   #import win32com.internet.internet
   import win32com.makegw
   import win32com.makegw.makegw
   import win32com.makegw.makegwenum
   #import win32com.mapi
   #import win32com.mapi.emsabtags
   #import win32com.mapi.exchange
   #import win32com.mapi.exchdapi
   #import win32com.mapi.mapi
   #import win32com.mapi.mapiutil
   #import win32com.propsys
   #import win32com.propsys.pscon
   import win32com.server.factory
   import win32com.server.localserver
   import win32com.servers
   import win32com.servers.PythonTools
   import win32com.servers.dictionary
   import win32com.servers.interp
   import win32com.servers.perfmon
   import win32com.servers.test_pycomtest
   #import win32com.shell
   #import win32com.shell.shell
   #import win32com.shell.shellcon
   import win32com.storagecon
   #import win32com.taskscheduler
   #import win32com.taskscheduler.taskscheduler
   #import win32com.test # excluded
   import win32con
   import win32console
   import win32cred
   import win32crypt
   import win32cryptcon
   import win32event
   import win32evtlog
   import win32evtlogutil
   import win32file
   import win32gui
   import win32gui_struct
   import win32help
   import win32inet
   import win32inetcon
   import win32job
   import win32lz
   import win32net
   import win32netcon
   import win32pdh
   import win32pdhquery
   import win32pdhutil
   import win32pipe
   import win32print
   import win32process
   import win32profile
   import win32ras
   import win32rcparser
   import win32security
   import win32service
   import win32serviceutil
   import win32timezone
   import win32trace
   import win32transaction
   import win32ts
   #import win32ui    # requires additional dll
   #import win32uiole # requires additional dll
   import win32verstamp
   import win32wnet
   import winerror
   import winioctlcon
   import winnt
   import winperf
   import winsound
   import winxpgui
   import winxptheme
   import wsgiref
   import wsgiref.handlers
   import wsgiref.simple_server
   import wsgiref.validate
   import xdrlib
   import xml
   import xml.dom.expatbuilder
   import xml.etree.ElementInclude
   import xml.sax.expatreader
   import xmllib
   import xmlrpclib
   import xxsubtype
   import zipextimporter
   import zipfile
   import zipimport
   import zlib


def alternate_raw_input(prompt=None):
   """Write the prompt to stderr, then call raw_input without a prompt.
    This is to try to mimic better what the python executable does.
   Enter: prompt: prompt to print to stderr."""
   if prompt and len(prompt):
      sys.stderr.write(prompt)
      sys.stderr.flush()
   return raw_input("")


if hasattr(sys, "frozen"):
   delattr(sys, "frozen")
Help = False
DirectCmd = None
ImportSite = True
Interactive = "check"
RunModule = False
ShowVersion = False
SkipFirstLine = False
Start = None
Unbuffered = False
UseEnvironment = True
skip = 0
for i in xrange(1, len(sys.argv)):
   if DirectCmd is not None:
      break
   if skip:
      skip -= 1
      continue
   arg = sys.argv[i]
   if arg.startswith("-") and arg[1:2]!="-":
      for let in arg[1:]:
         if let=="c":
            DirectCmd = " ".join(sys.argv[i+1+skip:])
            DirectCmd = sys.argv[i+1+skip:]
         elif let=="E":
            UseEnvironment = False
         elif let=="i":
            Interactive = True
         elif let=="m" and i+1<len(sys.argv):
            RunModule = sys.argv[i+1]
            skip = 1
         elif let=="S":
            ImportSite = False
         elif let=="u":
            Unbuffered = True
         elif let=="V":
            ShowVersion = True
         elif let=="x":
            SkipFirstLine = True
         elif let in ("E", "O"):
            # ignore these options
            pass
         else:
            Help = True
   elif arg=="--all":
      continue
   elif arg=="--help" or arg=="-h" or arg=="/?":
      Help = True
   elif arg=="--multiprocessing-fork":
      skip = 1
      import multiprocessing.forking
      multiprocessing.forking.freeze_support()
   elif arg=="--version":
      ShowVersion = True
   elif arg.startswith("-"):
      Help = True
   elif not Start:
      Start = i
      break
if Help:
   print """Stand-Alone Python Interpreter

Syntax: py.exe [--all] [--help] [-c (cmd) | -m (module) | (python file) [arg]]
               [-i] [-S] [-u] [-V] [-x]
               [--multiprocessing-fork (handle)]

--all attempts to import all modules.
-c runs the remaining options as a program.
-E ignores environment variables.
-i forces a prompt even if stdin does not appear to be a terminal; also
  PYTHONINSPECT=x
--help, -h, or /? prints this message.
-m runs the specified python module.
--multiprocessing-fork supports the multiprocessing module.
-S supresses importing the site module
-u runs in unbuffered mode; also PYTHONUNBUFFERED=x
-V prints the version and exits (--version also works).
-x skips the first line of a source file.
If no file is specified and stdin is a terminal, the interactive interpreter is
  started."""
   #print sys.argv, repr(sys.argv)
   sys.exit(0)
if ShowVersion:            
   from py_version import Version, Description
   print "%s, Version %s"%(Description,Version)
   sys.exit(0)
if Interactive=="check" and UseEnvironment:
   if os.environ.get("PYTHONINSPECT"):
      Interactive = True
if Unbuffered is False and UseEnvironment:
   if os.environ.get("PYTHONUNBUFFERED"):
      Unbuffered = True
if Unbuffered:
   sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 0)
   sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
   sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
if ImportSite:
   import site
# Generate the globals/locals environment
globenv = {}
for key in globals().keys():
   if key.startswith("_"): # or key=="AllModules":
      globenv[key] = globals()[key]
if Start:
   sys.argv = sys.argv[Start:]
   __name__ = "__main__"
   __file__ = sys.argv[0]
   sys.path[0:0] = [os.path.split(__file__)[0]]
   # If I try to use the simplified global dictionary, multiprocessing doesn't
   # work.
   if not SkipFirstLine:
      #execfile(sys.argv[0], globenv)
      execfile(sys.argv[0])
   else:
      fptr = open(sys.argv[0])
      discard = fptr.readline()
      src = fptr.read()
      fptr.close()
      #exec src in globenv
      #exec src
elif RunModule:
   import runpy
   runpy.run_module(RunModule, run_name='__main__')
elif DirectCmd:
   sys.path[0:0] = [""]
   sys.argv = DirectCmd
   exec DirectCmd[0] in globenv
else:
   if Interactive=="check":
      Interactive = sys.stdin.isatty()
   sys.path[0:0] = [""]
   if Interactive:
      import code
      cons = code.InteractiveConsole(locals=globenv)
      if not sys.stdout.isatty():
         cons.raw_input = alternate_raw_input
         if not Unbuffered:
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
            sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
      cons.interact()
   elif False:
      # This will run code as it comes it, rather than wait until it has parsed
      # it all; it doesn't seem to be what the main python interpreter ever
      # does, however.
      import code
      interp = code.InteractiveInterpreter(locals=globenv)
      src = []
      for line in sys.stdin:
         if not len(line.rstrip("\r\n")):
            continue
         if line.startswith("#"):
            continue
         if line.rstrip("\r\n")[0:1] not in (" ", "\t"):
            if len(src):
               interp.runsource("".join(src), "<stdin>")
               src = []
         src.append(line)
      if len(src):
         interp.runsource("".join(src))
   else:
      src = sys.stdin.read()
      # This doesn't work the way I expect for some reason
      #interp = code.InteractiveInterpreter(locals=globenv)
      #interp.runsource(src, "<stdin>")
      # But an exec works fine
      exec src in globenv

