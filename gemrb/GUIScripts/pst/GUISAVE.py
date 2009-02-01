# -*-python-*-
# GemRB - Infinity Engine Emulator
# Copyright (C) 2003 The GemRB Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id$


# GUISAVE.py - Save game screen from GUISAVE winpack

###################################################

import GemRB
from GUIDefines import *
from LoadScreen import *

SaveWindow = None
SaveDetailWindow = None
OptionsWindow = None
GameCount = 0
ScrollBar = 0


def OpenSaveWindow ():
	global SaveWindow, OptionsWindow, GameCount, ScrollBar

	if SaveWindow:
		GemRB.HideGUI ()

		if SaveDetailWindow: OpenSaveDetailWindow ()
		
		if SaveWindow:
			SaveWindow.Unload ()
		SaveWindow = None
		# FIXME: LOAD GUIOPT?
		GemRB.SetVar ("OtherWindow", OptionsWindow.ID)

		GemRB.UnhideGUI ()
		return

	GemRB.HideGUI ()
	GemRB.LoadWindowPack ("GUISAVE", 640, 480)
	SaveWindow = Window = GemRB.LoadWindowObject (0)
	OptionsWindow = GemRB.GetVar ("OtherWindow")
	GemRB.SetVar ("OtherWindow", SaveWindow.ID)


	# Cancel button
	CancelButton = Window.GetControl (46)
	CancelButton.SetText (4196)
	CancelButton.SetEvent (IE_GUI_BUTTON_ON_PRESS, "CancelPress")
	GemRB.SetVar ("SaveIdx", 0)

	for i in range (4):
		Button = Window.GetControl (14 + i)
		Button.SetText (28645)
		Button.SetEvent (IE_GUI_BUTTON_ON_PRESS, "SaveGamePress")
		Button.SetState (IE_GUI_BUTTON_DISABLED)
		Button.SetVarAssoc ("SaveIdx", i)

		Button = Window.GetControl (18 + i)
		Button.SetText (28640)
		Button.SetEvent (IE_GUI_BUTTON_ON_PRESS, "DeleteGamePress")
		Button.SetState (IE_GUI_BUTTON_DISABLED)
		Button.SetVarAssoc ("SaveIdx", i)

		# area previews
		Button = Window.GetControl (1 + i)
		Button.SetFlags (IE_GUI_BUTTON_NO_IMAGE|IE_GUI_BUTTON_PICTURE, OP_SET)

		# PC portraits
		for j in range (6):
			Button = Window.GetControl (22 + i*6 + j)
			Button.SetFlags (IE_GUI_BUTTON_NO_IMAGE|IE_GUI_BUTTON_PICTURE, OP_SET)

	ScrollBar = Window.GetControl(13)
	ScrollBar.SetEvent(IE_GUI_SCROLLBAR_ON_CHANGE, "ScrollBarPress")
	GameCount = GemRB.GetSaveGameCount () + 1 #one more for the 'new game'
	TopIndex = max (0, GameCount - 4)

	GemRB.SetVar ("TopIndex",TopIndex)
	ScrollBar.SetVarAssoc ("TopIndex", GameCount)
	ScrollBarPress ()

	GemRB.UnhideGUI ()


def ScrollBarPress():
	Window = SaveWindow
	# draw load game portraits
	Pos = GemRB.GetVar ("TopIndex")
	for i in range (4):
		ActPos = Pos + i

		Button1 = Window.GetControl (14 + i)
		Button2 = Window.GetControl (18 + i)
		if ActPos < GameCount:
			Button1.SetState(IE_GUI_BUTTON_ENABLED)
			Button2.SetState(IE_GUI_BUTTON_ENABLED)
		else:
			Button1.SetState(IE_GUI_BUTTON_DISABLED)
			Button2.SetState(IE_GUI_BUTTON_DISABLED)

		if ActPos < GameCount - 1:
			Slotname = GemRB.GetSaveGameAttrib (0, ActPos)
			Slottime = GemRB.GetSaveGameAttrib (3, ActPos)
		elif ActPos == GameCount-1:
			Slotname = 28647    # "Empty"
			Slottime = ""
		else:
			Slotname = ""
			Slottime = ""
			
		Label = Window.GetControl (0x10000004+i)
		Label.SetText (Slotname)

		Label = Window.GetControl (0x10000008 + i)
		Label.SetText (Slottime)

		Button = Window.GetControl (1 + i)
		if ActPos < GameCount - 1:
			Button.SetSaveGamePreview (ActPos)
		else:
			Button.SetPicture ("")
			
		for j in range (6):
			Button = Window.GetControl (22 + i*6 + j)
			if ActPos < GameCount - 1:
				Button.SetSaveGamePortrait (ActPos,j)
			else:
				Button.SetPicture ("")


def SaveGamePress ():
	OpenSaveDetailWindow ()


def DeleteGameConfirm():
	global GameCount

	TopIndex = GemRB.GetVar("TopIndex")
	Pos = TopIndex +GemRB.GetVar("SaveIdx")
	GemRB.DeleteSaveGame(Pos)
	if TopIndex>0:
		GemRB.SetVar("TopIndex",TopIndex-1)
	GameCount=GemRB.GetSaveGameCount()   #count of games in save folder?
	ScrollBar.SetVarAssoc("TopIndex", GameCount)
	ScrollBarPress()
	if ConfirmWindow:
		ConfirmWindow.Unload()
	SaveWindow.SetVisible(1)
	return

def DeleteGameCancel():
	if ConfirmWindow:
		ConfirmWindow.Unload()
	SaveWindow.SetVisible(1)
	return

def DeleteGamePress():
	global ConfirmWindow

	SaveWindow.SetVisible(0)
	ConfirmWindow=GemRB.LoadWindowObject(1)

	Text=ConfirmWindow.GetControl(0)
	Text.SetText(15305)

	DeleteButton=ConfirmWindow.GetControl(1)
	DeleteButton.SetText(13957)
	DeleteButton.SetEvent(IE_GUI_BUTTON_ON_PRESS, "DeleteGameConfirm")

	CancelButton=ConfirmWindow.GetControl(2)
	CancelButton.SetText(4196)
	CancelButton.SetEvent(IE_GUI_BUTTON_ON_PRESS, "DeleteGameCancel")

	ConfirmWindow.SetVisible(1)
	return
	
def CancelPress():
	OpenSaveWindow ()


def OpenSaveDetailWindow ():
	global SaveDetailWindow

	GemRB.HideGUI ()
	
	if SaveDetailWindow != None:
		if SaveDetailWindow:
			SaveDetailWindow.Unload ()
		SaveDetailWindow = None
		GemRB.SetVar ("FloatWindow", -1)
		
		GemRB.UnhideGUI ()
		return
		
	SaveDetailWindow = Window = GemRB.LoadWindowObject (1)
	GemRB.SetVar ("FloatWindow", SaveDetailWindow.ID)	


	Pos = GemRB.GetVar ("TopIndex") + GemRB.GetVar ("SaveIdx")


	# Save/Overwrite
	Button = Window.GetControl (4)
	if Pos < GameCount - 1:
		Button.SetText (28644)   # Overwrite
	else:
		Button.SetText (28645)   # Save
	Button.SetEvent (IE_GUI_BUTTON_ON_PRESS, "ConfirmedSaveGame")

	# Cancel
	Button = Window.GetControl (5)
	Button.SetText (4196)
	Button.SetEvent (IE_GUI_BUTTON_ON_PRESS, "OpenSaveDetailWindow")


	# Slot name and time
	if Pos < GameCount - 1:
		Slotname = GemRB.GetSaveGameAttrib (0, Pos)
		Slottime = GemRB.GetSaveGameAttrib (4, Pos)
	else:
		Slotname = ""
		Slottime = ""
		
	Edit = Window.GetControl (1)
	Edit.SetText (Slotname)
	Edit.SetStatus (IE_GUI_CONTROL_FOCUSED)
	Edit.SetEvent (IE_GUI_EDIT_ON_CHANGE, "CheckSaveName")
	Edit.SetEvent (IE_GUI_EDIT_ON_DONE, "ConfirmedSaveGame")

	Label = Window.GetControl (0x10000002)
	Label.SetText (Slottime)
	

	# Areapreview
	Button = Window.GetControl (0)
	GemRB.SetGamePreview (Window, Button)

	# PC portraits
	for j in range (PARTY_SIZE):
		Button = Window.GetControl (6 + j)
		Button.SetGamePortraitPreview (j)


	CheckSaveName ()
	GemRB.UnhideGUI ()
	Window.ShowModal (MODAL_SHADOW_GRAY)


# Disable Save/Overwrite button if the save slotname is empty,
#   else enable it
def CheckSaveName ():
	Window = SaveDetailWindow
	Button = Window.GetControl (4)
	Edit = Window.GetControl (1)
	Name = Edit.QueryText ()

	if Name == "":
		Button.SetState (IE_GUI_BUTTON_DISABLED)
	else:
		Button.SetState (IE_GUI_BUTTON_ENABLED)
		
	

# User entered save name and pressed save/overwrite.
# Display progress bar screen and save the game, close the save windows
def ConfirmedSaveGame ():
	Window = SaveDetailWindow
	
	Pos = GemRB.GetVar ("TopIndex") + GemRB.GetVar ("SaveIdx")
	Label = Window.GetControl (1)
	Slotname = Label.QueryText ()

	# Empty save name. We can get here if user presses Enter key
	if Slotname == "":
		return

	# We have to close floating window first
	OpenSaveDetailWindow ()
	StartLoadScreen (LS_TYPE_SAVING)
	GemRB.SaveGame (Pos, Slotname)
	CloseSaveWindow ()


# Exit either back to game or to the Start window
def CloseSaveWindow ():
	OpenSaveWindow ()
	if GemRB.GetVar ("QuitAfterSave"):
		GemRB.QuitGame ()
		GemRB.SetNextScript ("Start")
		return

	GemRB.RunEventHandler ("OpenOptionsWindow")

