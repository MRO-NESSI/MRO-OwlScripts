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

import pyfits as pf
import numpy as np
import glob
import argparse
from datetime import datetime
import os

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

def process(f):
	print "Deinterlacing {}...".format(f)
	hdu = readfile(f)
	hdu = deinterlace(hdu)
	savefile(hdu)
	moveFile(f)
	

if __name__== '__main__':
	files = glob.glob("/home/nessi/NewImages/*")
	for f in files:
		process(f)
