import tkinter as tk
import requests
import concurrent.futures
import numpy as np
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties
from collections import Counter
from bs4 import BeautifulSoup
from tkinter import ttk
if __name__ == '__main__':
    matplotlib.use('Agg')
    def analyzecontrol():
        def findurl(time):
            url = 'https://www.etax.nat.gov.tw/etw-main/web/ETW183W1/'
            html = requests.get(url).content.decode('utf-8')
            sp = BeautifulSoup(html,'html.parser')
            links = sp.find_all('a')
            for l in links:
                if(l.string == (time + '期統一發票特別獎及特獎中獎清冊')):
                    return 'https://www.etax.nat.gov.tw'+ l.get('href')
    
        def timeinterval(startyear,startmonth,endyear,endmonth):
            time_interval = []
            start = int(startyear)
            end = int(endyear)
            startmonth = int(startmonth[0:2])
            endmonth = int(endmonth[0:2])
            if end < start:
                startyear = end
                endyear = start            
            for y in range(int(startyear),int(endyear)+1):
                if y < int(endyear):
                    for m in range(startmonth, 13, 2):
                        time = str(y) + '年' + str(m).zfill(2) + '-' + str(m+1).zfill(2) + '月'
                        time_interval.append(time)
                else:
                    for m in range(startmonth, endmonth + 1, 2):
                        time = str(y) + '年' + str(m).zfill(2) + '-' + str(m+1).zfill(2) + '月'
                        time_interval.append(time)
                startmonth = 1
            return time_interval
        def getdata(url):
            if url != None:
                item_1000 = {}
                item_200 = {}
                html = requests.get(url).content.decode('utf-8')
                sp = BeautifulSoup(html,'html.parser')
                table_1000 = sp.find('table',{'id':'fbonly'})
                table_200 = sp.find('table',{'id':'fbonly_200'})
                td_1000 = table_1000.find_all('td',{'headers':'tranItem'})
                td_200 = table_200.find_all('td',{'headers':'tranItem2'})
                for i in td_1000:
                    item = re.split('[個組項份瓶盒 共及等計元*，,、0-9]',i.text)
                    for j in item:
                        if j !='' and j!='杯':
                            if(j in item_1000):
                                item_1000[j] += 1
                            else:
                                item_1000[j] = 1
                for i in td_200:
                    item = re.split('[個組項份瓶盒 共及等計元*，,、0-9]',i.text)
                    for j in item:
                        if j!='' and j!='杯':
                            if(j in item_200):
                                item_200[j] += 1
                            else:
                                item_200[j] = 1
                return item_1000,item_200
            else :
                return None,None
        def get_cities(url):
            if url != None:
                city_200 = {}
                city_1000 = {}
                html = requests.get(url).content.decode('utf-8')
                sp = BeautifulSoup(html,'html.parser')
                table_1000 = sp.find('table',{'id':'fbonly'})
                table_200 = sp.find('table',{'id':'fbonly_200'})
                td_1000 = table_1000.find_all('td',{'headers':'companyAddress'})
                td_200 = table_200.find_all('td',{'headers':'companyAddress2'})
                for i in td_1000:
                    item = re.findall(r'.+市|.+縣',i.text)
                    for j in item:
                        if(j in city_1000):
                            city_1000[j] += 1
                        else:
                            city_1000[j] = 1 
                for i in td_200:
                    item = re.findall(r'.+市|.+縣',i.text)
                    for j in item:
                        if(j in city_200):
                            city_200[j] += 1
                        else:
                            city_200[j] = 1 
                return city_1000,city_200
            else :
                return None,None
        def drawbars(num,data,date):
            font = FontProperties(fname='C:\\Windows\\Fonts\\mingliu.ttc', size=16)
            names = list(data.keys())
            values = list(data.values())
            fig = plt.figure(figsize=(20,4))
            plt.ylim(0, max(data.values()))
            plt.xticks(np.arange(len(names)),names,rotation=90,fontproperties=font)
            plt.title(date[0] + '到' + date[-1] + ' ' + str(num)+'萬中獎清冊' + '項目(共'+str(len(names))+'種)',fontproperties=font)
            plt.xlabel('項目(共'+str(len(names))+'種)',fontproperties=font)
            plt.ylabel('數量',fontproperties=font)
            plt.bar(names,values)
            return fig
        def drawcities(num,data,date):
            font = FontProperties(fname='C:\\Windows\\Fonts\\mingliu.ttc', size=16)
            names = list(data.keys())
            values = list(data.values())
            fig = plt.figure(figsize=(20,4))
            plt.ylim(0, max(data.values()))
            plt.xticks(np.arange(len(names)),names,rotation=90,fontproperties=font)
            plt.title(date[0] + '到' + date[-1] + ' ' + str(num)+'萬縣市統計' + '(共'+str(len(names))+'個縣市)',fontproperties=font)
            plt.xlabel('(共'+str(len(names))+'個縣市)',fontproperties=font)
            plt.ylabel('數量',fontproperties=font)
            plt.bar(names,values)
            return fig
        def crawler(time_interval):
            urls = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_url = [executor.submit(findurl, time) for time in time_interval]
                for future in concurrent.futures.as_completed(future_to_url):
                    urls.append(future.result())
            return urls
        def data_threadpool(urls):
            item_1000 = {}
            item_200 = {} 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_data = [executor.submit(getdata, url) for url in urls]
                for future in concurrent.futures.as_completed(future_to_data):
                    dic1000,dic200 = future.result()
                    item_1000 = dict(Counter(item_1000)+Counter(dic1000))
                    item_200 = dict(Counter(item_200)+Counter(dic200))
            return item_1000,item_200
        def cities_threadpool(urls):
            city_1000 = {}
            city_200 = {} 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_data = [executor.submit(get_cities, url) for url in urls]
                for future in concurrent.futures.as_completed(future_to_data):
                    dic1000,dic200 = future.result()
                    city_1000 = dict(Counter(city_1000)+Counter(dic1000))
                    city_200 = dict(Counter(city_200)+Counter(dic200))
            return city_1000,city_200
        def analyze():
            time_interval = timeinterval(startyear.get(),startmonth.get(),endyear.get(),endmonth.get())                
            urls = crawler(time_interval)
            d1000,d200 = data_threadpool(urls)
            fig = drawbars(1000,d1000,time_interval)
            fig2 = drawbars(200,d200,time_interval)
            root = tk.Tk()
            root2 = tk.Tk()
            canvas = FigureCanvasTkAgg(fig, root)
            canvas2 = FigureCanvasTkAgg(fig2, root2)
            canvas.draw()
            canvas2.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            root.mainloop()
            root2.mainloop()
            try:
                root.destroy()
                root2.destroy()
            except:
                pass
        def analyze_city():
            time_interval = timeinterval(startyear.get(),startmonth.get(),endyear.get(),endmonth.get())
            urls = crawler(time_interval)
            d1000,d200 = cities_threadpool(urls)
            fig = drawcities(1000,d1000,time_interval)
            fig2 = drawcities(200,d200,time_interval)
            root = tk.Tk()
            root2 = tk.Tk()
            canvas = FigureCanvasTkAgg(fig, root)
            canvas2 = FigureCanvasTkAgg(fig2, root2)
            canvas.draw()
            canvas2.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            root.mainloop()
            root2.mainloop()
        root = tk.Tk()
        root.title('Analyze window')
        tk.Label(root,text = '開始年').grid(column=0, row=0)
        startyear = tk.ttk.Combobox(root,width = 6,value= [i for i in range(102,109)],state='readonly')
        startyear.grid(column = 1,row = 0)
        tk.Label(root,text = '月').grid(column=2, row=0)
        startmonth = tk.ttk.Combobox(root,width = 7,value = [str(i).zfill(2) + '-' + str(i+1).zfill(2) + '月' for i in range(1,13,2)],state='readonly')
        startmonth.grid(column = 3,row = 0)
        tk.Label(root,text = '結束年').grid(column=0, row=2)
        endyear = tk.ttk.Combobox(root,width = 6,value = [i for i in range(102,109)],state='readonly')
        endyear.grid(column = 1,row = 2)
        tk.Label(root,text = '月').grid(column=2, row=2)
        endmonth = tk.ttk.Combobox(root,width = 7,value = [str(i).zfill(2) + '-' + str(i+1).zfill(2) + '月' for i in range(1,13,2)],state='readonly')
        endmonth.grid(column = 3,row = 2)
        ana = tk.Button(root,text = '商品分析',command = analyze)
        city = tk.Button(root,text = '縣市分析',command = analyze_city)
        ana.grid(column = 0,row = 3)
        city.grid(column = 3, row = 3)
        tk.Button(root,text = '結束',command = root.destroy).grid(column = 1,row = 4)
    root = tk.Tk()
    menu = tk.Menu(root)
    testmenu = tk.Menu(menu)
    menu.add_cascade(label = 'Menu',menu = testmenu)
    testmenu.add_command(label = 'Analyze',command = analyzecontrol)
    testmenu.add_separator()
    testmenu.add_command(label = 'Exit',command = root.destroy)
    root.config(menu= menu)
    root.mainloop()