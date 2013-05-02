#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pencore import *
import sys
print sys.argv


def usage():
	print "Usage: ./penmode [tool] -p [parameters] [host]"
	exit(1)

try:
	str(sys.argv[1])
	str(sys.argv[-1])
except IndexError:
	usage()
	

m = globals()['penmode']()

if m.dc.has_key(sys.argv[1]):
	func = getattr(m, sys.argv[1])()
	print func


