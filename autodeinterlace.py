#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  h2rgDeinterlace.py
#  
#  Copyright 2013 Luke Schmidt, <lschmidt@mro.nmt.edu>
#  Copyright 2014 Jesse Crawford, <jcrawford@cs.nmt.edu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  ****Remember, indexes are switched, x axis is second index in pyfits****
#
#  suggestions for use:
#    Consider a cron job, e.g.:
#      */2 *  *   *   *     nice -10 /home/nessi/autodeinterlace.py
#    Also set an alias, e.g.:
#      alias newimages="/home/nessi/autodeinterlace.py"

from argparse import ArgumentParser
import glob
from datetime import datetime
import os
from subprocess import call

import pyfits as pf
import numpy as np

NEWORDER = []

for i in range(32):
	NEWORDER = NEWORDER + range(i, 2048, 32)

def readfile(fname):
	hdu = pf.open(fname, do_not_scale_image_data=True, mode='update')
	return hdu

def deinterlace(hdu):
	try:
		frames = hdu[0].header['NAXIS3']
	except KeyError:
		frames = 1
	#shape = (header['NAXIS2'], header['NAXIS1'])
	#data1 = np.zeros((frames, shape[0], shape[1]))

	if frames > 1:
		for f in range(frames):
			hdu[0].data[f] = hdu[0].data[f][:][:,NEWORDER]
	else:
		hdu[0].data = hdu[0].data[:][:,NEWORDER]
		
	return hdu
		
def savefile(hdu):
	hdu.flush()

def ensureDirectory(path):
	d = os.path.dirname(path)
	if not os.path.exists(d):
		os.makedirs(d)

def moveFile(f):
	dateString = datetime.now().strftime("%Y-%m-%d")
	ensureDirectory("/home/nessi/Images/{}/".format(dateString))
	newName = "/home/nessi/Images/{}/{}".format(dateString, os.path.basename(os.path.normpath(f)))
	os.rename(f, newName)
	return newName

# Danger will robinson!
# This will clobber the existing second in memory, it should be
# written out to disk first!
def subtract(first, second, original):
	try:
		frames = second[0].header['NAXIS3']
	except KeyError:
		frames = 1
	
	if frames > 1:
		for f in range(frames):
			for x in range(2048):
				for y in range(2048):
					second[0].data[y][x] = second[0].data[f][y][x] - first[0].data[y][x]
	else:
		for x in range(2048):
			for y in range(2048):
				second[0].data[y][x] = second[0].data[y][x] - first[0].data[y][x]
	dateString = datetime.now().strftime("%Y-%m-%d")
	oname = os.path.basename(os.path.normpath(f))
	second.writeto("/home/nessi/Images/{}/subt-{}".format(dateString, oname)) 

def process(f, firstImage):
	print "Deinterlacing {}...".format(f)
	hdu = readfile(f)
	hdu = deinterlace(hdu)
	savefile(hdu)
	if(firstImage):
		subtract(firstImage, hdu, f)
	return moveFile(f)
	

if __name__== '__main__':
	parser = ArgumentParser()
	parser.add_argument('--openwith', nargs=1)
	parser.add_argument('-s', '--subtract', action='store', help="Subtract given frame from each new frame.")
	args = parser.parse_args()

	if(args.subtract != None):
		firstImage = readfile(f)
	else:
		firstImage = None

	files = glob.glob("/home/nessi/NewImages/*")
	for f in files:
		new_f = process(f)
		if args.openwith and (not os.fork()):
			call([args.openwith[0], new_f])
