#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Penmode.

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


import datetime
import os.path
import sys
from subprocess import Popen, PIPE
from urllib2 import urlopen

#Usage
def usage():
	print "Usage: ./penmode [tool] -p [parameters] [host]"
	exit(1)

#Color 
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

def green(word):
	return GREEN + word + END

def yellow(word):
	return YELLOW + word + END

def red(word):
	return RED + word + END



class penmode:
	def __init__(self):
		
		#Target
		self.t = None
		
		#Parameters
		self.p = None
		
		#Log file
		self.lf = None
		
		#Dictionary (the tools)
		self.dc = {}
		
		# Check tools
		self.check_tools()
		
		# Settings
		self.settings()
		
		# IP del target da tor-resolve
		self.ip = str(Popen('tor-resolve '+self.t+' 127.0.0.1:9050', shell=True, stdout=PIPE).stdout.read()).replace("b''",'')
		
		
	def settings(self):
		
		#Check for parameters and target
		try:
			sys.argv[2]
			if sys.argv[2] == "-p":
				self.p = sys.argv[3]
				
			elif sys.argv[2] == "-f":
				self.fl = sys.argv[3]
				
			elif sys.argv[2] == "-g":
				#Start gui
				print "GUI"
		except IndexError:
			next
				
		#Check for target
		self.t = sys.argv[-1]
		if self.dc.has_key(self.t):
			usage()
		
		if self.t[0:7] == "http://":
			self.t = sys.argv[-1][7:]
			
		self.ip = str(Popen('tor-resolve '+self.t+' 127.0.0.1:9050', shell=True, stdout=PIPE).stdout.read()).replace("b''",'')
		
	def check_tools(self):
		
		#Check proxychains and socat
		if not os.path.exists('/usr/bin/proxychains') or not os.path.exists('/usr/bin/socat'):
			print red("Please, install "+green("proxychains ")+red("and ")+green("socat."))
			exit(1)
		
		#Check the tools
		tools = ['nmap', 'whatweb', 'skipfish', 'wpscan', 'sqlmap', 'joomscan', 'nikto']
		for i in tools:
			needle = "/usr/bin/"+i
			if os.path.exists(needle):
				self.dc[i] = 1
			else:
				self.dc[i] = 0

	def pendate(self):
		# Funzione che rileva la data per i log
		return datetime.datetime.now().strftime("-%m-%d-%Y_%H-%M")
	
	def sqlmap(self):
		return 'sudo proxychains sqlmap --wizard | tee ./' + self.t + self.pendate() + '.txt'	

	def nmap(self):
		if self.p:
			return 'sudo proxychains nmap ' + self.p + ' ' + self.t + ' | tee ./' + self.t + self.pendate() + '.txt'
		else:
			return 'sudo proxychains nmap -sV -O -P0 -p 21,22,25,53,80,135,139,443,445 ' + self.t + ' | tee ./' + self.t + self.pendate() + '.txt'

	def whatweb(self):
		return 'whatweb -v 127.0.0.1:8080 | tee ./nmap' + self.ip + self.pendate() + '.txt'
	
	def slowloris(self,number,timeout):
		return 'perl /opt/backbox/penmode/slowloris.pl -dns 127.0.0.1 -port 8080 -timeout '+str(timeout)+' -num '+str(number)
		
	def exploit(self):
		return 'sudo proxychains htexploit -u' + self.ip + '-o -w --verbose 3'
		
	def skipfish(self):
		return 'sudo proxychains skipfish -o /home/' + self.ip + 'http.//' + self.ip
	
	def wpscan(self):
		return 'sudo proxychains wpscan --url' + self.ip + ' | tee ./wpscan' + self.pendate() + '.txt'
		
	def joomscan(self):
		return 'joomscan -u' + self.ip + '-x 127.0.0.1:8080 | tee ./joomscan' + self.pendate() + '.txt'
		
	def nikto(self):
		return 'nikto -h 127.0.0.1:8080 | tee ./nikto' + self.pendate() + '.txt'
