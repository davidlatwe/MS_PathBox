# -*- coding:utf-8 -*-
'''
Created on 2017.03.23

@author: davidpower
'''

from pymel.core import *
from functools import partial
import sys
import os
import json
#sys.path.append(os.path.dirname(__file__))
import pySideTool as pst; reload(pst)


def Singleton(cls):
	instances = {}
	def Instance():
		if cls not in instances:
			instances[cls] = cls()
		return instances[cls]
	return Instance

@Singleton
class PathBox():
	"""
	"""
	def __init__(self):
		"""
		"""
		self.user_name = os.environ.get('USERNAME')
		self.proj_name = os.environ.get('PROJ')
		self.proj_root = self._workspaceRoot()
		self.maya_home = os.environ['MAYA_APP_DIR']
		self.path_home = 'data'
		self.file_proj = 'MS_pathBox_proj.json'
		self.file_path = 'MS_maya_pathBox.json'
		self.json_proj = os.altsep.join([self.maya_home, self.file_proj])
		self.dict_proj = self._json_load(self.json_proj)
		self.json_path = ''
		self.dict_path = ''
		self.ui_cust_type = '~New Type...'
		self._json_path_init()

		self.windowWidth = 0
		self.windowHeight = 0
		self.ui_colm_main = ''
		self.ui_menu_proj = ''
		self.ui_menu_user = ''
		self.ui_menu_type = ''
		self.ui_text_type = ''
		self.ui_text_path = ''
		self.ui_text_note = ''
		self.ui_butn_rmtp = ''
		self.ui_scrl_pick = ''
		self.ui_copyPaste = ''


	def _workspaceRoot(self):
		"""
		"""
		proj_root = ''

		if self.proj_name:
			import shotAssetUtils; reload(shotAssetUtils)
			shotObj = shotAssetUtils.Project(proj= self.proj_name)
			proj_root = '/'.join(shotObj.getPath().split(os.sep))
		else:
			wsPath = workspace(q= 1, rd= 1)
			self.proj_name = wsPath.split('/')[1].split('_')[-1]
			proj_root = wsPath
			if len(wsPath.split('/')) > 3:
				if wsPath.split('/')[2].lower() == 'maya':
					# 應為原 pipeline 資料樹架構
					proj_root = '/'.join(wsPath.split('/')[:3])
				else:
					# 應為豪狗 pipeline 資料樹架構
					proj_root = '/'.join(wsPath.split('/')[:2])

		return proj_root


	def _json_load(self, jsonPath):
		"""
		"""
		dictData = {}
		if os.path.isfile(jsonPath):
			try:
				with open(jsonPath) as jsonFile:
					dictData = json.load(jsonFile)
			except:
				pass

		return dictData


	def _json_save(self, jsonPath, dictData):
		"""
		"""
		with open(jsonPath, 'w') as jsonFile:
			json.dump(dictData, jsonFile, indent=4)


	def _json_path_init(self):
		"""
		"""
		self.json_path = os.altsep.join([self.proj_root, self.path_home, self.file_path])
		self.dict_path = self._json_load(self.json_path)

		#print '[MS_PathBox] : ----------------------------------------------------'
		#print '[MS_PathBox] : proj_name = ' + self.proj_name
		#print '[MS_PathBox] : proj_root = ' + self.proj_root

		# init json file
		if not self.proj_name in self.dict_proj:
			self.dict_proj[self.proj_name] = self.proj_root
			self._json_save(self.json_proj, self.dict_proj)
		if not self.dict_path or not self.user_name in self.dict_path:
			self.dict_path[self.user_name] = {self.ui_cust_type:{}}
			self._json_save(self.json_path, self.dict_path)


	def _ui_userUpdate(self):
		"""
		"""
		orig = self.ui_menu_user.getValue()
		self.ui_menu_user.clear()
		for user in self.dict_path:
			menuItem(l= user, p= self.ui_menu_user)
		if orig in self.dict_path:
			self.ui_menu_user.setValue(orig)
		else:
			self.ui_menu_user.setValue(self.user_name)


	def _ui_typeUpdate(self):
		"""
		"""
		typeList = self.dict_path[self.ui_menu_user.getValue()].keys()
		typeList.sort()
		self.ui_menu_type.clear()
		for typp in typeList:
			menuItem(l= typp, p= self.ui_menu_type)


	def uic_checkDel(self):
		"""
		"""
		result = confirmDialog(
			title= 'Confirm',
			message= 'Do Delete, are you sure?',
			button= ['Yes','No'],
			defaultButton= 'No',
			cancelButton= 'No',
			dismissString= 'No'
			)
		return True if result == 'Yes' else False


	def uic_removeProj(self, *args):
		"""
		"""
		if self.uic_checkDel():
			proj = self.ui_menu_proj.getValue()
			self.ui_menu_proj.clear()
			self.dict_proj.pop(proj, None)
			self._json_save(self.json_proj, self.dict_proj)
			for proj in self.dict_proj:
				menuItem(l= proj, p= self.ui_menu_proj)
			if self.dict_proj:
				self.uic_projChange()
			else:
				self.ui_menu_type.clear()
				self.ui_scrl_pick.clear()
				self.ui_colm_main.setEnable(False)


	def uic_removeType(self, *args):
		"""
		"""
		if self.uic_checkDel():
			typp = self.ui_menu_type.getValue()
			self.ui_menu_type.clear()
			self.dict_path[self.ui_menu_user.getValue()].pop(typp, None)
			self._json_save(self.json_path, self.dict_path)
			self._ui_typeUpdate()
			self.uic_typeChange()


	def uic_projChange(self, *args):
		"""
		"""
		self.proj_name = self.ui_menu_proj.getValue()
		self.proj_root = self.dict_proj[self.proj_name]
		self._json_path_init()
		self._ui_userUpdate()
		self._ui_typeUpdate()
		self.uic_typeChange()


	def uic_userChange(self, *args):
		"""
		"""
		self._ui_typeUpdate()
		self.uic_typeChange()


	def uic_typeChange(self, *args):
		"""
		"""
		if self.ui_menu_type.getValue() == self.ui_cust_type:
			self.ui_text_type.setEnable(True)
			self.ui_butn_rmtp.setEnable(False)
		else:
			self.ui_text_type.setEnable(False)
			self.ui_butn_rmtp.setEnable(True)
		# update pathBox
		self.ui_pathBox_make()


	def uic_addPath(self, *args):
		"""
		"""
		isNewType = False
		user = self.ui_menu_user.getValue()
		typp = self.ui_menu_type.getValue()
		path = self.ui_text_path.getText()
		note = self.ui_text_note.getText()
		if path:
			if os.path.exists(path):
				path = str(os.path.abspath(str(path).encode('string-escape')))
				path = path.replace('\\', '/')
			if typp == self.ui_cust_type:
				typp = self.ui_text_type.getText()
				if not typp:
					warning('Empty Type...')
					return None
			if not typp in self.dict_path[user]:
				isNewType = True
				self.dict_path[user][typp] = []
			self.dict_path[user][typp].insert(0, [path, note])
			self._json_save(self.json_path, self.dict_path)
			self.ui_pathBox_make()
			if isNewType:
				self._ui_typeUpdate()
				self.ui_menu_type.setValue(typp)
				self.uic_typeChange()
			self.ui_text_path.setText('')
			self.ui_text_note.setText('')
			self.ui_text_type.setText('')
		else:
			warning('Empty Path...')
			return None


	def uic_copyPath(self, pathText, *args):
		"""
		"""
		self.ui_copyPaste.clear()
		self.ui_copyPaste.setText(pathText)
		self.ui_copyPaste.selectAll()
		self.ui_copyPaste.copySelection()


	def uic_delPath(self, pathData, pathBoxData, pathBoxInst, *args):
		"""
		"""
		if self.uic_checkDel():
			user = pathBoxData[0]
			typp = pathBoxData[1]
			self.dict_path[user][typp].remove(pathData)
			self._json_save(self.json_path, self.dict_path)
			deleteUI(pathBoxInst)


	def ui_pathBox(self, pathData, pathBoxData):
		"""
		"""
		frameBaseColor = pst.hex_rgb('646464')
		BGcolor = pst.rgb_nor(frameBaseColor)
		
		pathBoxInst = columnLayout(adj= 1, p= self.ui_scrl_pick);\
			frameLy = frameLayout(lv= False, bv= False, bgc= BGcolor, cll= False, w= self.windowWidth - 25);\
				columnLayout(adj= 1);\
					rowLayout(nc= 2);\
						text(l= 'PATH: ', fn= 'smallFixedWidthFont');\
						textPath = textField(tx= pathData[0], ed= False, w= self.windowWidth - 75);\
					setParent('..');\
					rowLayout(nc= 2);\
						text(l= 'NOTE: ', fn= 'smallFixedWidthFont');\
						textNote = textField(tx= pathData[1], ed= False, w= self.windowWidth - 75);\
					setParent('..');\
					rowLayout(nc= 3, adj= 1);\
						text(l= '', h= 18);\
						btn_copy = button(l= 'copy', c= partial(self.uic_copyPath, pathData[0]), h= 18, w= 70);\
						btn_remv = button(l= 'X', c= partial(self.uic_delPath, pathData, pathBoxData, pathBoxInst), h= 18, w= 18);\
					setParent('..');\
				setParent('..');\
			setParent('..');\
			text(l= '', h= 3);\
		setParent('..');
		BGcolor = pst.rgb_hex(frameBaseColor, 10)
		pst.makePySideUI(frameLy, 'QWidget {color: #333333; background-color: %s}' % BGcolor)
		BGcolor = pst.rgb_hex(frameBaseColor, 20)
		pst.makePySideUI(textPath, 'QWidget {color: #887544; background-color: %s}' % BGcolor)
		pst.makePySideUI(textNote, 'QWidget {color: #55aaee;}')
		pst.makePySideUI(btn_copy, 'QPushButton {color: #%s; background-color: #%s}' % ('698085', '396055'))
		pst.makePySideUI(btn_remv, 'QPushButton {color: #%s; background-color: #%s}' % ('888888', '674842'))


	def ui_pathBox_make(self):
		"""
		"""
		self.ui_scrl_pick.clear()
		user = self.ui_menu_user.getValue()
		typp = self.ui_menu_type.getValue()
		pathBook = self.dict_path[user][typp]
		for pathData in pathBook:
			self.ui_pathBox(pathData, [user, typp])


	def ui_main(self):
		"""
		"""
		windowName = 'ms_pathBox_mainUI'
		self.windowWidth = 360
		self.windowHeight = 460

		if window(windowName, q= 1, ex= 1):
			deleteUI(windowName)

		window(windowName, t= self.user_name + '\'s Path Box', s= 0, mxb= 0, mnb= 0)
		self.ui_colm_main = columnLayout(adj= 1, cal= 'left')

		# input zone
		columnLayout(adj= 1)

		rowLayout(nc= 4)
		text(l= 'PROJ:', fn= 'smallFixedWidthFont')
		self.ui_menu_proj = optionMenu(w= 140, cc= self.uic_projChange)
		text(l= '', w= 1)
		iconTextButton(i= 'SP_TrashIcon.png', w= 19, h= 18, c= self.uic_removeProj)
		setParent('..')

		rowLayout(nc= 2)
		text(l= 'USER:', fn= 'smallFixedWidthFont')
		self.ui_menu_user = optionMenu(w= 140, cc= self.uic_userChange)
		setParent('..')

		rowLayout(nc= 6, adj= 6)
		text(l= 'TYPE:', fn= 'smallFixedWidthFont')
		self.ui_menu_type = optionMenu(w= 140, cc= self.uic_typeChange)
		text(l= '', w= 1)
		self.ui_butn_rmtp = iconTextButton(i= 'SP_TrashIcon.png', w= 19, h= 18, c= self.uic_removeType)
		text(l= '', w= 1)
		self.ui_text_type = textField(en= False, pht= 'Input new type...')
		setParent('..')

		rowLayout(nc= 2, adj= 2)
		text(l= 'PATH:', fn= 'smallFixedWidthFont')
		self.ui_text_path = textField(pht= 'Paste file/folder path here...')
		setParent('..')

		rowLayout(nc= 2, adj= 2)
		text(l= 'NOTE:', fn= 'smallFixedWidthFont')
		self.ui_text_note = textField(pht= 'Write something about this path...')
		setParent('..')
		text(l= '', h= 3)
		btn_addP = button(l= 'A D D     P A T H', h= 30, c= self.uic_addPath)
		pst.makePySideUI(btn_addP, 'QPushButton {color: #%s; background-color: #%s}' % ('999999', '587748'))

		setParent('..')
		text(l= '', h= 3)
		separator()
		text(l= '', h= 3)

		# pick zone
		columnLayout(adj= 1)
		self.ui_copyPaste = cmdScrollFieldExecuter(vis= 0)
		self.ui_scrl_pick = scrollLayout(h= self.windowHeight)
		setParent('..')

		# modify
		for proj in self.dict_proj:
			menuItem(l= proj, p= self.ui_menu_proj)
		self.ui_menu_proj.setValue(self.proj_name)
		self._ui_userUpdate()
		self._ui_typeUpdate()
		self.uic_typeChange()

		self.ui_pathBox_make()

		window(windowName, e= 1, w= self.windowWidth, h= self.windowHeight)
		showWindow(windowName)
