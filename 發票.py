import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import matplotlib.pyplot as plt  
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
import os 

font = FontProperties(fname=os.environ['WINDIR']+'\\Fonts\\kaiu.ttf', size=12)

class myGUI:
    def __init__(self, master):
        self.dates = [(year, month) for year in range(102, 108) for month in range(1, 12, 2) if (year != 107 or year == 107 and month < 10)]
        self.types = ["200萬縣市", "1000萬縣市", "200+1000萬縣市"]
        self.results = list()
        self.url = "https://www.etax.nat.gov.tw"
        self.master = master
        self.master.geometry("407x500")
        self.selectFrame = tk.LabelFrame(self.master, text="選擇", padx=15, pady=10)
        self.selectFrame.grid(row=0, column=0, padx=10)
        self.setupUI()
    def setupUI(self):
        tk.Label(self.selectFrame, text="開始日期：", width=9, height=1, pady=5, font=("微軟正黑體",16)).grid(row=0, column=0)
        tk.Label(self.selectFrame, text="結束日期：", width=9, height=1, pady=5, font=("微軟正黑體",16)).grid(row=1, column=0)
        tk.Label(self.selectFrame, text="類型：", width=9, height=1, pady=5, font=("微軟正黑體",16)).grid(row=2, column=0)
        self.startCombo = ttk.Combobox(self.selectFrame, width=19, font=("微軟正黑體", 14), justify="center", state="readonly")
        self.startCombo['values'] = [str(date[0])+"年"+str(date[1])+"月~"+str(date[0])+"年"+str(date[1]+1)+"月" for date in self.dates]
        self.startCombo.grid(row=0, column=1)
        self.startCombo.current(0)
        self.startCombo.bind("<<ComboboxSelected>>", self.startComboSelected)
        self.endCombo = ttk.Combobox(self.selectFrame, width=19, font=("微軟正黑體", 14), justify="center", state="readonly")
        self.endCombo['values'] = [str(date[0])+"年"+str(date[1])+"月~"+str(date[0])+"年"+str(date[1]+1)+"月" for date in self.dates]
        self.endCombo.grid(row=1, column=1)
        self.endCombo.current(0)
        self.typeCombo = ttk.Combobox(self.selectFrame, width=19, font=("微軟正黑體", 14), justify="center", state="readonly")
        self.typeCombo['values'] = self.types
        self.typeCombo.grid(row=2, column=1)
        self.typeCombo.current(0)
        self.selectBtn1 = tk.Button(self.selectFrame, text="選擇", width=10, font=("微軟正黑體", 14), justify="center", command=self.selectBtnHandler)
        self.selectBtn1.grid(row=3, column=1, padx=15, pady=7)
    def selectBtnHandler(self):
        
        self.results = []
        self.thread = []
        
        if (self.typeCombo.current() == 0):
            for i in range(self.startCombo.current(), self.endCombo.current() + 1):
                start = self.dates[i]
                s = str(start[0] * 100 + start[1])
                t = threading.Thread(target=self.get200, args=(s,))
                self.thread.append(t)
                t.start()
            for thread in self.thread:
                thread.join()
            print(self.results)
            
        elif (self.typeCombo.current() == 1):
            for i in range(self.startCombo.current(), self.endCombo.current() + 1):
                start = self.dates[i]
                s = str(start[0] * 100 + start[1])
                t = threading.Thread(target=self.get1000, args=(s,))
                self.thread.append(t)
                t.start()

            for thread in self.thread:
                thread.join()
                
            print(self.results)
            
        elif (self.typeCombo.current() == 2):
            for i in range(self.startCombo.current(), self.endCombo.current() + 1):
                start = self.dates[i]
                s = str(start[0] * 100 + start[1])
                t = threading.Thread(target=self.get1000, args=(s,))
                t2 = threading.Thread(target=self.get200, args=(s,))

                self.thread.append(t)
                self.thread.append(t2)

                t.start()
                t2.start()
                
            # 等待所有thread完成    

            for thread in self.thread:
                thread.join()

            print(self.results)
        print()
        self.total=dict()
        for result in self.results:
            for (key, value) in result.items():
                if self.total.get(key) is None:
                    self.total[key] = value
                else:
                    self.total[key] = self.total[key] + value

        print(self.total)
        print()
        self.bar()

    def startComboSelected(self, combobox):
        self.endCombo['values'] = [str(date[0])+"年"+str(date[1])+"月~"+str(date[0])+"年"+str(date[1]+1)+"月" for date in self.dates[self.startCombo.current():]]
        self.endCombo.current(0)

    def get1000(self, url):

        print(url)
        city_dict = dict()
        html = requests.get("https://www.etax.nat.gov.tw/etw-main/web/ETW183W3_" + url).content.decode('utf-8')
        sp = BeautifulSoup(html, 'html.parser')
        trs = sp.find("table", {'id':'fbonly'}).find("tbody").find_all("tr")
        for tr in trs:
            city = tr.find_all("td")[3].text[:3]
            if city_dict.get(city) is None:
                city_dict[city] = 1
            else:
                city_dict[city] = city_dict[city] + 1

        self.results.append(city_dict)
        
    def bar(self):
        f = plt.figure( dpi=100)
        x_value = list(self.total.keys())
        y_value = list(self.total.values())
        plt.bar(x_value,y_value, fc='#FF9901')

        l = len(x_value)
        a=list()

        for i in range(l) :
            a.append(i)

        plt.xticks(a, x_value,fontproperties=font)
        plt.title(self.types[self.typeCombo.current()],fontproperties=font)
        plt.xlabel("縣市",fontproperties=font)
        plt.ylabel("數量",fontproperties=font)
        plt.show()

        f.add_subplot(111)
        window=tk.Tk()
        window.title("BookHub")
        window.geometry(str(len(self.total) * 100) + "x400")
        canvas = FigureCanvasTkAgg(f, window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get200(self, url):
        city_dict = dict()
        html = requests.get("https://www.etax.nat.gov.tw/etw-main/web/ETW183W3_" + url).content.decode('utf-8')
        sp = BeautifulSoup(html, 'html.parser')
        trs = sp.find("table", {'id':'fbonly_200'}).find("tbody").find_all("tr")
        for tr in trs:
            city = tr.find_all("td")[3].text[:3]
            if city_dict.get(city) is None:
                city_dict[city] = 1
            else:
                city_dict[city] = city_dict[city] + 1
        self.results.append(city_dict)
        
if __name__ == "__main__":
    master = tk.Tk()
    root = myGUI(master)
    master.mainloop()