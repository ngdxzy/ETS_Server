import os
import shlex
import subprocess
import time
import tkinter as tk
import sys

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)



import DSP_funcs
import Socket_Server
import Wave_plot

Tick = 1
stat = 0  # A status value,ensure the mainloop() runs only once

stop = True

PIPE_PATH = "/tmp/ETS_Server_PIPE"

def loop(d_aver_l,d_aver_h,IP,port,dpi=100,size=(6.4,4.8),d_length=448):  # GUI
    #while True:
    color_bg = '#FFFFFF'  # Set background color
    color_text = '#000000'  # Set text color
    color_btn = '#E0E0E0'  # Set button color
    color_up = '#E0E010'  # Set button color
    def update_coe(event):  # Call this function for Bias current adjustment
        DATA.Aver_H = int(Aver_H_D.get())
        DATA.update_coe()

    def Save_Func(event):
        if DRAW.Save_All(FileName_D.get(),1):
           tk.messagebox.showinfo('Info','Saved successfully!')
        else:
           tk.messagebox.showinfo('Info','Something wrong, failed!')


    def ss_Con(event):
        if not DATA.ss_opened:
            DATA.init_socket(port=int(Port_D.get()))
            if DATA.connect():
                Port_B['text'] = 'Disconnect'
                Msg_D['text'] = 'Connected'
            else:
                Msg_D['text'] = 'Socket connection Failed!'
        else:
            DATA.close_socket()
            Port_B['text'] = 'Connect'
            User_APP()

    def SR_Func(event):
        global stop
        if not stop:
            stop = True
            StopRun_B['text'] = 'Run'
        else:
            stop = False
            StopRun_B['text'] = 'Stop'
            User_APP()

    def Reset_AXIS_Func(event): 
        DRAW.reset_axis()

    def Shot_Func(event):
        DRAW.Shot();

    def Clear_Func(event):
        DRAW.Clear();

    def User_APP():
        global stop
        if DATA.try_receive():
            flag = DRAW.Plot(en_rough_data,en_diff_data)
            canvas.draw_idle()
            #print(DSP.diff,DSP.Smith_Counter)
            if flag:
                Msg_D['text'] = 'Saving!'
            else:
                Msg_D['text'] = 'Error = ' + str(DSP.mag)
        else:
            Msg_D['text']='No Data'
            #DRAW.test()
            canvas.draw_idle()
        if not stop:
            root.after(Tick, User_APP)

    def before_close():
        #terminal.terminate()
        stop = True
        time.sleep(0.5)
        root.destroy()



    Enable_Rough = False
    root = tk.Tk()  # Define a window named root
    root.title('Nextlab AntiProbe')  # Main window title
    root.config(bg=color_bg)  # Set the background color of root window

    en_rough_data = tk.BooleanVar()
    en_diff_data = tk.BooleanVar()
    en_deconv = tk.BooleanVar()
    en_lp = tk.BooleanVar()
    en_iv = tk.BooleanVar()

    Left_Frame = tk.Frame(root, height=size[1]*dpi+180, width=size[0]*dpi, bg=color_bg)
    Left_Frame.pack(expand='yes',fill='both',side='left',padx=10,pady=10)
    #Right_Frame = tk.Frame(root, height=size[1] * dpi + 180, width = 640, bg=color_bg)
    #Right_Frame.pack(expand='no', fill='y', side='left',padx=10,pady=10)

    Draw_Frame = tk.Frame(Left_Frame, height=size[1]*dpi, width=size[0]*dpi, bg=color_bg)
    #Draw_Frame.grid(column=0, row=0, columnspan=1, rowspan=1,sticky="nsew")
    Draw_Frame.pack(expand='yes',fill='both',side='top')

    #root.update_idletasks()

    Conf_Frame = tk.Frame(Left_Frame, height = 180, width =size[0]*dpi, bg = color_bg)
    #Conf_Frame.grid(column=0, row=1, columnspan=1, rowspan=1,sticky=tk.N+tk.S+tk.E+tk.W)
    Conf_Frame.pack(expand='no',fill='y',side='bottom')

    #Term_Frame = tk.Frame(Right_Frame, height=size[1]*dpi+180, width=640, bg = color_bg)
    #Term_Frame.grid(column=1, row=0, columnspan=1, rowspan=2,sticky="e")
    #Term_Frame.pack(expand='yes',fill='both',side='top')

    #
    # logo = tk.PhotoImage(file='Nextlab.png')  # Define the picture of logo,but only supports '.png' and '.gif'
    # l_logo = tk.Label(root, image=logo, bg=color_bg)  # Set a label to show the logo picture
    # l_logo.grid(column=0, row=0, rowspan=2, columnspan=3)  # Place the Label in a right position


    FileName_L = tk.Label(Conf_Frame,text='File Name: ',bg=color_bg, fg=color_text)
    FileName_L.grid(column=0, row=2, padx = 2, pady = 2)
    FileName_D = tk.Entry(Conf_Frame, show=None, width=32, bg=color_btn, fg=color_text, exportselection=0,justify='left')
    FileName_D.grid(column=1, row=2, padx = 2, pady = 2)
    FileName_D.insert(0, './data_linux/test')

    Save_B = tk.Button(Conf_Frame, width=16, text='Save', fg=color_text, bg=color_up, relief='ridge')
    Save_B.grid(column=2, row=2, padx = 2, pady = 2)

    RefName_L = tk.Label(Conf_Frame, text='Reference File Name: ', bg=color_bg, fg=color_text)
    RefName_L.grid(column=0, row=3, padx=2, pady=2)
    RefName_D = tk.Entry(Conf_Frame, show=None, width=32, bg=color_btn, fg=color_text, exportselection=0,
                          justify='left')
    RefName_D.grid(column=1, row=3, padx=2, pady=2)
    RefName_D.insert(0, './data/Default')
    Load_B = tk.Button(Conf_Frame, width=16, text='Load Ref', fg=color_text, bg=color_up, relief='ridge')
    Load_B.grid(column=2, row=3, padx = 2, pady = 2)


    Port_L = tk.Label(Conf_Frame, text='Port Number: ', bg=color_bg, fg=color_text, justify='left')
    Port_L.grid(column=0, row=0, padx = 2, pady = 2)
    Port_D = tk.Entry(Conf_Frame, show=None, width=16, bg=color_btn, fg=color_text, exportselection=0, justify='center')
    Port_D.grid(column=1, row=0, padx = 2, pady = 2)  # Place the Label in a right position
    Port_D.insert(0, port)
    Port_B = tk.Button(Conf_Frame, width=16, text='Connect', fg=color_text, bg=color_up, relief='ridge')
    Port_B.grid(column=2, row=0, padx = 2, pady = 2)

    Aver_H_L = tk.Label(Conf_Frame, text='Higher Average Time: ', bg=color_bg, fg=color_text, justify='left')
    Aver_H_L.grid(column=0, row=1, padx = 2, pady = 2)
    Aver_H_D = tk.Entry(Conf_Frame, show=None, width=16, bg=color_btn, fg=color_text, exportselection=0, justify='center')
    Aver_H_D.grid(column=1, row=1, padx = 2, pady = 2)  # Place the Label in a right position
    Aver_H_D.insert(0, d_aver_h)
    Update_B = tk.Button(Conf_Frame, width=16, text='Update', fg=color_text, bg=color_up, relief='ridge')
    Update_B.grid(column=2, row=1, padx = 2, pady = 2)

    StopRun_B = tk.Button(Conf_Frame, width=16, text='Run', fg=color_text, bg=color_up, relief='ridge')
    StopRun_B.grid(column=7, row=3, padx = 2, pady = 2)

    Shot_B = tk.Button(Conf_Frame, width=16, text='Shot', fg=color_text, bg=color_up, relief='ridge')
    Shot_B.grid(column=7, row=0, padx = 2, pady = 2)

    Clear_B = tk.Button(Conf_Frame, width=16, text='Clear', fg=color_text, bg=color_up, relief='ridge')
    Clear_B.grid(column=7, row=1, padx = 2, pady = 2)

    Reset_AXIS_B = tk.Button(Conf_Frame, width=16, text='Reset AXIS', fg=color_text, bg=color_up, relief='ridge')
    Reset_AXIS_B.grid(column=7, row=2, padx = 2, pady = 2)


    Msg_D = tk.Label(Conf_Frame,text='NONE',bg='#E0E0E0', fg=color_text,width=32)
    Msg_D.grid(column=4, row=3, columnspan=3, padx = 2, pady = 2)  # Place the Label in a right position

    Save_B.bind('<ButtonPress-1>',Save_Func)
    Update_B.bind('<ButtonPress-1>', update_coe)
    StopRun_B.bind('<ButtonPress-1>', SR_Func)
    Port_B.bind('<ButtonPress-1>', ss_Con)
    Shot_B.bind('<ButtonPress-1>', Shot_Func)
    Clear_B.bind('<ButtonPress-1>', Clear_Func)
    Reset_AXIS_B.bind('<ButtonPress-1>', Reset_AXIS_Func)

    RoughEn = tk.Checkbutton(Conf_Frame, text="Rough Data", variable=en_rough_data, onvalue=True, offvalue=False, height=1, width=20,
                             bg=color_bg, bd=0, activebackground=color_bg)
    RoughEn.grid(column=4, row=0, columnspan=2, padx = 2, pady = 2)

    DiffEn = tk.Checkbutton(Conf_Frame, text="Diff Data", variable=en_diff_data, onvalue=True, offvalue=False, height=1, width=20,
                             bg=color_bg, bd=0, activebackground=color_bg)
    DiffEn.grid(column=4, row=1, columnspan=2, padx = 2, pady = 2)

    DeconvEn = tk.Checkbutton(Conf_Frame, text="Deconvolution", variable=en_deconv, onvalue=True, offvalue=False, height=1, width=20, bg=color_bg, bd=0, activebackground=color_bg)
    DeconvEn.grid(column=6, row=1, padx=2, pady=2)



    IVEN = tk.Checkbutton(Conf_Frame, text="Invert", variable=en_iv, onvalue=True, offvalue=False, height=1,
                          width=20, bg=color_bg, bd=0, activebackground=color_bg)
    IVEN.grid(column=6, row=0, padx=2, pady=2)

    DF_L = tk.Label(Conf_Frame, text='Threshold:', bg=color_bg, fg=color_text, justify='left')
    DF_L.grid(column=4, row=2, padx=2, pady=2)
    Thres_D = tk.Entry(Conf_Frame, show=None, width=13, bg=color_btn, fg=color_text, exportselection=0,
                          justify='center')
    Thres_D.grid(column=5, row=2, padx=2, pady=2)
    Thres_D.insert(0, '3')

    DFEN = tk.Checkbutton(Conf_Frame, text="Data Filter", variable=en_lp, onvalue=True, offvalue=False, height=1,
                          width=20, bg=color_bg, bd=0, activebackground=color_bg)
    DFEN.grid(column=6, row=2, padx=2, pady=2)

    DSP = DSP_funcs.DSP(en_lp,en_iv,Thres_D)

    DATA = Socket_Server.Data_Center(DSP,en_iv,Aver_L=d_aver_l,Aver_H=d_aver_h,Length=d_length)
    DATA.init_socket(port=port)

    DRAW = Wave_plot.Draw_Server(DATA, size=size, dpi=dpi)
    canvas = FigureCanvasTkAgg(DRAW.FIG, master=Draw_Frame)  # A tk.DrawingArea.
    canvas.get_tk_widget().pack(expand='yes',fill="both",padx = 0, pady = 0)
    DRAW.test()
    toolbar = NavigationToolbar2Tk(canvas, Draw_Frame)
    toolbar.config(background = color_bg)
    toolbar._message_label.config(background = color_bg)
    for button in toolbar.winfo_children():
        button.config(background = color_bg)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1,padx = 0, pady = 0)


    #if not os.path.exists(PIPE_PATH):
    #   os.mkfifo(PIPE_PATH)


    #wid = Term_Frame.winfo_id()
    #args = shlex.split("xterm -into %d -geometry 200x100"  % (wid))
    #terminal = subprocess.Popen(args)

    global stat
    if stat == 0:  # Ensure the mainloop runs only once
        root.after(Tick, User_APP)
        root.protocol('WM_DELETE_WINDOW',lambda: sys.exit(0))
        #print(root.winfo_width())
        #root.update_idletasks()
        #root.bind('<Configure>',update_size)
        #root.resizable(False,False)

        root.mainloop()  # Run the mainloop()
        stat = 1  # Change the value to '1' so the mainloop() would not run again.


if __name__ == '__main__':
    try:
        loop(d_aver_l=440,d_aver_h=50,d_length=5600,IP='',port=60000,size=(7.2 ,4.8))
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
