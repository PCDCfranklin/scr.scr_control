#!/usr/bin/env python

from scr_control.srv import *
import rospy
import socket
import time
import sys
import os

class ColorSensorServer():

	'''
	INIT FUNCTIONS
	'''

	def __init__(self):
		self.address = self.read_config()
		self.COS_server_init()

	def read_config(self):

		config = open(os.path.join(os.path.dirname(__file__), 'COS_conf.txt'))
		line = config.readline()
		line = line.rstrip()
		config.close()

		return line

	def establish_connection(self):
		port = 5005
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.address, port))
		except:
			print("Connection refused on " + self.address)
			
		return s

	'''
	COMMAND HANDLERS
	'''

	def handle_readAll(self, req):

		COS_reader = os.path.join(os.path.dirname(__file__), "SCR_COS_read.py")
		data = os.popen('python3 ' + COS_reader + ' ' + self.address + " 5005").read()

		
		data = data.replace('[', '')
		data = data.replace(']', '')
		data = data.replace("'", '')
		sensors_list = data.split(',')
		data_list, step = [], 0

		for i in range(len(sensors_list)):
			if sensors_list[i] != " ":
				sensor_data = sensors_list[i].split()
				step = max(len(sensor_data), step)
				for j in sensor_data:
					data_list.append(int(j))


		return COSReadAllResponse(step, data_list)

	def handle_readOne(self, req):
		num = str(req.num).zfill(3)

		s = self.establish_connection()
		
		s.send('CS_Read'+num)
		data = s.recv(23)

		s.shutdown(socket.SHUT_RDWR)
		s.close()

		data = str(data.decode())
		data = data.translate(None,"[]'")
		# data = data.split(', ')
		data = filter(None, data)

		data_list = []

		for line in data:
			line = line.split(' ')
			for item in line:
				try:
					item = int(item)
					data_list.append(item)
				except:
					pass
					
		resp = COSReadOneResponse()
		resp.data = data_list

		return resp

	def handle_inteTime(self, req):
		num = min(max(req.num, 1), 250)

		s = self.establish_connection()
		
		s.send('CS_Inte'+num)
		a = s.recv(1024)

		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
	'''
	HELPER FUNCTIONS
	'''

	def COS_server_init(self):
		rospy.init_node("COS_server")

		readAll_service = rospy.Service(
			"read_all",
			COSReadAll,
			self.handle_readAll)

		readOne_service = rospy.Service(
			"read",
			COSReadOne,
			self.handle_readOne)

		inteTime_service = rospy.Service(
			"inte_time",
			COSInteTime,
			self.handle_inteTime)

		print("Color sensor server ready")
		rospy.spin()

if (__name__ == "__main__"):
	ColorSensorServer()
