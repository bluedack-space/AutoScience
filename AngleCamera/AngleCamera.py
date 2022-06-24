from iOSMotionHandler import *

#coding: utf-8
# For use in pythonista on iOS
import ui

from scene import *
import math
import numpy as np
import time
scale =80  # scale raw accelerometer values to screen
W=2
L=1
H=.5/2
class MyScene (Scene):
    def setup(self):
            global scale
            scale=self.size.w/10
            #motion start
            motion.start_updates()
            #pitch,roll,yawメータの半径
            self.R=scale
            #Boxの定義 後の計算の為arrayにしておく
            self.Box=[[[W,L,-H]],[[-W,L,-H]],[[-W,-L,-H]],[[W,-L,-H]],[[W,L,H]],[[-W,L,H]],[[-W,-L,H]],[[W,-L,H]]]
            self.Box=np.array(self.Box)

    def draw(self):
        #Boxの中心
        self.cx =self.size.w * 0.5
        self.cy = self.size.h * 0.5
        #pitch,roll,yawメータの中心
        self.cx2 =self.size.w * 0.5
        self.cy2 = self.size.h * 0.5-scale*3.5
        time.sleep(0.1)
        
        #motionセンサの値更新
        ax,ay,az        = iOSMotionHandler.getUserAcceleration()
        gx,gy,gz        = iOSMotionHandler.getGravity()
        pitch,roll,yaw  = iOSMotionHandler.getAttitude()
        mx,my,mz,ma     = iOSMotionHandler.getMagneticField()
        
        #ラジアン→度
        pitch= -pitch*180/3.1415926
        roll = roll*180/3.1415926
        yaw  = -yaw*180/3.1415926
        
        #redraw screen
        background(1, 1, 1)
        fill(1,1,1)
        stroke(0,0,0)
        stroke_weight(1)
        #pitch,roll,yaw描画
        ellipse(self.cx2-scale*3-self.R,self.cy2-self.R,self.R*2,self.R*2)
        ellipse(self.cx2-0.0-self.R,self.cy2-self.R,self.R*2,self.R*2)
        ellipse(self.cx2+scale*3-self.R,self.cy2-self.R,self.R*2,self.R*2)
        roll_sin=math.sin(math.radians(roll))
        roll_cos=math.cos(math.radians(roll))
        pitch_sin=math.sin(math.radians(pitch))
        pitch_cos=math.cos(math.radians(pitch))
        yaw_sin=math.sin(math.radians(yaw))
        yaw_cos=math.cos(math.radians(yaw))
        line(self.cx2-roll_cos*self.R-scale*3,self.cy2-roll_sin*self.R,self.cx2+roll_cos*self.R-scale*3,self.cy2+roll_sin*self.R)
        line(self.cx2-pitch_cos*self.R-0,self.cy2-pitch_sin*self.R,self.cx2+pitch_cos*self.R-0,self.cy2+pitch_sin*self.R)
        line(self.cx2-yaw_cos*self.R+scale*3,self.cy2-yaw_sin*self.R,self.cx2+yaw_cos*self.R+scale*3,self.cy2+yaw_sin*self.R)
        #回転マトリックスの計算
        yawMatrix = np.matrix([[yaw_cos, -yaw_sin, 0],[yaw_sin, yaw_cos, 0],[0, 0, 1]])
        pitchMatrix = np.matrix([[pitch_cos, 0, pitch_sin],[0, 1, 0],[-pitch_sin, 0, pitch_cos]])
        rollMatrix = np.matrix([[1, 0, 0],[0, roll_cos, -roll_sin],[0, roll_sin, roll_cos]])
        R = yawMatrix * pitchMatrix * rollMatrix
        R=np.array(R)
        x_3d,y_3d,z_3d=np.transpose(np.dot(self.Box,R),(2,0,1))
        #陰線処理のため1番奥の頂点を特定
        zmin=np.argmin(z_3d)
        #奥の頂点を含んでいない辺を描画
        if zmin!=0 and zmin!=1 :
            line(self.cx+x_3d[0]*scale,self.cy+y_3d[0]*scale,self.cx+x_3d[1]*scale,self.cy+y_3d[1]*scale)
        if zmin!=1 and zmin!=2 :
            line(self.cx+x_3d[1]*scale,self.cy+y_3d[1]*scale,self.cx+x_3d[2]*scale,self.cy+y_3d[2]*scale)
        if zmin!=2 and zmin!=3 :
            line(self.cx+x_3d[2]*scale,self.cy+y_3d[2]*scale,self.cx+x_3d[3]*scale,self.cy+y_3d[3]*scale)
        if zmin!=3 and zmin!=0 :
            line(self.cx+x_3d[3]*scale,self.cy+y_3d[3]*scale,self.cx+x_3d[0]*scale,self.cy+y_3d[0]*scale)

        if zmin!=4 and zmin!=5 :
            line(self.cx+x_3d[4]*scale,self.cy+y_3d[4]*scale,self.cx+x_3d[5]*scale,self.cy+y_3d[5]*scale)
        if zmin!=5 and zmin!=6 :
            line(self.cx+x_3d[5]*scale,self.cy+y_3d[5]*scale,self.cx+x_3d[6]*scale,self.cy+y_3d[6]*scale)
        if zmin!=6 and zmin!=7 :
            line(self.cx+x_3d[6]*scale,self.cy+y_3d[6]*scale,self.cx+x_3d[7]*scale,self.cy+y_3d[7]*scale)
        if zmin!=7 and zmin!=4 :
            line(self.cx+x_3d[7]*scale,self.cy+y_3d[7]*scale,self.cx+x_3d[4]*scale,self.cy+y_3d[4]*scale)

        if zmin!=0 and zmin!=4 :
            line(self.cx+x_3d[0]*scale,self.cy+y_3d[0]*scale,self.cx+x_3d[4]*scale,self.cy+y_3d[4]*scale)
        if zmin!=1 and zmin!=5 :
            line(self.cx+x_3d[1]*scale,self.cy+y_3d[1]*scale,self.cx+x_3d[5]*scale,self.cy+y_3d[5]*scale)
        if zmin!=2 and zmin!=6 :
            line(self.cx+x_3d[2]*scale,self.cy+y_3d[2]*scale,self.cx+x_3d[6]*scale,self.cy+y_3d[6]*scale)
        if zmin!=7 and zmin!=3 :
            line(self.cx+x_3d[3]*scale,self.cy+y_3d[3]*scale,self.cx+x_3d[7]*scale,self.cy+y_3d[7]*scale)

        #取得したmotionセンサのデータを画面上に印字
        tint(0,0,0,1)
        text('roll', font_name='Helvetica', font_size=16.0, x=self.cx2-scale*3, y=self.cy2+self.R+40, alignment=5)
        text(str(round(roll,2)), font_name='Helvetica', font_size=16.0, x=self.cx2-scale*3, y=self.cy2+self.R+20, alignment=5)
        text('pitch', font_name='Helvetica', font_size=16.0, x=self.cx2, y=self.cy2+self.R+40, alignment=5)
        text(str(round(pitch,2)), font_name='Helvetica', font_size=16.0, x=self.cx2, y=self.cy2+self.R+20, alignment=5)
        text('yaw', font_name='Helvetica', font_size=16.0, x=self.cx2+scale*3, y=self.cy2+self.R+40, alignment=5)
        text(str(round(yaw,2)), font_name='Helvetica', font_size=16.0, x=self.cx2+scale*3, y=self.cy2+self.R+20, alignment=5)

        text('ax=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-20, alignment=6)
        text(str(ax),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-20, alignment=6)
        text('ay=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-40, alignment=6)
        text(str(ay),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-40,alignment=6)
        text('az=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-60, alignment=6)
        text(str(az),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-60, alignment=6)

        text('gx=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-80, alignment=6)
        text(str(gx),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-80, alignment=6)
        text('gy=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-100, alignment=6)
        text(str(gy),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-100,alignment=6)
        text('gz=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-120, alignment=6)
        text(str(gz),font_name='Helvetica',font_size=16.0,x=60, y=self.cy*2-120, alignment=6)
        text('magx=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-140, alignment=6)
        text(str(mx),font_name='Helvetica',font_size=16.0,x=80, y=self.cy*2-140, alignment=6)
        text('magy=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-160, alignment=6)
        text(str(my),font_name='Helvetica',font_size=16.0,x=80, y=self.cy*2-160,alignment=6)
        text('magz=',font_name='Helvetica',font_size=16.0,x=20, y=self.cy*2-180, alignment=6)
        text(str(mz),font_name='Helvetica',font_size=16.0,x=80, y=self.cy*2-180, alignment=6)
if __name__ == "__main__":
   scene = run(MyScene())
