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
import subprocess
from optparse import OptionParser, OptionGroup

#Usage
def usage():
	print ("\nUsage: ./penmode.py [tool] -p [parameters] -t [host]\n")
	print ("Split parameters with comma, for example: \n\n ./penmode.py nmap -p -sS,-p80 -t 127.0.0.1\n")
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
		
		#Log file
		self.lf = None
		
		#Dictionary (the tools)
		self.dc = {}
		
		#Parameters
		self.par = None
		
		#Check for parameters
		#self.get_params()
		
		#Check tools
		self.check_tools()
		
		#Is GUI?
		self.gui = 0
	
	def set_target(self,target):
		self.t = target
		#Settings and configuration
		self.settings()
	
	def set_gui(self,gui):
		self.isgui = gui
	
	def get_params(self):
		parser = OptionParser()
		
		#Options
		parser.add_option( "-t", "--target", action="store", dest="target", default=False, help="Target address." );
		parser.add_option( "-p", "--params", action="store", dest="params", default=False, help="Additional parameters." );
		parser.add_option( "-o", "--output", action="store", dest="output", default=None, help="Output file" );
		
		(o,args) = parser.parse_args()
		
		#Check for Target
		if not o.target:
			if self.isgui == 0:
				print (red("\nSpecific target!"))
				usage()
				exit(1)
		else:
			self.t = o.target
			
		#Check for parameters
		if o.params and o.params != None:
			c = o.params.split(',')
			for a in c:
				self.par = ' '.join(c)
			
		#Check for LogFile
		elif o.output:
			self.fl = o.output
	
	def settings(self):
		
		#Adjust target
		if self.t[0:7] == "http://":
			self.t = self.t[-1][7:]
			
		self.t = str(Popen('tor-resolve '+self.t+' 127.0.0.1:9050', shell=True, stdout=PIPE).stdout.read()).replace("b'",'')
		self.t = self.t[:-3]
		self.start_proxy()
		
		
	def check_tor(self):
		#Tor is running?
		stdout = Popen('ps aux | grep torrc | grep -v grep', shell=True, stdout=PIPE).stdout
		stdout = str(stdout.read()).replace("b''",'')
		if not stdout:
			return 0
		else:
			return 1
            
	def check_socat(self):
		#Socat is running?
		stdout = Popen('(ps caux | grep socat)', shell=True, stdout=PIPE).stdout
		stdout = str(stdout.read()).replace("b''",'')
		if not stdout:
			return 0
		else:
			return 1
            
	def start_proxy(self):
		#Start Tor and Socat
		if self.check_tor() == 0:
			stdout, stderr = Popen('su-to-root -X -c /etc/init.d/tor start', shell=True, stdout=PIPE).communicate()
			if stderr:
				print (red("Can't start proxy"))
				exit(1)
		if self.check_socat() == 0:
			stdout, stderr = Popen('su-to-root -X -c socat TCP4-LISTEN:8080,fork SOCKS4a:127.0.0.1:'+self.t+',socksport=9050 &', shell=True, stdout=PIPE).communicate()
			if stderr:
				print (red("Can't start proxy"))
				exit(1)

        
	def check_tools(self):
		#Check Proxychains and Socat
		if not os.path.exists('/usr/bin/proxychains') or not os.path.exists('/usr/bin/socat'):
			print (red("Please, install "+green("proxychains ")+red("and ")+green("socat.")))
			exit(1)
		
		#Check the tools
		tools = ['nmap', 'whatweb', 'skipfish', 'wpscan', 'sqlmap', 'joomscan', 'nikto', 'htexploit']
		for i in tools:
			needle = "/usr/bin/"+i
			if os.path.exists(needle):
				self.dc[i] = 1
			else:
				self.dc[i] = 0
		
	#Run tools		
	def run_command(self, command):
		test = Popen(command, stdout=subprocess.PIPE, shell=True)
		stdout, stderr = test.communicate()
		if stderr:
			print (red("Error, check parameters"))
		else:
			print (stdout)


	#Take data for LogFile
	def pendate(self):
		return datetime.datetime.now().strftime("-%m-%d-%Y_%H-%M")
	
	def sqlmap(self):
		if self.par:
			return 'sudo proxychains sqlmap --url=' + self.t + ' ' + self.par + ' | tee ./' + self.t + self.pendate() + '.txt'
		else:
			return 'sudo proxychains sqlmap --wizard | tee ./' + self.t + self.pendate() + '.txt'

	def nmap(self):
		if self.par:
			return 'sudo proxychains nmap -v ' + self.par + ' ' + self.t + ' | tee ./' + self.t + self.pendate() + '.txt'
		else:
			return 'sudo proxychains nmap -sV -O -P0 -p 21,22,25,53,80,135,139,443,445 ' + self.t + ' | tee ./' + self.t + self.pendate() + '.txt'

	def whatweb(self):
		if self.par:
			return 'whatweb -v ' + self.t + ' ' + self.par + ' | tee ./nmap' + t + self.pendate() + '.txt'
		else:
			return 'whatweb -v ' + self.t + ' | tee ./nmap' + self.t+ self.pendate() + '.txt'
	
	def slowloris(self):
		if self.par:
			return 'perl /opt/backbox/penmode/slowloris.pl -dns ' + self.t + ' ' + self.param
		else:
			return 'perl /opt/backbox/penmode/slowloris.pl -dns ' + self.t + ' -port 8080 -timeout 500 -num 500'
		
	def htexploit(self):
		if self.par:
			return 'sudo proxychains htexploit -u ' + self.t + ' ' + self.par
		else:
			return 'sudo proxychains htexploit -u ' + self.t + ' -o -w --verbose 3'
		
	def skipfish(self):
		if self.par:
			return 'sudo proxychains skipfish ' + self.par + ' ' + self.t
		else:
			return 'sudo proxychains skipfish -o ' + os.path.dirname(os.path.realpath(sys.argv[0]))+'/log/' + ' ' + self.t
	
	def wpscan(self):
		if self.par:
			return 'sudo proxychains wpscan --url' + self.t + ' ' + self.par + ' | tee ./wpscan' + self.pendate() + '.txt'
		else:
			return 'sudo proxychains wpscan --url' + self.t + ' | tee ./wpscan' + self.pendate() + '.txt'
		
	def joomscan(self):
		return 'joomscan -u' + self.t + ' -x 127.0.0.1:8080 | tee ./joomscan' + self.pendate() + '.txt'
		
	def nikto(self):
		return 'nikto -h 127.0.0.1:8080 | tee ./nikto' + self.pendate() + '.txt'
