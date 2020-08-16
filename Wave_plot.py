from math import *
import numpy as np
from matplotlib.figure import Figure
from math import *

import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os

class Draw_Server():
    RoughEN = False
    def __init__(self,DATA_Center,dpi=100,size=(6.4,4.8)):
        #self.FIG = Figure(figsize=size, dpi=dpi)
        #self.FIG.set_tight_layout(tight = True)
        self.FIG = plt.figure(figsize=size, dpi=dpi)
        self.FIG.set_tight_layout(tight = True)
        self.i = 0
        self.Data_Center = DATA_Center
        self.enShot = False
        #self.DSP = DSP
        self.diff_y_max = 0
        self.saving = False
        self.Number2Save = 0
        self.Name = 'Default'
        self.Counter = 0

    def Set_Object(self,FIG):
        self.FIG = FIG

    def reset_axis(self):
        self.diff_y_max = 0
        self.Data_Center.DSP.update_envlope()

    def test(self):
        self.FIG.clf()
        # fig = self.FIG.add_subplot(111)
        fig = plt.subplot(211)
        #fig.grid()
        x = np.arange(1024)
        x = x / 512
        x = x * pi
        y = np.sin(x + self.i / 128)
        self.i = self.i + 1
        #fig.clear()
        #fig.grid()
        plt.plot(x, y)
        plt.subplot(212)
        plt.plot(x,y)

    def Plot(self,en_rough_data,en_diff_data):
        self.FIG.clf()
        data = self.Data_Center.get_pdata()
        self.Data_Center.DSP.push_data(data)
        N = len(data)
        x = np.arange(N)
        x = x * 100 / N
        if en_diff_data.get():
            fig1 = self.FIG.add_subplot(211)
            fig1.grid()
            fig1.plot(x,data)

            fig2 = self.FIG.add_subplot(212)
            fig2.grid()
            shot,Max,Min = self.Data_Center.DSP.get_diff(self.enShot)

            fig2.plot(x,shot)
            #fig2.plot(x,Max)
            #fig2.plot(x,Min)
            fig2.set_xlim((0,100))
            #fig2.set_ylim((0,1))
            #fig2.set_ylim([-self.diff_y_max,self.diff_y_max])
            fig2.set_xlabel('$T/ns$')
            fig2.set_ylabel('Probability')


        else:
            fig1 = self.FIG.add_subplot(111)
            fig1.grid()
            fig1.plot(x,data)

        if en_rough_data.get():
            fig1.plot(x,self.Data_Center.get_rdata())

        fig1.set_xlim((0,100))
        #fig1.set_ylim((0,1))
        fig1.set_xlabel('T/ns')
        fig1.set_ylabel('Probability')
        if self.enShot:
            fig1.plot(x,self.Data_Center.DSP.get_shot())

        return self.Save_Stream()


    def Shot(self):
        self.enShot = True
        self.Data_Center.DSP.shot()

    def Clear(self):
        self.enShot = False
        self.Data_Center.DSP.update_envlope()

    def Save_Stream(self):
        self.Counter += 1
        if self.Counter == 10:
            self.Counter = 0
            if self.Number2Save > 0:
                self.Save_All(self.Name + '_' + str(self.Number2Save))
                self.Number2Save -= 1
        if self.Number2Save == 0:
            self.saving = False
            return False
        else:
            return True

    def Save_All(self,Name,Number=1):
        if Number == 1:
            try:
                #self.FIG.savefig(Name +'.png')
                if self.enShot:
                    np.savetxt(Name + '_S.txt',self.Data_Center.DSP.get_shot())
                    os.system('scp ' + Name + '_S.txt' + ' alfred@192.168.0.185:/home/alfred/experiment_data/VNA/')
                self.Data_Center.DSP.Save_All(Name)
            except:
                return False
            else:
                return True
        else:
            self.Number2Save = Number
            self.Name = Name
            self.saving = True