# -*- coding: utf-8 -*-
"""USER_RATE_FINAL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/132gHvwmvUKuRf_PtZeqRHDM8wkAVdk1q


## load data
"""

import requests, datetime
#選取的資料時間範圍為從現在到前一天
t1 = datetime.datetime.now()
t2 = t1 + datetime.timedelta(days= -10)

table_name = 'device_history'
columns = 'ip_adrs,dat,val_name,value,val_unit'
condition = " where dat between '"+t2.strftime("%Y-%m-%d %H:%M:%S")+"' and '"+t1.strftime("%Y-%m-%d %H:%M:%S")+"'"

condition = condition.replace(' ','%20')
condition = condition.replace("'",'%27')
r = requests.get('https://kent-iiot.synology.me/php/query_table_v2.php?tblfield='+columns+'&tblname='+table_name+''+condition)
print(r.status_code)

import ast
import json
import pandas as pd
temp_dict = {}
for i in ast.literal_eval(r.text) :
    for j in i:
        if j not in temp_dict.keys():
            temp_dict[j] = [i[j]]
        else:
            temp_dict[j].append(i[j])
df = pd.DataFrame(temp_dict)
df['value'] = df['value'].astype(float)
df

import matplotlib.pyplot as plt

plt.figure(figsize = (10,10))
plt.plot(df['val_name'].value_counts())

#有不同種類型的資料
print(set(list(df['val_name'])))

import matplotlib.pyplot as plt
for datatype in set(list(df['val_name'])):
    temp_df = df[df['val_name']==datatype]
    print(datatype,'(unit=',df['val_unit'].iloc[0],')')
    plt.figure(figsize=[15,2])
    plt.plot(temp_df['value'])
    plt.show()

df[df['val_name'] ==  'PLC_sec'].plot()

df_sp = df[(df['val_name'] ==  'S_speed_y') & (df['dat'].apply(lambda x:  x[0:10] == '2021-07-15') )]

"""## select day"""

df_position = df.loc[(df['val_name'] == 'PLC_sec') & (df['dat'].apply(lambda x:  x[0:10]) == '2021-07-12') ]
df_position

"""## begin time & end time"""

#future use
from datetime import datetime

begin_time = datetime.strptime(df['dat'].iloc[0], '%Y-%m-%d %H:%M:%S')
end_time = datetime.strptime(df['dat'].iloc[-1], '%Y-%m-%d %H:%M:%S')

day_span = end_time - begin_time 
day_span = day_span.seconds

vector = pd.Series(np.zeros(day_span))
time_vector = pd.Series(pd.period_range(begin_time, freq="s", periods=day_span))
vector.index = time_vector

"""## main function"""

import numpy as np
# for getting current time, last_time , 因為def裡面的變數不能測試

def position_worktime (variablename,day_want):

  """input (position variable name), calculate 
  the work time for that position variable """
  
  from datetime import datetime
  df_position = df.loc[df['val_name'] == 'cPos_z' ] #這邊因為測試方便不然理論上cPos_z應該要填 variablenames
  position_tuples = tuple(zip(df_position['dat'], df_position['value']))
  last_tuple =  position_tuples[0]
    
  """loop through the tuples, graspe
   idle time stamp by its values"""
  
  for current_tuple in position_tuples:
      
    if current_tuple[1] != last_tuple[1]:
        
      current_time = datetime.strptime(current_tuple[0], '%Y-%m-%d %H:%M:%S') #要記得註解給學長看
      last_time = datetime.strptime(last_tuple[0], '%Y-%m-%d %H:%M:%S')
        
      work_interval = (last_time, current_time)
      work_time = current_time - last_time


  """this part we aim for the slicing, the reason we used slicing 
  is because we can operate or gate on different index later"""

  vector = pd.Series(np.zeros(1000000))
  time_vector = pd.Series(pd.period_range("15/6/2021", freq="s", periods=1000000))
  vector.index = time_vector

  vector[last_time : current_time] = 1.0

  print(current_time)
  print(last_time)

  print(vector)
  return vector

"""## the one original"""

def use_rate(day_want)  
  vector_A = position_worktime(a,day_want)
  vector_B = position_worktime(b,day_want)
  vector_c = position_worktime(c,day_want)
  vector_total = vector_A + vector_B +vector_c
  unique, counts = np.unique(vector_total, return_counts=True)
  matrix = np.asarray((unique, counts)).T
  print(matrix)
  print(f'the 稼動率 will be {100 * matrix[1][1] / ( matrix[0][1] + matrix[1][1])} %, 總共idle的時間長度為{matrix[0][1]}秒鐘,總共working的時間長度為{matrix[1][1]}秒鐘')

"""## adjust version"""

def use_rate(day_want): 
  vector_A = position_worktime(a,day_want)
  vector_B = position_worktime(b,day_want)
  vector_c = position_worktime(c,day_want)
  vector_total = vector_A + vector_B + vector_c
  
  vector_work = vector_total[vector_total > 0]
  vector_idle = vector_total[vector_total <= 0]
  
  matrix = np.asarray((unique, counts)).T
  print(matrix)
  print(f'the 稼動率 will be {100 * matrix[1][1] / ( matrix[0][1] + matrix[1][1])} %, 總共idle的時間長度為{matrix[0][1]}秒鐘,總共working的時間長度為{matrix[1][1]}秒鐘')


  import matplotlib.pyplot as plt

  labels = ['正在加工', 'idle']
  sizes = [work_value, idle_value]
  explode = (0.1, 0) 

  fig1, ax1 = plt.subplots()
  ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
          shadow=True, startangle=90)
  ax1.axis('equal') 

  plt.show()

import matplotlib.pyplot as plt

labels = ['正在加工', 'idle']
sizes = [work_value, idle_value]
explode = (0.1, 0) 

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal') 

plt.show()

"""## Final Version"""

import numpy as np


def position_worktime (variablename,day_want): #輸入想要考慮的參數跟哪一天ㄋ

  """input (position variable name), calculate 
  the work time for that position variable """
  
  from datetime import datetime


  df_position = df.loc[(df['val_name'] == variablename) & (df['dat'].apply(lambda x:  x[0:10]) == day_want) ] #選日期跟選出考慮的變數名稱
  position_tuples = tuple(zip(df_position['dat'], df_position['value'])) #將time, 跟value整理成tuple of tuple的形式
  last_tuple =  position_tuples[0] #我們將last tuple設定為一開始的時間


  """這邊我們用來產生當天的向量，start time為當天開始的時間,一路到當天所收到的最後一筆data"""

  begin_time = datetime.strptime(df['dat'].iloc[0], '%Y-%m-%d %H:%M:%S')#取出今天開工的時間
  end_time = datetime.strptime(df['dat'].iloc[-1], '%Y-%m-%d %H:%M:%S') #取出今天收工的時間

  day_span = end_time - begin_time #今天總共工作的時間多長ㄋ？
  day_span = day_span.seconds #把他轉乘int

  vector = pd.Series(np.zeros(day_span)) #創造ㄧ個series
  time_vector = pd.Series(pd.period_range(begin_time, freq="s", periods=day_span)) #series長度是從每天上工到收工
  vector.index = time_vector #series的index是每天的工作時間
  
    
  """loop through the tuples, graspe
   idle time stamp by its values"""
  
  for current_tuple in position_tuples: #我們去loop過去整個（時間,value）所形成的tuple
      
    if current_tuple[1] != last_tuple[1]: #將位置跟上一次的進行比較
        
      current_time = datetime.strptime(current_tuple[0], '%Y-%m-%d %H:%M:%S') 
      last_time = datetime.strptime(last_tuple[0], '%Y-%m-%d %H:%M:%S') #我們把時間str轉換成datetime,這樣之後可以做相減,也可以方便做slicing
        
      work_interval = (last_time, current_time)   #我們將時間戳章紀錄起來,分別是開始跑的時間跟
      work_time = current_time - last_time  #可以選擇的功能, 如果希望知道機器連續運作了多久,之後如果需要讓機器休息可以靠慮

      vector[last_time : current_time] = 1.0 #把開始的時間到結束的時間做slicing, why vector? 因為我們後面如果考慮多個參數可以用OR Gate

      last_tuple = current_tuple #然後我們將last_tuple進行更新


  """this part we aim for the slicing, the reason we used slicing 
  is because we can operate or gate on different index later"""



  print(vector)
  return vector #把slicing 的向量return回來,之後就可以來做or的邏輯囉！


  

def speed_worktime (variablename,day_want): #輸入想要考慮的參數跟哪一天ㄋ

  """input (speed variable name), calculate 
  the work time for that speed variable """
  
  from datetime import datetime


  df_speed = df.loc[(df['val_name'] == variablename) & (df['dat'].apply(lambda x:  x[0:10]) == day_want) ] #選日期跟選出考慮的變數名稱
  speed_tuples = tuple(zip(df_speed['dat'], df_speed['value'])) #將time, 跟value整理成tuple of tuple的形式
 

  """這邊我們用來產生當天的向量，start time為當天開始的時間,一路到當天所收到的最後一筆data"""

  begin_time = datetime.strptime(df['dat'].iloc[0], '%Y-%m-%d %H:%M:%S')#取出今天開工的時間
  end_time = datetime.strptime(df['dat'].iloc[-1], '%Y-%m-%d %H:%M:%S') #取出今天收工的時間

  day_span = end_time - begin_time #今天總共工作的時間多長ㄋ？
  day_span = day_span.seconds #把他轉乘int

  vector = pd.Series(np.zeros(day_span)) #創造ㄧ個series
  time_vector = pd.Series(pd.period_range(begin_time, freq="s", periods=day_span)) #series長度是從每天上工到收工
  vector.index = time_vector #series的index是每天的工作時間
  
    
  """loop through the tuples, graspe
   idle time stamp by its values"""
  
  for i in range(len(speed_tuples)): #我們去loop整個工作時間中的每一秒

    if speed_tuples[i][1]!=0 and speed_tuples[i+1][1]!=0:
      current_time = datetime.strptime(speed_tuples[i+1][0], '%Y-%m-%d %H:%M:%S')
      last_time = datetime.strptime(speed_tuples[i][0], '%Y-%m-%d %H:%M:%S')
      vector[last_time : current_time] = 1
    elif speed_tuples[i][1]!=0 and speed_tuples[i+1][1]==0:
      current_time_1 = datetime.strptime(speed_tuples[i+1][0], '%Y-%m-%d %H:%M:%S')
      last_time_1 = datetime.strptime(speed_tuples[i][0], '%Y-%m-%d %H:%M:%S')
      vector[last_time_1 : current_time_1] = 1
    else:
      continue
  


  """this part we aim for the slicing, the reason we used slicing 
  is because we can operate or gate on different index later"""



  print(vector)
  return vector #把slicing 的向量return回來,之後就可以來做or的邏輯囉！

def use_rate(critiria_want,day_want, mode): 
  
  if mode == "POSITION":
    vector_total = position_worktime(critiria_want,day_want)  #這邊可以視需求想要考慮多少個index來決定,這一個module的考慮數量是彈性的
  elif mode =="SPEED" :
    vector_total = speed_worktime(critiria_want,day_want)

  #vector_A = position_worktime(a,day_want)
  #vector_B = position_worktime(b,day_want)
  #vector_c = position_worktime(c,day_want)
  #vector_total = vector_A + vector_B + vector_c
  
  vector_work = vector_total[vector_total > 0]
  vector_idle = vector_total[vector_total <= 0]   #將slice之後的結果分成兩個向量,一個是大於0（ａｋａ有在做事）,另一個是等於0的( a k a沒有在做事)
  
 
  print(f'the 稼動率 will be {100 * vector_work.size/ ( vector_work.size + vector_idle.size)} %, 總共idle的時間長度為{vector_idle.size}秒鐘,總共working的時間長度為{vector_work.size}秒鐘')


  import matplotlib.pyplot as plt     #將結果用圓餅圖呈現

  labels = ['正在加工', 'idle']
  sizes = [vector_work.size, vector_idle.size]
  explode = (0.1, 0)    #讓idle呈現出來, 方便閱讀

  fig1, ax1 = plt.subplots()
  ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',   #畫圓餅
          shadow=True, startangle=90)
  ax1.axis('equal') 

  plt.show()

  return 100 * vector_work.size/ ( vector_work.size + vector_idle.size)

import time
start = time.time()

use_rate('S_speed_y','2021-07-15','SPEED')

end = time.time()
print(f'此次計算的運行時間為{end - start}秒鐘')

import time
start = time.time()

use_rate('PLC_sec','2021-07-15','POSITION')

end = time.time()
print(f'此次計算的運行時間為{end - start}秒鐘')


"""

#!pip install mariadb
import mariadb
import sys

conn = mariadb.connect(
    user="kntust",
    password="Ikent$123",
    host="140.118.201.250",
    port=3306,
    database="energy"
)
cur = conn.cursor()

rate_insert = use_rate('PLC_sec','2021-07-15','POSITION')

import datetime

dat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
item = 'utiliz'
value = rate_insert #單位 % float
sql = "INSERT INTO `result`(`dat`, `item`, `value`) VALUES ('" + dat +"' , '"+ item +"' , '"+ str(value) +"')"
cur.execute(sql)
conn.commit()
conn.close()

"""## some test chunk"""

vector = position_worktime('')
unique, counts = np.unique(vector, return_counts=True)
matrix = np.asarray((unique, counts)).T
print(matrix)
print(f'the 稼動率 will be {100 * matrix[1][1] / ( matrix[0][1] + matrix[1][1])} %, 總共idle的時間長度為{matrix[0][1]}秒鐘,總共working的時間長度為{matrix[1][1]}秒鐘')

#this work, this one is for create 0 series with time index
import numpy as np
vector = pd.Series(np.zeros(1000000))
time_vector = pd.Series(pd.period_range("15/6/2021", freq="s", periods=1000000))
vector.index = time_vector
print(vector)

#this work, this one for setting them to 1
vector[last_time : current_time] = 1
vector[last_time : current_time]

time_stamp

#this one work
time_stamp = []
time_work = []

def position_worktime (variablename):
  
  '''input (position variable name)
  calculate the work time for that position variable '''

  df_position = df.loc[df['val_name'] == variablename ]

  from datetime import datetime
  
  
  position_tuples = tuple(zip(df_position['dat'], df_position['value']))
  last_tuple =  position_tuples[0]
  
  for current_tuple in position_tuples:
    
    if current_tuple[1] != last_tuple[1]:
      
      current_time = datetime.strptime(current_tuple[0], '%Y-%m-%d %H:%M:%S') 
      last_time = datetime.strptime(last_tuple[0], '%Y-%m-%d %H:%M:%S')
      
      work_interval = (last_time, current_time)
      work_time = current_time - last_time
      
      time_stamp.append(work_interval)
      time_work.append(work_time)
    
    last_tuple = current_tuple

position_worktime('cPos_z')

print(time_stamp)
print(time_work)

time_work_S = pd.Series(time_work)
time_work_total = sum(time_work_S.dt.seconds)
print(time_work_total)

position_tuples

print(work_time)

time_stamp = pd.Series(time_stamp)
time_stamp.dt.seconds

df_position = df.loc[df['val_name'] == 'cPos_z' ]

position_tuples = tuple(zip(df_position['dat'], df_position['value']))
last_val =  position_tuples[0]
time_stamp = []
time_work = []
i = 0

for current_tuple in position_tuples:
  if current_tuple[1] != last_val[1]:
      
    current_time = datetime.strptime(current_val[0], '%Y-%m-%d %H:%M:%S') 
    last_time = datetime.strptime(last_val[0], '%Y-%m-%d %H:%M:%S')
      
    work_interval = (current_time, last_time)
    work_time = current_time - last_time
      
    time_stamp.append(work_interval)
    time_work.append(work_time)

    i += 1
    
    last_val = current_val

current

time_stamp

i

position_tuples



"""## timer"""

import time

start = time.time()
print("hello")
end = time.time()
print(end - start)

"""## complex

時間複雜度 O(n)
這邊因為資料量有限3600＊小時,所以我們用比較多的空間複雜度o(n)
"""