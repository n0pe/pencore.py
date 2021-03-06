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
	print ("\nUsage: sudo ./penmode.py [tool] -p [parameters] -t [host]\n")
	print ("Split parameters with comma, for example: \n\n ./penmode.py nmap -p -sS,-p80 -t 127.0.0.1\n")
	exit(1)
	
def check_root():
	if os.getuid() != 0:
		return 0
	else:
		return 1

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
		
		#Log Dir
		self.logdir = '/var/log/penmode/'
		
		#Target
		self.url = None
		self.t = None
		
		#Dictionary (the tools)
		self.dc = {}
		
		#Parameters
		self.par = None
		
		#Check tools
		self.check_tools()
		
		#Is GUI?
		self.isgui = 0
	
	def set_target(self,target):
		self.url = target
		#Settings and configuration
		self.settings()
		
	def get_target(self):
		return self.t
	
	def set_gui(self,gui):
		self.isgui = gui
	
	#For GUI Parameters
	def set_params(self,params):
		self.par = params
		
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
			self.set_target(o.target)
			
		#Check for parameters
		if o.params and o.params != None:
			c = o.params.split(',')
			for a in c:
				self.par = ' '.join(c)
			
		#Check for LogFile
		elif o.output:
			self.fl = o.output
			
			
	#Check for Log Directory
	def check_logdir(self):
		if not os.path.exists(self.logdir):
			try:
				os.makedirs(self.logdir)
				print (green("Created " + self.logdir))
			except OSError as e:
				print (e)
		else:
			next
	
	def settings(self):
		
		self.check_logdir()
		
		
		#Adjust target
		if self.url[0:7] == "http://":
			self.url = self.url[-1][7:]
			
		p = subprocess.Popen('tor-resolve '+self.url+' 127.0.0.1:9050', shell=True, stdout=PIPE)
		self.t, err = p.communicate()
		self.t.rstrip('\r\n')
		
				
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
            
            
	def start_tor(self):
		stdout, stderr = Popen('/etc/init.d/tor start', shell=True, stdout=PIPE).communicate()
		if stderr:
			return 0
		else:
			return 1
			
	def start_socat(self):
		stdout, stderr = Popen('socat TCP4-LISTEN:8080,fork SOCKS4a:127.0.0.1:'+self.t+',socksport=9050 &', shell=True, stdout=PIPE).communicate()
		if stderr:
			return 0
		else:
			return 1

        
	def check_tools(self):
		#Check Proxychains and Socat
		if not os.path.exists('/usr/bin/proxychains') or not os.path.exists('/usr/bin/socat'):
			print (red("Please, install "+green("proxychains ")+red("and ")+green("socat.")))
			exit(1)
			
		#Check tor-resolve
		if not os.path.exists('/usr/bin/tor-resolve'):
			print (red("Please, install "+green("tor-resolve")+""))
		
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
			print (red(stderr))
		else:
			print (stdout)


	#Take data for LogFile
	def pendate(self):
		return datetime.datetime.now().strftime("-%m-%d-%Y_%H-%M")
		
	def log_string(self,tool):
		date = self.pendate()
		return ' | tee ' + self.logdir + tool + '-' + self.t  + date + '.txt'
	
	def sqlmap(self):
		if self.par:
			return 'proxychains sqlmap --url=' + self.t + ' ' + self.par + self.log_string('sqlmap')
		else:
			return 'proxychains sqlmap --wizard | tee ' + self.logdir + self.log_string('sqlmap')

	def nmap(self):
		if self.par:
			return 'proxychains nmap -v ' + self.par + ' ' + self.t + self.log_string('nmap')
		else:
			return 'proxychains nmap -sV -O -P0 -p 21,22,25,53,80,135,139,443,445 ' + self.t + self.log_string('nmap')

	def whatweb(self):
		if self.par:
			return 'whatweb -v ' + self.t + ' ' + self.par + self.log_string('wpscan')
		else:
			return 'whatweb -v ' + self.t + self.log_string('wpscan')
	
	def slowloris(self):
		if self.par:
			return 'perl /opt/backbox/penmode/slowloris.pl -dns ' + self.t + ' ' + self.par + self.log_string('slowloris')
		else:
			return 'perl /opt/backbox/penmode/slowloris.pl -dns ' + self.t + ' -port 8080 -timeout 500 -num 500' + self.log_string('slowloris')
		
	def htexploit(self):
		if self.par:
			return 'sproxychains htexploit -u ' + self.t + ' ' + self.par + self.log_string('htexploit')
		else:
			return 'proxychains htexploit -u ' + self.t + ' -o -w --verbose 3' + self.log_string('htexploit')
		
	def skipfish(self):
		if self.par:
			return 'proxychains skipfish ' + self.par + ' ' + self.t
		else:
			return 'proxychains skipfish -o ' + self.logdir + ' ' + self.t
	
	def wpscan(self):
		if self.par:
			return 'proxychains wpscan --url ' + self.t + ' ' + self.par + self.log_string('wpscan')
		else:
			return 'proxychains wpscan --url ' + self.t + self.log_string('wpscan')
		
	def joomscan(self):
		if self.par:
			return 'joomscan -u' + self.t + ' ' + self.par + self.log_string('joomscan')
		else:
			return 'joomscan -u' + self.t + self.log_string('joomscan')
		
	def nikto(self):
		if self.par:
			return 'nikto ' + self.par + ' ' + '-h ' + self.t + self.log_string('joomscan')
		else:
			return 'nikto -h ' + self.t + self.log_string('joomscan')
