from annotation import Ui_MainWindow
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QGraphicsView,QGraphicsPixmapItem,QFileDialog,QGraphicsScene,QStyleOptionGraphicsItem
from PyQt5.QtGui import QPixmap,QImage,QPainter,QBrush,QPen,QColor
from PyQt5.QtCore import Qt,QPoint,pyqtSignal,QThread
import os
import sys
from XMLProcess import XML


import cv2 as cv

IMAGE_W,IMAGE_H=871,489 #设置软件中显示的图片大小   #761,581

distFloader=""
res=False


class GraphicsPixItem(QGraphicsPixmapItem):
    def __init__(self,parent=None):
        super(GraphicsPixItem,self).__init__(parent)
        self.__isChecked=False                      #标注是否选择了右边的选项
        self.__isDrawing=False                      #标注是否正在绘图
        self.__tempPixmap=QPixmap()                 #辅助画布
        self.__firstPoint=QPoint()                  #起始坐标
        self.__latestPoint=QPoint()                 #最新的坐标
        self.__pen=QPen()                           #对画笔的设置
        self.__pen.setColor(QColor(255,0,0))
        self.__pen.setWidth(3)
        self.__oldPen=QPen()
        self.__oldPen.setColor(QColor(0,255,0))
        self.__oldPen.setWidth(2)
        self.__posOfObject=[]                           #装载图像中的物体坐标


    def setChecks(self,state=False):
        self.__isChecked=state

    def paint(self, Painter, StyleOptionGraphicsItem, Widget):
        """
        绘图更新函数，调用self.update()时，自动调用该函数
        :param QPainter:
        :param QStyleOptionGraphicsItem:
        :param QWidget:
        :return:
        """
        x = self.__firstPoint.x()
        y=self.__firstPoint.y()
        w=self.__latestPoint.x()-x
        h=self.__latestPoint.y()-y
        self.__tempPixmap=self.pixmap()


        Painter.drawPixmap(0,0,self.__tempPixmap)
        if self.__isChecked:
            Painter.setPen(self.__pen)
            Painter.drawRect(x,y,w,h)
            #Painter.drawRect(361, 307, 388, 343)
        #绘制以前画的矩形

        for pos in self.__posOfObject:
            xOld=pos[0]
            yOld=pos[1]
            wOld=pos[2]-xOld
            hOld=pos[3]-yOld
            Painter.setPen(self.__oldPen)
            Painter.drawRect(xOld,yOld,wOld,hOld)

        # else:
        #     print("not checked")
        #



    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        """
        重载鼠标事件，获取坐标
        :param QGraphicsSceneMouseEvent:
        :return:
        """
        # print(QGraphicsSceneMouseEvent.scenePos().x())
        # print(QGraphicsSceneMouseEvent.scenePos().y())
        # print(QGraphicsSceneMouseEvent.button())
        if QGraphicsSceneMouseEvent.button()==Qt.LeftButton:
            if self.__isChecked:
                self.__firstPoint=QGraphicsSceneMouseEvent.scenePos()
                self.__isDrawing=True
            else:
                print("not loaded")






    def mouseMoveEvent(self, QGraphicsSceneMouseEvent):
        """
        重载鼠标事件，处理鼠标拖动过程
        :param QGraphicsSceneMouseEvent:
        :return:
        """
        # print(QGraphicsSceneMouseEvent.scenePos().x())
        # print(QGraphicsSceneMouseEvent.scenePos().y())
        # x=self.__firstPoint.x()
        # y=self.__firstPoint.y()
        # w=QGraphicsSceneMouseEvent.scenePos().x()-x
        # h=QGraphicsSceneMouseEvent.scenePos().y()-y
        self.__latestPoint=QGraphicsSceneMouseEvent.scenePos()
        if self.__isChecked:
            self.update()



    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        """
        重载鼠标释放函数，获取最终坐标
        :param QGraphicsSceneMouseEvent:
        :return:
        """
        # print(QGraphicsSceneMouseEvent.scenePos().x())
        # print(QGraphicsSceneMouseEvent.scenePos().y())
        if QGraphicsSceneMouseEvent.button()==Qt.LeftButton:
            self.__latestPoint=QGraphicsSceneMouseEvent.scenePos()
            self.__isDrawing=False
            # x=self.__firstPoint.x()
            # y=self.__firstPoint.y()
            # w=self.__endPoint.x()-x
            # h=self.__endPoint.y()-y
            if self.__isChecked:
                self.__setPos()             #设置坐标数据
            self.__isChecked=False
            self.update()



    def __setPos(self):
        """
        该函数获取物体的坐标
        :return:
        """
        Xmin=self.__firstPoint.x()
        Ymin=self.__firstPoint.y()
        Xmax=self.__latestPoint.x()
        Ymax=self.__latestPoint.y()
        self.__posOfObject.append([Xmin,Ymin,Xmax,Ymax])

    def clearPos(self):
        """
        清空坐标缓存
        :return:
        """
        self.__posOfObject=[]


    def getPos(self):
        """
        返回坐标信息
        :return:array对象
        """
        return self.__posOfObject







class Graphicscene(QGraphicsScene):
    """
    绘图相关的类
    """
    def __init__(self,parent=None):
        super(Graphicscene,self).__init__(parent)
    # def mousePressEvent(self, QGraphicsSceneMouseEvent):
    #     Graphicscene.mouseMoveEvent(self,QGraphicsSceneMouseEvent)




class VideoThread(QThread):
    """
    处理视屏的线程类
    """
    def __init__(self,parent=None):
        super(VideoThread,self).__init__(parent)
        self.__dist_path=""
        self.__filename=""
        self.__videoPath=""
        self.__frameCount=0             #总总帧数
        self.__currentFrameIndex=0


    def run(self):
        """
        此处编写视屏处理的业务逻辑
        :return:
        """

        # 调用图片处理方法


        cap = cv.VideoCapture(self.__videoPath)
        self.__frameCount=cap.get(cv.CAP_PROP_FRAME_COUNT)

        cwd = os.getcwd()
        if not os.path.exists(self.__dist_path):
            os.makedirs(self.__dist_path)

        os.chdir(self.__dist_path)

        while (cap.isOpened()):
            ret, frame = cap.read()
            cv.imwrite(self.__filename+"_"+str(self.__currentFrameIndex)+".jpg",frame)
            # print(self.__dist_path + self.__filename + "_" + str(self.__currentFrameIndex) + ".jpg")

            self.__currentFrameIndex= self.__currentFrameIndex + 1
            percent=(self.__currentFrameIndex/self.__frameCount)*100
            self.__progressBar.setProperty("value",percent)

            if self.__currentFrameIndex>=self.__frameCount:
                break

        os.chdir(cwd)
        cap.release()

        return

    def getfilenames(self,dist_path,filename,videopath):
        """
        获取文件名称以及路径
        :param dist_path:
        :param filename:
        :return:
        """
        self.__dist_path=dist_path
        self.__filename=filename
        self.__videoPath=videopath

    def getProgressEntery(self,progressbar):
        """
        获取progressBar
        :param progressBar:
        :return:
        """
        self.__progressBar=progressbar







class annWind(QMainWindow,Ui_MainWindow):
    """
    主窗口的工作类，主要为业务逻辑
    """
    def __init__(self,parent=None):
        super(annWind,self).__init__(parent)
        self.setupUi(self)

        #-----------------------链接信号与槽--------------------
        self.actionSelectFloader.triggered.connect(self.getFloader)
        self.actionSelectFile.triggered.connect(self.getFile)
        self.actionClose.triggered.connect(self.closeApp)
        self.openVideo.triggered.connect(self.openvideo)
        self.confirmAndAnnocateButton.clicked.connect(self.confirmAndann)
        self.nextPicButton.clicked.connect(self.nextpic)
        #----------------------------------------------------

        self.__graphicSence=Graphicscene()
        self.__datafloderPath=""                            # 文件夹路径
        self.__imagePath=""                                 # 文件路径,用于单独打开的一个文件.
        self.__filelist=[]                                  # 图片文件名列表
        self.__image=QImage()                               # Qimage对象，用于装载当前图片
        self.__pixmap=QPixmap()                             # QPixmap对象，用于将QImage转换为Pixmap对象并且存储起来，该对象用于显示以及绘图
        self.__graphicItem=GraphicsPixItem()
        self.infoTextBrowser.setText("初始化完成。请设置输入文件夹或者输入文件路经..........")
        self.__isPicloaded=False                            # 图片是否加载的标志
        self.__outInfo=[]                                   # 存储图片中的相关数据,将被输出到xml 文件中[rat/others/non,truncet:-1/1,
                                                            # occlud:-1/1,perspect:0-frontal/1-side/2-tail, ]
        self.__index=1                                      # 给定文件夹下，加载当前图片的索引
        self.__imageFileCounts=0                            # 文件夹中图片文件的总数
        self.__videoPath=""
        self.__videoThread=VideoThread()                    # 处理视屏的工作线程





    def __write2images(self):
        """
        把视屏的每一帧写到特定的文件夹中
        :return:
        """
        self.infoTextBrowser.append("处理视屏中....")
        # 将视频转换为图片,并且放在视屏目录下
        dist_path =self.__videoPath.split(".")[0]+"/"
        filename=dist_path.split("/")[-2]
        #print(dist_path,filename)
        self.__videoThread.getfilenames(dist_path,filename,self.__videoPath)
        self.__videoThread.getProgressEntery(self.progressBar)  #控制进度条
        self.__videoThread.start()







    def openvideo(self):
        """
        打开一个视屏文件
        :return:
        """
        self.__videoPath = QFileDialog.getOpenFileName(self, None, "选择文件", )[0]
        filename = self.__videoPath
        sufix = filename.split(".")[-1]
        if sufix.lower() == "mov":
            #此处获取了文件名称路径，开始读取视频
            self.__write2images()
            #QMessageBox.information(self, "通知", "成功选择文件"+filename, QMessageBox.Yes)
        elif sufix == "":
            pass
        else:
            QMessageBox.warning(self, "错误", "选择的文件类型错误！可接受*.mov类型文件！", QMessageBox.Yes)






    def confirmAndann(self):
        """
        获取识别结果
        :return:
        """
        # 选择目标类别

        outInfo=["",-1,-1,-1]

        if self.ratButton.isChecked():
            outInfo[0] = "rats"
        elif self.nonratButton.isChecked():
            outInfo[0] = "others"
        elif self.nonobjectButton.isChecked():
            outInfo[0] = "non"
        else:
            QMessageBox.critical(self, "错误", "第一步必选类别尚未选择", QMessageBox.Yes)
            return

        #选择可选项
        if self.truncetCheckBox.isChecked():
            outInfo[1]=1
        else:
            outInfo[1]=-1

        if self.occludCheckBox.isChecked():
            outInfo[2]=1
        else:
            outInfo[2]=-1

        # 观察角度选择
        if self.frontalButton.isChecked():
            outInfo[3]=0
        elif self.sideButton.isChecked():
            outInfo[3]=1
        elif self.tailButton.isChecked():
            outInfo[3]=2

        # 判断是否加载了图片
        if self.__isPicloaded:
            # 判断坐标缓存和标记缓存的长度是否相等
            if len(self.__outInfo)==len(self.__graphicItem.getPos()):
                self.__outInfo.append(outInfo)
                # print(self.__outInfo)
                self.__graphicItem.setChecks(True)
            else:
                QMessageBox.information(self, "提示", "请标记图片中的目标\n然后再进行下一个目标标记", QMessageBox.Yes)
        else:
            self.__outInfo=[]    # 重置图片中的信息
            QMessageBox.critical(self, "错误", "图片尚未加载\n请先在菜单中选择图片放置的文件夹", QMessageBox.Yes)
            self.__graphicItem.setChecks(False)



    def nextpic(self):
        """
        将本张图片的坐标信息存储下来，同时加载下一张照片
        :return:
        """
        self.tailButton.setChecked(False)
        self.sideButton.setChecked(False)
        self.frontalButton.setChecked(False)

        # 判断文件夹是否已经选好以及文件夹中有无图片
        if len(self.__filelist) > 0 or self.__imagePath != "":
            # 获取并且清除缓存
            posOfCurrent = self.__graphicItem.getPos()      # 获取坐标信息
            self.__graphicItem.clearPos()                   # 清空坐标缓存
            picOutInfo = self.__outInfo                     # 获取标记信息
            self.__clearOutInfo()                           # 清空图片标记信息缓存

            # 删除多余的状态信息
            if len(posOfCurrent)<len(picOutInfo):
                picOutInfo.pop()

            # 如果没有做标记，则不做操作
            if len(posOfCurrent)==0:
                self.infoTextBrowser.append("warning:第"+str(self.__index) + "张图片没有标记")
                # 判断索引是否超出文件数量
                if self.__index < self.__imageFileCounts:
                    self.__index = self.__index + 1
                    self.loadImage(self.__index)  # 载入下一张图片
                else:
                    QMessageBox.information(self, "信息", "该文件夹下图片已经全部标记完成.谢谢！", QMessageBox.Yes)

            else:

                if len(self.__filelist) > 0:                    # 对于文件夹的操作
                    self.infoTextBrowser.append("第" + str(self.__index) + "张图片：" + self.__filelist[self.__index - 1]+" 标记完成，"+"共标记了 "+str(len(posOfCurrent))+" 个目标")
                    # 将文件信息写入对应的xml文件中
                    # TODO：
                    xml=XML(self.__datafloderPath,self.__filelist[self.__index-1])
                    # 读取标记信息
                    xml.StoreInfo(posOfCurrent,picOutInfo)
                    # 存储图片
                    xml.savePic(self.__image)
                    # 判断索引是否超出文件数量
                    if self.__index < self.__imageFileCounts:
                        self.__index = self.__index + 1
                        self.loadImage(self.__index)             # 载入下一张图片
                    else:
                        QMessageBox.information(self, "信息", "该文件夹下图片已经全部标记完成.谢谢！", QMessageBox.Yes)

                elif self.__imagePath != "":                    # 对于文件的操作
                    # 将文件信息写入对应的xml文件中去
                    # TODO：

                    spath=self.__imagePath
                    fname=spath.split("/")[-1]
                    fpath=spath.split("/")[0:-1]
                    fpath="/".join(fpath)

                    xml=XML(fpath,fname)
                    xml.StoreInfo(posOfCurrent,picOutInfo)
                    xml.savePic(self.__image)
                    self.__imagePath=""
                    self.infoTextBrowser.append(self.__imagePath+"标记完成，"+"共标记了 "+str(len(posOfCurrent))+"个目标")



        else:
            QMessageBox.critical(self, "错误", "请先选择输入文件夹", QMessageBox.Yes)







    def __clearOutInfo(self):
        """
        清空图片标记信息
        :return:
        """
        self.__outInfo=[]





    def showImage(self,pixmap):
        """
        给函数一个Qimage对象，他在GraphicView的scene中显示出来
        :param pixmap:QPixmap对象
        :return:
        """
        self.__graphicItem = GraphicsPixItem(pixmap)
        # self.__graphicSence.addPixmap(QPixmap.fromImage(self.__image))
        self.__graphicSence.addItem(self.__graphicItem)
        self.graphicsView.setScene(self.__graphicSence)
        # self.graphicsView.resize(611,531)
        #print(self.__image.height(), self.__image.width())
        self.graphicsView.show()





    def loadImage(self,index):
        '''
        在所选目录中加载给定目录的图片
        :index:目录中的图片索引
        :return:
        '''

        # first,check the path and files.
        if len(self.__filelist)>0:
            # load image.
            self.__image.load(self.__datafloderPath+"/"+self.__filelist[index-1])
            # 获取原始图片大小,并且按照比例缩小
            self.__setWindWH()
            self.__image=self.__image.scaled(IMAGE_W,IMAGE_H,Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
            self.__pixmap=QPixmap.fromImage(self.__image)                   # 转换为Pixmap对象
            self.showImage(self.__pixmap)
            self.__isPicloaded=True
            self.infoTextBrowser.append("载入第"+str(index)+"张图片："+self.__filelist[index-1])




    def __setWindWH(self):
        """
        按照图像原来比例放缩到与窗口合适的尺寸,在装载了图像之后使用
        :return:
        """
        global IMAGE_W,IMAGE_H
        originWidth = self.__image.width()
        orighnHeight = self.__image.height()
        windWidth = self.verticalLayout_4.geometry().width()
        windHeight = self.verticalLayout_4.geometry().height()
        IMAGE_H = (windWidth * orighnHeight) / originWidth
        IMAGE_W = windWidth
        # print(windWidth,windHeight)


    def loadSingelImage(self):
        """

        :return:
        """
        if self.__imagePath=="":
            pass
        else:
            self.__image.load(self.__imagePath)
            self.__setWindWH()
            self.__image = self.__image.scaled(IMAGE_W, IMAGE_H, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.__pixmap = QPixmap.fromImage(self.__image)  # 转换为Pixmap对象
            self.showImage(self.__pixmap)
            self.__isPicloaded = True
            self.infoTextBrowser.append("载入图片："+self.__imagePath)





    def getFloader(self):
        '''
        here,we get floader path of Images/videos to be processed.
        :return: 
        '''
        fileList=[]      #用于放置文件夹下所有文件的名称

        #status=False    #choosed floaders.
        self.__datafloderPath=QFileDialog.getExistingDirectory(self,None,"请选择文件夹")

        if self.__datafloderPath!="":
            fileList=os.listdir(self.__datafloderPath)

            #status=True
        else:
            QMessageBox.critical(self, "错误", "选择路经为空！", QMessageBox.Yes)


        #获取文件夹下图片文件列表
            #每次获取列表前，清空列表内容
        self.__filelist.clear()
        for file in fileList:
            sufix=file.split(".")[-1]
            if sufix.lower()=="jpg" or sufix.lower()=="jpeg":
                self.__filelist.append(file)

        if len(self.__filelist)==0:
            QMessageBox.critical(self, "错误", "该文件夹中没有image/voc文件！", QMessageBox.Yes)
        else:
            self.infoTextBrowser.append("您选择的输入文件夹路经：" + self.__datafloderPath)
            self.infoTextBrowser.append("其中有"+str(len(self.__filelist))+"个图像文件。")
            #设置索引,加载第一张图片
            self.__index=1
            self.loadImage(self.__index)
            self.__imageFileCounts=len(self.__filelist)







    def getFile(self):
        '''
        here,we get files' path.
        :return:
        '''

        self.__imagePath=QFileDialog.getOpenFileName(self,None,"选择文件",)[0]
        filename=self.__imagePath
        sufix=filename.split(".")[-1]
        if(sufix.lower() =="jpg" or sufix.lower()=="jpeg"):
            self.loadSingelImage()
            # QMessageBox.information(self, "通知", "成功选择文件"+filename, QMessageBox.Yes)
        elif sufix=="":
            pass
        else:
            QMessageBox.warning(self, "错误", "选择的文件类型错误！可接受*.jpg,*.jpeg类型文件！", QMessageBox.Yes)






    def closeApp(self):
        '''
        Exit the process.
        :return:
        '''
        reply=QMessageBox.warning(self,"确认","你是否确定退出去？",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if reply==QMessageBox.Yes:
            self.close()
        else:
            pass












def iniall():
    '''
    This function is used to set the dist-path.
    :return:
    '''
    if not os.path.isfile("annotation.cfg"):
        file=open("annotation.cfg","w")

    with open("annotation.cfg","r") as f:
        res=f.readline()
        return res


def updateDistFloader():
    '''
    This function is used to update the dist-path.
    :return:
    '''
    path = QFileDialog.getExistingDirectory(None, "请选择存储文件夹：")
    if not path == "":                                  #have choosed floader
        with open("annotation.cfg","w") as f:
            f.write(path)
        if not os.path.exists(path+"/VOC/"):
            os.makedirs(path+"/VOC/Annotations/")
            os.makedirs(path+"/VOC/ImageSets/Action/")
            os.makedirs(path+"/VOC/ImageSets/Layout/")
            os.makedirs(path+"/VOC/ImageSets/Main/")
            os.makedirs(path+"/VOC/ImageSets/Segmentation/")
            os.makedirs(path+"/VOC/JPEGImages/")
            os.makedirs(path+"/VOC/SegmentationClass/")
            os.makedirs(path+"/VOC/SegmentationObject/")
            os.makedirs(path+"/VOC/OriginalImages/")
        return True
    return False                                        #not choosed.







app=QApplication(sys.argv)


#process of dist-floaders.
distFloader=iniall()
if distFloader == "":
    res=updateDistFloader()
if distFloader=="" and res == False:
    QMessageBox.information(None,"提示！","请先选择存储输出的文件夹。",QMessageBox.Yes)
    path = QFileDialog.getExistingDirectory(None, "请选择存储文件夹：")
    secPath=updateDistFloader(path)
    if secPath==False:
        exit(0)

wind=annWind()
wind.show()
app.exit(app.exec_())