#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-


# Copyright Lordblick, Christoph Riehl
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


# This panelizer script is a modified and simplified form of the one from https://github.com/LordBlick/kicadPanelizer
# Christoph Riehl, f4eru <at> free.fr
# this version works without a GUI.
# the project settings are stored directly in this script file, please see/edit settings a few lines down from here.

	
##############################################################################################
# libs to load
##############################################################################################

from pcbnew import LoadBoard, TEXTE_PCB as TEXTE_PCB, DIMENSION as DIMN, \
	Edge_Cuts as Cutout, wxPoint as wxPt, FromMils, FromMM, GetKicadConfigPath as cfgPath
from os import path as pt
import re


##############################################################################################
# user settings
# please edit here
##############################################################################################

# put the source file name here
fileNamePCB = 'demo_files/demo_layout.kicad_pcb'

# comment one of those, depending on which units to use
#Units=FromMils
Units=FromMM

# umber of boards in each dimension
nx = 3
ny = 2

# stepping width
step_x = 65
step_y = 142 + 2     # 2 is the router tool width

# general offset
offset_x = 0
offset_y = 0

# rotation definition
angles = [0,180] # multiple angle steps can be defined for panels with multiple orientations
center_x = 82.5
center_y = 121






##############################################################################################
# subfunctions
##############################################################################################


# listing objects in a PCB
def brdItemize(pcb):
		lsItems = []
		nullType = type(None)
		for ItemStr in ('Drawings', 'Tracks', 'Modules'):
			for idx, Item in enumerate(getattr(pcb, 'Get'+ItemStr)()):
				if type(Item)==nullType:
					raise TypeError, "Null Object Error#%i, expected %s Type…" % (idx+1, ItemStr[:-1])
				lsItems.append(Item)
		nZones = pcb.GetAreaCount()
		if nZones:
			for idx in range(nZones):
				Zone = pcb.GetArea(idx)
				if type(Zone)==nullType:
					raise TypeError, "Null Object Error#%i, expected Zone/Area Type…" % (idx+1,)
				lsItems.append(Zone)
		return lsItems

# instanciates one object list on the board, with rotation and displacement
def pcb_instanciate_one_board(pcb, lsItems, vector, angle, center):
	global boardcount
	boardcount = boardcount+1;
	
	for Item in lsItems:
		newItem = Item.Duplicate()
		pcb.Add(newItem)
		if angle:
			newItem.Rotate(center, angle*10) # kicad uses decidegrees ....
		newItem.Move(vector)
		
		# replace the marker "##PCBNUMBER##" by tha ctual number of this copy
		if type(newItem) is TEXTE_PCB:#
			text = newItem.GetText()
			text = re.sub(r'\##PCBNUMBER##',str(boardcount),text)
			newItem.SetText(text)
	
	return

# instanciates multiple object lists on the board, stepping displacements
def pcb_instanciate_multiple_boards(pcb, lsItems, nx, ny, step_vector, offset_vector, angle, center):
	if nx<1 or(ny<1):
		raise ValueError, "Columns(%i) or Rows(%i) cannot be less than 1…" % (nx, ny)
		
	for y in range(ny):
		for x in range(nx):
			vector_to_place = wxPt(x*step_vector.x + offset_vector.x, y*step_vector.y + offset_vector.y)
			pcb_instanciate_one_board(pcb, lsItems, vector_to_place, angle, center)
			
	return




##############################################################################################
# panelizing script
##############################################################################################


from pcbnew import LoadBoard, TEXTE_PCB as TEXTE_PCB, DIMENSION as DIMN, \
	Edge_Cuts as Cutout, wxPoint as wxPt, FromMils, FromMM, GetKicadConfigPath as cfgPath
from os import path as pt
import re




# generate vectors from dimensions
step_vector = wxPt(Units(step_x),Units(step_y))
offset_vector = wxPt(Units(offset_x),Units(offset_y))
center = wxPt(Units(center_x),Units(center_y))


# derived file names
fileNameSave = "%s-panelized.%s" % tuple(fileNamePCB.rsplit('.', 1))
fileNameCommonParts = "%s-panel-common.%s" % tuple(fileNamePCB.rsplit('.', 1))


# load PCB
print("Reading file: '%s'\n"% fileNamePCB)
pcb = LoadBoard(fileNamePCB)
print("\n")

# get all items
lsItems = brdItemize(pcb)

# delete original items
for Item in lsItems:
	pcb.Remove(Item)



boardcount =0; # global variable is fine here for counting boards


# instantiate boards @ different rotations
for angle in angles:
	pcb_instanciate_multiple_boards(pcb, lsItems, nx, ny, step_vector, offset_vector, angle, center)

print("Instantiate %i boards\n"% boardcount)



# try to load and add common parts
print("trying to read file: '%s'\n"% fileNameCommonParts)
try:
	pcb_common = LoadBoard(fileNameCommonParts)
	print("\n")
except:
	print("File '%s' not found, Ignoring common parts\n"% fileNameCommonParts)
	pass
else:
	# get all items
	lsItems_common = brdItemize(pcb_common)
	
	# add common parts
	
	print("Add common parts from file: '%s'\n"% fileNameCommonParts)
	pcb_instanciate_one_board(pcb, lsItems_common, wxPt(0,0), 0, wxPt(0,0))
	


# save finished panel
print("\nSave panel to file:'%s'\n"% fileNameSave)
pcb.Save(fileNameSave)







