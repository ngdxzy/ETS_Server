import numpy as np
import os

class DSP:
    def __init__(self,data_checker,Invert,Thres):
        self.last_data = 0
        self.current_data = 0
        self.saving_data = 0
        self.Smith_Counter = 0
        self.diff = 0
        self.data_checker = data_checker
        self.Invert = Invert
        self.Thres = Thres
        self.INIT = False
        self.mag = 0

    def push_data(self, data):
        self.last_data = self.current_data
        self.current_data = data

        self.mag = np.max(data) -np.min(data)
        if not self.INIT:
            #self.UP = self.current_data - self.last_data
            self.UP = np.zeros(np.shape(self.current_data))
            self.DOWN = self.current_data - self.last_data
            self.INIT = True

    def get_diff(self, flag):
        if flag:
            diff =  self.current_data - self.saving_data
        else:
            diff =  self.current_data - self.last_data
        #diff = np.power(diff,2)
        m_flag = diff > self.UP
        self.UP = self.UP * (~m_flag) + diff * m_flag

        l_flag = diff < self.DOWN
        self.DOWN= self.DOWN * (~l_flag) + diff * l_flag
        return  diff,self.UP,self.DOWN


    def shot(self):
        self.saving_data = self.current_data
        self.INIT = False

    def update_envlope(self):
        self.INIT = False


    def get_shot(self):
        return self.saving_data;

    def Save_All(self, Name):
        np.savetxt(Name + '.txt', self.current_data);
        os.system('scp ' + Name + '.txt' + ' alfred@192.168.0.185:/home/alfred/experiment_data/VNA/')

    def Check_Confidence(self,Last,Current):
        if not self.data_checker.get():
            return True
        self.diff = np.sum(np.abs(Last-Current))
        try:
            if self.diff > float(self.Thres.get()):
                if self.Smith_Counter < 3:
                    self.Smith_Counter += 1
                    return False
                else:
                    return True
            else:
                self.Smith_Counter = 0
                return True
        except:
            return False

