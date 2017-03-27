# -*- coding:utf-8 -*-
'''
Created on 2017.03.24

@author: davidpower
'''

from maya.OpenMayaUI import MQtUtil
from shiboken import wrapInstance
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


def rgb_hex(rgb, downGrade= None):
	def _hex(num):
		if num < 16:
			return '0' + hex(num)[2:]
		else:
			return hex(num)[2:]
	r, g, b = rgb
	if downGrade:
		r = (r - downGrade) if downGrade < r else 0
		g = (g - downGrade) if downGrade < g else 0
		b = (b - downGrade) if downGrade < b else 0
	return ('#' + _hex(r) + _hex(g) + _hex(b)).upper()


def rgb_nor(rgb, downGrade= None):
	r, g, b = rgb
	if downGrade:
		r = (r - downGrade) if downGrade < r else 0
		g = (g - downGrade) if downGrade < g else 0
		b = (b - downGrade) if downGrade < b else 0
	return [r/255.0, g/255.0, b/255.0]


def hex_rgb(strHex):

	if strHex.startswith('#'):
		strHex = strHex[1:]
	r = int(strHex[0:2], 16)
	g = int(strHex[2:4], 16)
	b = int(strHex[4:6], 16)

	return [r, g, b]


def makePySideUI(ctrlName, myStyle):

	# thanks to Nathan Horne
	ctrlName = long(MQtUtil.findControl(ctrlName))
	qObj = wrapInstance(ctrlName, QtCore.QObject)
	metaObj = qObj.metaObject()
	cls = metaObj.className()
	superCls = metaObj.superClass().className()

	if hasattr(QtGui, cls):
		base = getattr(QtGui, cls)
	elif hasattr(QtGui, superCls):
		base = getattr(QtGui, superCls)
	else:
		base = QtGui.QWidget

	uiPySide = wrapInstance(ctrlName, base)
	uiPySide.setStyleSheet(myStyle)

	return uiPySide