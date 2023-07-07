from tkinter import N
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import matplotlib.lines as line
import numpy as np
import time
import threading
import serial #导入模块
import serial.tools.list_ports
plt.rcParams["font.sans-serif"] =  'SimHei' #解决中文乱码问题
plt.rcParams['axes.unicode_minus']=False
group1=[1,2]
n=0
CHUNK = 2048  # 初始数据量
dataList=[]
dataX=[]
POWER_DATA=[]
TIME_DATA=[]
x_data = [1,299]
y1_data = []
y2_data = [50,50]
data=np.random.normal(0,1,CHUNK)  # 存放数据，用于绘制图像，数据类型可为列表
print(type(data))
# 定义画布
fig = plt.figure(1)
ax = plt.subplot(111,ylim=(-10,200))
ax.set_xlim(0,300)
ax.set_title("转速pid",fontsize=8)  # 设置title

plt.suptitle('current',fontsize=8)
#line = line.Line2D([], [])  # 绘制直线
line1, = ax.plot(TIME_DATA, POWER_DATA, label='曲线1')
line2, = ax.plot(x_data, y2_data, label='曲线2')

TIME_DATA.append(0)
POWER_DATA.append(0) 
# 初始化图像
def plot_init():
    #ax.add_line(line)
    ##ax.add_line(line)
    #line.set_lable('fillstyle=full')
    #line.legend()
    plt.ylabel('N (n/m)')
    plt.xlabel('T (s)')

    return line1,line2 # 必须加逗号,否则会报错（TypeError: 'Line2D' object is not iterable）

# 更新图像(animation会不断调用此函数刷新图像，实现动态图的效果)
def plot_update(i):

    global POWER_DATA
    global TIME_DATA
    global n
    global group1
    #line.set_xdata(dataX)  # 更新直线的数据
    #line.set_ydata(dataList)  # 更新直线的数据
    #line.set_xdata(TIME_DATA)  # 更新直线的数据
    #line.set_ydata(POWER_DATA)  # 更新直线的数据
    line1.set_data(TIME_DATA, POWER_DATA)
    y2_data[0]=int(group1[-1])
    y2_data[1]=int(group1[-1])
    line2.set_data(x_data, y2_data)
    #print(y2_data)
    #line.set_ydata(group1)
	# 大标题（若有多个子图，可为其设置大标题）
    if n>=100:
        #ani.save('sin_test1.gif', writer='imagemagick', fps=100)
        #plt.close(fig)
        n=100
    # 重新渲染子图
    #ax.figure.canvas.draw()  # 必须加入这一行代码，才能更新title和坐标!!!
    return line1,line2  # 必须加逗号,否则会报错（TypeError: 'Line2D' object is not iterable）

# 绘制动态图
ani = animation.FuncAnimation(fig,   # 画布
							  plot_update,  # 图像更新
                              init_func=plot_init,  # 图像初始化
                              frames=100,
                              interval=1,  # 图像更新间隔
                              blit=True)

# 数据更新函数
def dataUpdate_thead():
    global dataList
    global dataX
    global n
    # 为了方便理解代码，这里生成正态分布的随机数据
    while True:  # 为了方便测试，让数据不停的更新time.sleep(1)     
                data1=np.random.normal(0,1,CHUNK)
                time.sleep(1)
                data1=np.random.randint(0,9)
                dataList.append(data1)
                n=n+1
                dataX.append(n)
                #print(dataList)
                #print(dataX)
                
                if n==200:
                    
                    break
def recive_data(a):
    n1=0
    s=True
    global TIME_DATA
    global POWER_DATA
    global group1
    #超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
    timex=1
    # 打开串口，并得到串口对象
    ser=serial.Serial("COM3",115200,timeout=timex)
    print("串口已经启动\r\n")
    while s:
        
        data3=ser.readline().decode("gbk")
        print(data3)
        if data3.find('d') == 0:#每收到一个数据 开始处理
        #读一个字节//read.hex()
            
            n1+=1
            text="数据"+str(n1)+"已经收到\r\n"
            result=ser.write(text.encode("gbk"))
            print("写总字节数:",result)

            data3=data3.strip('d')#移除
            data3=data3.rstrip('\r\n')#字符串末尾的指定字符
            print(data3)
            data3=data3.split(",")#通过指定分隔符对字符串进行切片
            group1 = data3[:len(data3)//2]
            group2 = data3[len(data3)//2:]
            print(group1,group2,type(group1))
            
            #POWER_DATA.append(0-float(group1)) 
            for value in group2:
                if value != '':
                    try:
                        float_value = float(value)
                        print(float_value)
                        TIME_DATA.append(float(n1))
                        POWER_DATA.append(float_value)
                    except ValueError:
                        print("Invalid value:", value)
                else:
                    print("Empty value detected, skipping.")
            # for value in group2:
            #     float_value = float(value)
            #     neg_value = 0 - float_value
            #     POWER_DATA.append(neg_value)
            #print(POWER_DATA,type(POWER_DATA),TIME_DATA,type(TIME_DATA))
            

            if n1==1000:
                s=0
        time.sleep(0.1) 
    ser.close()#关闭串口
    print("串口已经关闭]\r\n")

# 为数据更新函数单独创建一个线程，与图像绘制的线程并发执行
ad_rdy_ev = threading.Event()
ad_rdy_ev.set()  # 设置线程运行
#t = threading.Thread(target=dataUpdate_thead, args=()) # 更新数据，参数说明：target是线程需要执行的函数，args是传递给函数的参数）
t2=threading.Thread(target=recive_data, args=("t2",)) 
t2.daemon = True

#t.start()  # 线程执行
t2.start()  # 线程执行
#ani.save('sin_test1.gif', writer='pillow',fps=500)
plt.show()