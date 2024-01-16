#-*-coding:UTF-8-*-
import tkinter as tk
import sqlite3 as sq
import sys
from tkinter import *
from tkinter import ttk

#Главное окно
root = tk.Tk()
root.geometry('796x600+400+298')
root.resizable(False,False)
root.title("Глоссарий технических требований")
#Заголовки окон
shapka='''Глоссарий поедназначен для изучения терминов по курсу <Технические средства информатизации>, 
<Информационная безопасность>, <Вычислительные системы и сети> '''
shapka1='''Выберите курс '''
#Курс № 1
def tab1():
    global en 
    global tree
    tab1 = ttk.Frame(tabControl)
    tabControl.add(tab1, text="<Технические средства информатизации>")
    frame= LabelFrame(tab1, borderwidth=8,padx=10,pady=10,relief='ridge', width=25, height = 5)
    lbl_poisk=Label(frame, text='Просмотр определения', width=25, height= 2)
    lbl_poisk.pack(anchor=NW)
    en = StringVar()
    entry = Entry(frame,textvariable=en)
    entry.pack(anchor=CENTER) 
    Search_btn = Button(frame, text='Поиск', width=8, height=1, pady=1, command=search_entr)
    Search_btn.pack()
    frame1= LabelFrame(tab1, borderwidth=8,padx=10,pady=11,relief='ridge', width=25, height=5)
    lbl_visio=Label(frame1, text='Поиск определения', width=25, height= 5)
    lbl_visio.pack(anchor=NW)
    tree=ttk.Treeview(tab1, selectmode="brows", columns = ("numb","terminus","znachenie"), show='headings')
    tree.heading("numb", text ="№", anchor=CENTER)
    tree.column("numb", stretch=NO, width=30)
    tree.heading("terminus", text ="Термин", anchor=CENTER)
    tree.column("terminus", stretch=N, width=360)
    tree.heading("znachenie", text ="Определение", anchor=CENTER)
    tree.column("znachenie", stretch=NO, width=520)
    tree.pack(side=BOTTOM, expand=1, fill=BOTH)
    frame.pack(anchor=NW, side=LEFT)
    frame1.pack(anchor=NE, side=LEFT)
#Курс № 2
def tab2():
    global tree
    tab2 = ttk.Frame(tabControl)
    tabControl.add(tab2, text="<Информационная безопасность>")
#Курс № 3        
def tab3():
    global tree
    tab3 = ttk.Frame(tabControl)
    tabControl.add(tab3, text="<Вычислительные системы и сети>")    
#Поиск по базе данных и выгрузка
def search_entr():
    global tree
    row=0
    ent=(en.get())
    with sq.connect("tsi") as con:
      cursor=con.cursor()
      cursor.execute("SELECT №, Термин, Определение FROM tsi WHERE Термин=?", (ent,))
      rows=cursor.fetchall()
      print(rows)	
      for row in rows:
        tree.insert("",END, values=row)		
      con.close   
#Начальное окно изучение курсов
def clicked():
    global window
    global tabControl
    window = Toplevel()
    window.geometry('880x600+400+298')
    window.resizable(False,False)
    window.title("Глоссарий технических терминов")
    root.withdraw()
    tabControl=ttk.Notebook(window)
    lbl=Label(window, text=shapka1, justify="center", borderwidth=10, padx=10, pady=10, relief='ridge', width=108)
    lbl.pack(side=TOP)   
    tab1()
    tab2()
    tab3()
    tabControl.pack(expand=1, fill= "both") 
    close_btn = Button(window, text='Назад', width=15, height=2, command=lambda: [window.destroy(), root.deiconify()])
    close_btn.pack(anchor=SE)
    root.mainloop()    
#Стартовое окно
lbl=Label(root, text=shapka, justify="center", borderwidth=10,padx=10,pady=10,relief='ridge', width=108)
lbl.pack(side=TOP)
btn = Button(text='Начать изучение', width=15, height=5, command=clicked)
btn.pack(anchor=CENTER, pady=200)
close_btn = Button(root, text='Выход', width=15, height=2, padx=3, command=root.destroy)
close_btn.pack(anchor=SE)
root.mainloop()
