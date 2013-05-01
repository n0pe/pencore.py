#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pencore import *
import sys

try:
	sys.argv[2]
except IndexError:
	print "Usage: ./penmode [tool] [host]"
	exit(1)

m = globals()['penmode']()

if m.dc.has_key(sys.argv[1]):
	func = getattr(m, sys.argv[1])()
	print func


