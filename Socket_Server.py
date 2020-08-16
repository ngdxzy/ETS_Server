import socket

import numpy as np


class Data_Center:
	def __init__(self,DSP,Invert,Aver_L=1,Aver_H=10,Length=448):
		self.his_C = 0
		self.history = np.zeros((32768,1),dtype=np.uint32)
		self.Aver_L = Aver_L
		self.Aver_H = Aver_H
		self.Length = Length
		self.Slice_Average = np.zeros((self.Aver_L,self.Length),dtype=np.uint32)
		self.accumulator = np.sum(self.Slice_Average, axis=0)
		self.Ready_Data = self.accumulator.copy()
		self.Counter = 0
		self.DSP = DSP
		self.ss_opened = False
		self.Invert = Invert
		self.flag = False


	def update_coe(self):
		self.Slice_Average = np.zeros((self.Aver_L,self.Length),dtype=np.uint32)
		self.accumulator = np.sum(self.Slice_Average, axis=0)
		self.Ready_Data = self.accumulator.copy()
		self.Counter = 0

	def init_socket(self,port=60000,Buffer_Size=32768):
		self.Target = ('',port)
		self.Buffer_Size = Buffer_Size

	def connect(self):
		try:
			self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.ss.bind(self.Target)
		except:
			return False
		else:
			self.ss_opened = True
			return True

	def try_receive(self):
		if not self.ss_opened:
			return False
		self.ss.settimeout(0.02)
		try:
			data, addrRsv = self.ss.recvfrom(self.Buffer_Size)
		except:
			return False
		else:
			data = np.frombuffer(data, dtype=np.uint32)
			data = np.reshape(data,[560,10])
			data = data.T
			data = np.reshape(data,[1,5600])
			data = np.fliplr(data)
			# print(self.his_C)
			# if self.his_C == 32768:
			# 	if not self.flag:
			# 		np.savetxt('./history.txt',self.history)
			# 		print('saved!!!')
			# 		self.flag = True
			# else:
			# 	self.history[self.his_C] = data[0,100]
			# 	self.his_C += 1
			#data = data / self.Aver_L
			if self.DSP.Check_Confidence(self.Ready_Data,data):
				self.accumulator = self.accumulator - self.Slice_Average[self.Counter];
				self.Slice_Average[self.Counter] = data.copy();
				self.accumulator = self.accumulator + self.Slice_Average[self.Counter];
				self.Ready_Data = self.accumulator.copy()
				self.Ready_Data = self.Ready_Data / self.Aver_H
				self.Rough_Data = data
				self.Counter = (self.Counter + 1) % self.Aver_H
				return True
			else:
				return False

	def get_pdata(self):
		if self.Invert.get():
			return 1 - self.Ready_Data
		else:
			return np.flipud(self.Ready_Data)

	def get_rdata(self):
		if self.Invert.get():
			return 1 - self.Rough_Data
		else:
			return np.flipud(self.Rough_Data)

	def close_socket(self):
		self.ss.close()
		self.ss_opened = False