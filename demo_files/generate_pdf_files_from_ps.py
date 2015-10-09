#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

# Christoph Riehl, f4eru <at> free.fr
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


# this script generates useful pdf files from your kicad pcb .ps output files
#
# steps to generate pdf files :
#   1) install 3 necessary packets with the following command : sudo apt-get install texlive-extra-utils pdftk texlive
#   2) make shure your PCB work folder contains the directories /output and /output/tmp
#   3) adapt file name and paper size a few lines down here to suit your PCB
#   4) open your PCB file, click file>trace
#   5) select "postscript", put "output/tmp/" as folder name, select all layers, select "real size" for "drill marking" etc....
#     (these settings can be saved with the file)
#   6) click "trace" : all the .ps files get generated
#   7) execute this script with the command "./generate_pdf_files_from_ps.py"
#      (you may need to allow the file to be executable with the command "chmod +x generate_pdf_files_from_ps.py")
#   8) you can remode all files in /output/tmp
#   9) enjoy the pdf output


##############################################################################################
##############################################################################################
# user settings
# please edit here
##############################################################################################
##############################################################################################

filename = 'demo_layout-panelized'
in_dir = 'output/tmp/'
out_dir ='output/'
papersize='a3'


##############################################################################################
# libs to load
##############################################################################################

import os
import re
import subprocess
import time
import shutil


##############################################################################################
# modify the color of a .ps file.
# this is a bit hacky
##############################################################################################
def ps_change_color(filename_in, filename_out, color):
	f = open(filename_in, 'r')
	pdf = f.read()
	f.close()
	
	pdf = re.sub(r'^(1 ){3}setrgbcolor$','white setrgbcolor',pdf,0, re.MULTILINE) # preserve white color
	pdf = re.sub(r'^([0-9\.\-]+ ){3}setrgbcolor$','{:.2f} {:.2f} {:.2f} setrgbcolor'.format(color[0], color[1], color[2]),pdf,0, re.MULTILINE) # replace all others by target color
	pdf = re.sub(r'^white setrgbcolor$','1 1 1 setrgbcolor',pdf,0, re.MULTILINE) # put back white color
	
	f = open(filename_out, 'w')
	f.write(pdf)
	f.close()
	
##############################################################################################
# set the color of a .ps, convert it to pdf, and stack it over another pdf
##############################################################################################
def add_colored_ps_to_pdf(filename_in, filename_out, color):
	tmpfile = 'kicad_copy_temp'

	ps_change_color(filename_in, tmpfile+'.ps', color)

	subprocess.check_call(["ps2pdf", "-sPAPERSIZE="+papersize, tmpfile+'.ps', tmpfile+'.pdf'])

	if os.path.exists(filename_out):
		subprocess.check_call(["pdftk", filename_out, 'stamp', tmpfile+'.pdf', 'output', tmpfile+'2.pdf' ]) # stack to pdf
		shutil.copyfile(tmpfile+'2.pdf', filename_out)
		os.remove(tmpfile+'2.pdf')
	else:
		shutil.copyfile(tmpfile+'.pdf', filename_out)
	
	os.remove(tmpfile+'.pdf')
	os.remove(tmpfile+'.ps')


##############################################################################################
# generate a pdf for one side of the board.
# if the 'flip' flag is set, also generate a mirror image
##############################################################################################
def compose_one_side(filename, side, flip):
	
	side_small = side[0]

	filename_out = out_dir+filename+'-layerstack_'+side+'.pdf'
	subprocess.call(["rm", filename_out ]) # remove previous output file

##############################################################################################
##############################################################################################
# colors and layer ordering can be modified here
# colors need to be expressed in numeric RGB format
##############################################################################################
##############################################################################################
	add_colored_ps_to_pdf(in_dir+filename+'-'+side_small+'_Mask'+'.ps',    filename_out, [0.95, 0.95, 0.95])       # Mask
	add_colored_ps_to_pdf(in_dir+filename+'-'+side_small+'_Cu'+'.ps',         filename_out, [0.6, 0.6, 1.0])       # copper
	add_colored_ps_to_pdf(in_dir+filename+'-'+side_small+'_Paste'+'.ps',   filename_out, [0.0, 0.0, 1.0])       # Paste
	add_colored_ps_to_pdf(in_dir+filename+'-'+side_small+'_SilkS'+'.ps',   filename_out, [1.0, 0.0, 0.0])       # Silksreen
	add_colored_ps_to_pdf(in_dir+filename+'-'+'Edge_Cuts'+'.ps',   filename_out, [0.0, 0.0, 0.0])
	add_colored_ps_to_pdf(in_dir+filename+'-'+'Eco2_User'+'.ps',   filename_out, [1.0, 0.6, 0.6])
	add_colored_ps_to_pdf(in_dir+filename+'-'+'Dwgs_User'+'.ps',   filename_out, [0.0, 0.0, 0.0])
	#	add_colored_ps_to_pdf(in_dir+filename+'-'+'Cmts_User'+'.ps',   filename_out, [0.0, 0.0, 0.0])

	if flip:
		subprocess.call(["pdfflip", '--outfile' ,out_dir  ,filename_out ]) # flip output file




##############################################################################################
# generate a pdf for one side of the board.
# This variant has a modified stackup, so it generates a pdf ready to print on film for etching
# if the 'flip' flag is set, also generate a mirror image
##############################################################################################
def compose_one_side_copper_film_to_print(filename, side, flip):
	
	side_small = side[0]

	filename_out = out_dir+filename+'-copperfilm_'+side+'.pdf'
	subprocess.call(["rm", filename_out ]) # remove previous output file

##############################################################################################
# layer ordering can be modified here
##############################################################################################
	add_colored_ps_to_pdf(in_dir+filename+'-'+side_small+'_Cu.ps',         filename_out, [0.0, 0.0, 0.0])       # copper
	add_colored_ps_to_pdf(in_dir+filename+'-'+'Edge_Cuts'+'.ps',   filename_out, [0.0, 0.0, 0.0])

	if flip:
		subprocess.call(["pdfflip", '--outfile' ,out_dir  ,filename_out ]) # flip output file



##############################################################################################
##############################################################################################
# this can be adapted if other files are needed
##############################################################################################
##############################################################################################
compose_one_side(filename, 'Front',0)
compose_one_side(filename, 'Back',1)
compose_one_side_copper_film_to_print(filename, 'Front',0)
compose_one_side_copper_film_to_print(filename, 'Back',1)

