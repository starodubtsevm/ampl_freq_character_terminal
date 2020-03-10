#!/usr/bin/env python3
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import sounddevice as sd
import sys
import queue
import numpy as np
import time

#---------------------------------------
class afc_device(object):
    ''' Класс измерителя АЧХ '''
    def __audio_callback (self,indata, outdata, frames, time, status):
        """callback функция для работы со звуковой картой"""
        if status:
            print(status, file=sys.stderr)

#--передача-потока на аудиовыход--------------------------------------------

        t = (self.start_idx + np.arange(frames)) / (sd.default.samplerate)
        t = t.reshape(-1, 1)
        data_left  = 1 * self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        data_right = 1 * self.amplitude * np.sin(2 * np.pi * self.frequency * t)

        data_stereo = np.column_stack([data_left, data_right])
        #outdata[::, self.mapping] = self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        outdata[::] = data_stereo
        self.start_idx += frames
#--прием потока с микрофоного входа-------------------------------------

        self.q.put(indata[::self.downsample, self.mapping])

    def __init__(self):
        """initialization"""
        self.Uref = 0.35
        self.downsample = 1
        self.start_idx = 0
        self.flag_start = 1
        self.start = 0
        self.x = []
        self.y = []
        self.data_left  = []
        self.data_right = []
        self.channels = [1,2]
        self.amplitude = 0.1
        self.freq_min = 150
        self.freq_max = 1500
        self.frequency = self.freq_min
        self.freq_step = 25
        self.time_conv = 1
        self.data_mean = 0
        self.samplerate = 16000
        sd.default.blocksize = 1024
        sd.default.samplerate = self.samplerate
        sd.default.channels = 2
        self.q = queue.Queue()
        self.stream = sd.Stream(device = (sd.default.device, sd.default.device),
                                    callback = self.__audio_callback)
        self.stream.start()
        self.mapping = [c - 1 for c in self.channels]
        self.figure = self.plotting(self.samplerate)
        ani = FuncAnimation(self.figure, self.update_plot,\
                                                   interval = 50, blit = True)
        plt.show()

    def calc(self,data):
        """вычисление rms сигнала"""
        self.data_left  =  data[:,1]
        self.data_right =  data[:,0]

        if self.flag_start == 1:
            self.start = time.time()
            self.flag_start = 0 

        if time.time() - self.start >= self.time_conv:
            rms_left  = np.sqrt(np.mean(np.square(self.data_left)))
            rms_right = np.sqrt(np.mean(np.square(self.data_right)))

            data_mean_left = np.mean(rms_left)
            data_mean_right = np.mean(rms_right)

            print(self.frequency,data_mean_left)
            self.x.append(self.frequency)
            self.y.append(20*np.log10(data_mean_left/data_mean_right))
            self.frequency += self.freq_step
            self.flag_start = 1
            if self.frequency > self.freq_max:
                self.plot_res()
                return 0
        return 1

    def update_plot(self,frame):
        ''' функция обновления изображения '''
        global plotdata
        global lines

        while True:
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                break

            shift = len(data)

            if self.calc(data) == 0:
                 raise SystemExit

            plotdata = np.roll(plotdata, -shift, axis=0)
            plotdata[-shift:, :] = data

        for column, line in enumerate(lines):
            line.set_ydata(plotdata[:, column])
        return lines

    def plotting(self,samplerate):
        '''функция построения анимации выходного и входного сигналов'''
        global plotdata
        global lines
        global data_mean

        length = int(250 * samplerate / (1000 * self.downsample))
        plotdata = np.zeros((length, len(self.channels)))
        fig, ax = plt.subplots()
        lines = ax.plot(plotdata)
        if len(self.channels) > 1:
            ax.legend(['channel {}'.format(c) for c in self.channels],
                loc='lower left', ncol=len(self.channels))
        ax.axis((0, len(plotdata), -1.0, 1.0))
        ax.set_xlabel('время')
        ax.set_ylabel('амплитуда, уе')
        plt.title("Входной сигнал")
        ax.yaxis.grid(True)
        ax.tick_params(bottom=True, top=False, labelbottom=True,
                right=False, left=True, labelleft=True)
        return fig

    def plot_res(self):
        ''' построение графика АЧХ'''
        fig, ax = plt.subplots()
        ax.axis((self.freq_min, self.freq_max, -50, 6))
        plt.axvspan(320, 1200, facecolor='#2ca02c', alpha=0.5)
        plt.axhspan(-50, -40, facecolor='#2ca02c', alpha=0.5)
        plt.axhspan(0, -9, facecolor='#2ca02c', alpha=0.5)
        ax.set_title("АЧХ устройства. Время замера = %d сек"\
                                                % (self.time_conv))
        ax.yaxis.grid(True)
        ax.xaxis.grid(True)
        ax.set_xlabel('частота, Hz')
        ax.set_ylabel('коэфф передачи, dB')
        plt.plot( self.x,self.y, linewidth=5, color='blue')
        self.stream.stop()
        plt.show()
        return 0


