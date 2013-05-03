#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



############################# DISCLAIMER ################################
# Usage of this software for probing/attacking targets without prior
# mutual consent, is illegal. It's the end user's responsability to
# obey alla applicable local laws. Developers assume no liability and
# are not responible for any missue or damage caused by thi program
#########################################################################

from pencore import *
from optparse import OptionParser, OptionGroup
import sys
	
m = globals()['penmode']()

if m.dc.has_key(sys.argv[1]):
	func = getattr(m, sys.argv[1])()
	m.run_command(func)


