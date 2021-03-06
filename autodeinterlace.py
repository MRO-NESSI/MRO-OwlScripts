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

DEFAULT_INPUT = os.path.expanduser("~/NewImages/")
DEFAULT_OUTPUT = os.path.expanduser("~/Images/%Y-%m-%d/")

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

def moveFile(f, args):
    outDir = datetime.now().strftime(args.output)
	ensureDirectory(outDir)
	newName = os.path.join(outDir, "{}".format(os.path.basename(os.path.normpath(f))))
	os.rename(f, newName)
	return newName

# Danger will robinson!
# This will clobber the existing second in memory, it should be
# written out to disk first!
def subtract(posData, posFile, negFile, args):
	negData = readfile(negFile)

	try:
		frames = posData[0].header['NAXIS3']
	except KeyError:
		frames = 1
	
	if frames > 1:
		for f in range(frames):
			for x in range(2048):
				for y in range(2048):
					posData[0].data[f][y][x] = posData[0].data[f][y][x] - negData[0].data[y][x]
	else:
		for x in range(2048):
			for y in range(2048):
				posData[0].data[y][x] = posData[0].data[y][x] - negData[0].data[y][x]
    outDir = datetime.now().strftime(DEFAULT_OUTPUT)
	pname, pexten = os.path.splitext(os.path.basename(os.path.normpath(posFile)))
	nname, nexten = os.path.splitext(os.path.basename(os.path.normpath(negFile)))
	posData.writeto(os.path.join(outDir, "{}-{}.fit".format(pname, nname)))

def process(f, args):
	print "Deinterlacing {}...".format(f)
	hdu = readfile(f)
	hdu = deinterlace(hdu)
	savefile(hdu)
	if(args.subtract):
		subtract(hdu, f, args.subtract, args)
	return moveFile(f, args)

if __name__== '__main__':
	parser = ArgumentParser()
	parser.add_argument('--openwith', nargs=1, help="Open file in selected viewer")
	parser.add_argument('-s', '--subtract', action='store', help="Subtract given frame from each new frame.")
	parser.add_argument('-i', '--input', action='store', help="Input folder.", default=DEFAULT_INPUT)
	parser.add_argument('-o', '--output', action='store', help="Output folder.", default=DEFAULT_OUTPUT)
	args = parser.parse_args()

	files = os.listdir(args.input)
	for f in files:
		fpath = os.path.join(args.input, f)
		new_f = process(fpath, args)
		if args.openwith and (not os.fork()):
			call([args.openwith[0], new_f])
