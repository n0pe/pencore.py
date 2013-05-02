#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pencore import *
from optparse import OptionParser, OptionGroup
import sys
	
m = globals()['penmode']()

if m.dc.has_key(sys.argv[1]):
	func = getattr(m, sys.argv[1])()
	print func


