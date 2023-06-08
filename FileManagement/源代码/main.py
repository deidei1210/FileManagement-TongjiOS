import sys
import PyQt5.QtCore
from PyQt5.Qt import *
from File import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTreeWidget,QTreeWidgetItem,QMainWindow,QDesktopWidget,QWidget,QGridLayout,QAction,QLineEdit,QApplication,QFormLayout,QMessageBox,QListView,QAbstractItemView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from typing import Optional
import time
import os
import pickle

# 打开文件修改的界面
class FileEditDisplay(QWidget):
    _signal = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self, name, data):
        super().__init__()
        self.resize(1200, 800)
        self.setWindowTitle(name)
        self.name = name
        self.setWindowIcon(QIcon('img/FileImg.png'))

        self.resize(500, 500)
        self.text_edit = QTextEdit(self)
        self.text_edit.setText(data)
        self.text_edit.setPlaceholderText("Enter file content here")
        self.text_edit.textChanged.connect(self.changeMessage)
        self.initialData = data

        self.setupUI()

    def setupUI(self):
        self.createLayout()
        self.createButtons()
        self.setLayout(self.v_layout)
        self.setWindowModality(Qt.ApplicationModal)

    def createLayout(self):
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.text_edit)

        self.h_layout = QHBoxLayout()
        self.v_layout.addLayout(self.h_layout)

    def createButtons(self):
        self.save_button = QPushButton("Save", self)
        self.clear_button = QPushButton("Clear", self)

        self.save_button.clicked.connect(lambda: self.button_slot(self.save_button))
        self.clear_button.clicked.connect(lambda: self.button_slot(self.clear_button))

        self.h_layout.addWidget(self.save_button)
        self.h_layout.addWidget(self.clear_button)

    def closeEvent(self, event):
        if self.initialData == self.text_edit.toPlainText():
            event.accept()
            return

        reply = QMessageBox.question(self, 'Reminder', 'Do you want to save the changes to ' + self.name + '?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)

        if reply == QMessageBox.Ignore:
            event.ignore()
        elif reply == QMessageBox.Yes:
            self._signal.emit(self.text_edit.toPlainText())
            event.accept()
        else:
            event.accept()

    def changeMessage(self):
        pass

    def button_slot(self, button):
        if button == self.save_button:
            choice = QMessageBox.question(self, "Question", "Do you want to save it?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                with open('First text.txt', 'w') as f:
                    f.write(self.text_edit.toPlainText())
                self.close()
            elif choice == QMessageBox.No:
                self.close()
        elif button == self.clear_button:
            self.text_edit.clear()

# 显示文件属性的界面
class attributeFormDisplay(QWidget):
    def __init__(self, name, isFile, createTime, updateTime, child=0):
        super().__init__()
        self.resize(1200, 800)
        self.setWindowTitle('Attribute')
        self.name = name
        self.setWindowIcon(QIcon('img/attribute.png'))
        self.resize(412, 412)

        self.setupUI(isFile, createTime, updateTime, child)

    def setupUI(self, isFile, createTime, updateTime, child):
        grid = QGridLayout()

        self.addIcon(grid, isFile)
        self.addTextInfo(grid, isFile, createTime, updateTime, child)

        self.setLayout(grid)
        self.setWindowModality(Qt.ApplicationModal)

    def addIcon(self, grid, isFile):
        if isFile:
            icon = QPixmap('img/FileImg.png')
        else:
            icon = QPixmap('img/Filefolder.png')

        lbl = QLabel(self)
        lbl.setPixmap(icon)
        grid.addWidget(lbl, 0, 0)

    def addTextInfo(self, grid, isFile, createTime, updateTime, child):
        textLayout = QVBoxLayout()  # 垂直布局，用于放置文本信息
        textLayout.setSpacing(1)  # 设置间距

        self.addFileName(textLayout)
        self.addCreateTime(textLayout, createTime)

        if isFile:
            self.addUpdateTime(textLayout, updateTime)
        else:
            self.addChildProjects(textLayout, child)

        grid.addLayout(textLayout, 0, 1)  # 将文本信息布局放置在网格布局中的第二列

    def addFileName(self, layout):
        fileName = QLabel(self)
        fileName.setText('Name:' + self.name)
        font = QFont('黑体', 12)  # 设置为黑体，字号为12
        fileName.setFont(font)
        layout.addWidget(fileName)

    def addCreateTime(self, layout, createTime):
        createLabel = QLabel(self)
        createLabel.setText('Create Time: ' + self.formatTime(createTime))
        font = QFont('黑体', 12)  # 设置为黑体，字号为12
        createLabel.setFont(font)
        layout.addWidget(createLabel)

    def addUpdateTime(self, layout, updateTime):
        updateLabel = QLabel(self)
        updateLabel.setText('Modify Time: ' + self.formatTime(updateTime))
        font = QFont('黑体', 12)  # 设置为黑体，字号为12
        updateLabel.setFont(font)
        layout.addWidget(updateLabel)

    def addChildProjects(self, layout, child):
        updateLabel = QLabel(self)
        updateLabel.setText('There are ' + str(child) + ' projects inside.')
        font = QFont('黑体', 12)  # 设置为黑体，字号为12
        updateLabel.setFont(font)
        layout.addWidget(updateLabel)

    def formatTime(self, time):
        year = str(time.tm_year)
        month = str(time.tm_mon)
        day = str(time.tm_mday)
        hour = str(time.tm_hour).zfill(2)
        minute = str(time.tm_min).zfill(2)
        second = str(time.tm_sec).zfill(2)
        return year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + second

#右边显示文件大图标界面的一些操作
class FileListWindow(QListWidget):
    """支持拖拽的QListWidget"""
    def __init__(self, curNode,parents,parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        # 双击可编辑
        self.edited_item = self.currentItem()
        self.close_flag = True

        self.currentItemChanged.connect(self.close_edit)
        #当前目录
        self.curNode=curNode
        #父亲
        self.parents=parents
        #正在被编辑状态
        self.isEdit=False

    def edit_new_item(self) -> None:
        """edit一个新的item"""
        self.close_flag = False
        self.close_edit()
        count = self.count()
        self.addItem('')
        item = self.item(count)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        
    def editLast(self,index=-1)->None:
        self.close_edit()
        item = self.item(self.count()-1)
        self.setCurrentItem(item)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        self.isEdit=True
        self.index=index
        
    def editSelected(self,index)->None:
        self.close_edit()
        item = self.selectedItems()[-1]
        self.setCurrentItem(item)
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        self.isEdit=True
        self.index=index

    #实现在修改文件的名字的时候可以用回车结束修改
    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        if e.key() == Qt.Key_Return:
            if self.close_flag:
                self.close_edit()
            self.close_flag = True

    def close_edit(self, *_) -> None:
        """关闭edit"""
        if self.edited_item:
            self.isEdit=False
            self.closePersistentEditor(self.edited_item)
            #检验是否重名
            print(self.curNode.children)
            while True:
                sameName=False
                for i in range(len(self.curNode.children)-1):
                    if self.edited_item.text()==self.curNode.children[i].name and self.index!=i:
                        self.edited_item.setText(self.edited_item.text()+"(2)")
                        sameName=True
                        print('same name')
                        break
                if not sameName:
                    break
            
            #计算item在其父结点的下标
            
            self.curNode.children[self.index].name=self.edited_item.text()
            #更新父目录
            self.parents.updateTree()
            
            self.edited_item=None

#主界面
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #读文件，并且将文件内容存在disk，fat，catalog成员中
        self.ReadFilesFromDisk()
        self.setWindowUI()
        self.FileTreeUI()
        self.basicFileInfoUI()

       
        #美化
        self.UpdateRootBar()
        self.lastLoc=-1
    
    #设置窗口UI
    def setWindowUI(self):
        #根目录
        self.currentNode=self.catalog[0]#当前节点默认在根目录上
        self.rootNode=self.currentNode#赋值给根目录
        self.RootUrl=['root']

        #窗体基本信息
        self.resize(1200,800)#窗体大小
        self.setWindowTitle('Assignment3 FileManagement 2051498 DaizeChu')#窗口名称
        self.setWindowIcon(QIcon('img/folder.ico'))

        #窗口布局
        self.grid=QGridLayout()
        self.grid.setSpacing(10)
        self.widGet=QWidget()
        self.widGet.setLayout(self.grid)
        self.setCentralWidget(self.widGet)
        
        #菜单栏
        menubar=self.menuBar()
        
        menubar.addAction('Format', self.FormatDisk)
        
        menubar.addAction('Guide', self.OperationIntroduction)

        #设置返回键和前进键
        self.backArrow=QAction(QIcon('img/back.png'), '&返回',self)
        self.forwardArrow=QAction(QIcon('img/forward.png'), '&前进',self)

        self.backArrow.triggered.connect(self.backToTheLastFolder)
        self.forwardArrow.triggered.connect(self.forwardEvent)

        self.infoBar=self.addToolBar('tool bar')
        # self.toolBar.setStyleSheet("background-color: black;")
        self.infoBar.addAction(self.backArrow)
        self.infoBar.addAction(self.forwardArrow)
        
        self.backArrow.setEnabled(False)
        self.forwardArrow.setEnabled(False)
        #创建一个分隔符，使得前进和返回的按钮在视觉上产生分离
        self.infoBar.addSeparator()

        #显示当前所在路径的控件
        self.curLocation=QLineEdit()
        self.curLocation.setText('> root') #初始内容
        self.curLocation.setReadOnly(True) #将该文本框设置为只读，用户只能通过她查看当前路径而不能够编辑中间的内容
        # self.curLocation.setStyleSheet("color: white;")
        #图标
        self.curLocation.addAction(QIcon('img/Filefolder.png'), QLineEdit.LeadingPosition)
        #设置显示当前路径的输入框的最小高度
        self.curLocation.setMinimumHeight(35)
        #创建一个QFormLayout对象ptrLayout，用于将路径文本框添加到布局中。
        ptrLayout=QFormLayout()
        #使用addRow方法将路径文本框添加到布局中的一行
        ptrLayout.addRow(self.curLocation)

        ptrWidget=QWidget()

        ptrWidget.setLayout(ptrLayout) 
        ptrWidget.adjustSize()
        #设置自动补全
        self.infoBar.addWidget(ptrWidget)
        self.infoBar.setMovable(False)
    
    #设置左边的文件树UI
    def FileTreeUI(self):
        #左侧的地址栏
        self.tree=QTreeWidget() #引入的是pyQT5中的树控件来显示地址栏
        #设置列数
        self.tree.setColumnCount(1)
        #设置树形组件第一列的标题
        self.tree.setHeaderLabels(['2051498 储岱泽'])
        #建树
        self.buildTree()
        #设置选中状态
        self.tree.setCurrentItem(self.rootItem)
        #设置当前路径
        self.treeItem=[self.rootItem]
        #绑定单击事件，根据用户点击的树形视图项导航到相应路径的功能，并更新界面显示
        self.tree.itemClicked['QTreeWidgetItem*','int'].connect(self.clickFileTreeNode)

        self.grid.addWidget(self.tree,1,0)
    
    #左边显示文件大图标的部分的代码实现
    def basicFileInfoUI(self):
        self.listView=FileListWindow(self.currentNode,parents=self)
        self.listView.setMinimumWidth(750)
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setIconSize(QSize(60,60))
        self.listView.setGridSize(QSize(100,100))
        self.listView.setMovement(QListView.Static)
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.listView.doubleClicked.connect(self.openTheFile)
        #加载当前路径文件
        self.loadCurFile()
        self.grid.addWidget(self.listView, 1, 1)
         #右击菜单
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.show_menu)

    #操作说明
# Operation Instructions
    def OperationIntroduction(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle('Operation Instructions')
        msgBox.setFixedSize(600, 300)  # 设置固定大小
        msgBox.setText('This is the third operating systems project of this semester.\n\n'+
        'The purpose of this project is to implement a file management system with a Windows-like interface using programming languages, simulating strategies used in file management such as FAT table and multi-level directory structure.\n'+
        'Usage:\n'+
        'Left Address Bar: Displays the multi-level directory structure (file tree). Clicking on the file icon in the address bar allows you to navigate to the corresponding internal file (displayed on the right side of the interface).\n'+
        'Open File: Right-click on the file icon to select or double-click the icon to open the file.\n'+
        'Delete File: Right-click on the selected file icon to delete the file.\n'+
        'Properties: Right-click on the file icon to view the properties of the file, right-click on the blank area of the folder to view the properties of the current folder.\n'+
        'Create File: Right-click on the selected area to create a new file or folder.\n'+
        'Rename: Right-click on the file or folder that needs to be renamed to rename it.\n'+
        'Format: Clear all content in the disk.\n'+
        'Navigation Bar: Displays the current folder path.\n'+
        'Back/Forward: Go back to the previous directory/Go to the directory previously visited.\n'+
        '\n'
        )
       
        msgBox.exec_()

    #点击文件树事件
    def clickFileTreeNode(self, item):
        # 创建一个空列表ways，用于存储点击路径的所有项
        ways = [item]

        # 通过循环获取所点击项的所有父项，并将其添加到ways列表中
        temp = item
        while temp.parent() is not None:
            temp = temp.parent()
            ways.append(temp)

        # 将ways列表反转，以便从根节点开始进行路径导航
        ways.reverse()

        # 回退到根节点
        while self.backToTheLastFolder():
            pass
        self.RootUrl = [self.RootUrl[0]]
        self.treeItem = [self.treeItem[0]]

        # 根据ways列表依次导航到点击的路径
        for i in ways:
            if i == self.rootItem:
                continue

            # 前往该路径
            # 从curNode中查询item
            newNode = next((j for j in self.currentNode.children if j.name == i.text(0)), None)

            # 前往路径j
            if newNode.isFile:
                # 文件的话，break即可
                break
            else:
                self.currentNode = newNode
                self.updateLoc()
                self.RootUrl.append(newNode.name)

                # 更新路径
                for j in range(self.treeItem[-1].childCount()):
                    if self.treeItem[-1].child(j).text(0) == newNode.name:
                        selectedItem = self.treeItem[-1].child(j)
                self.treeItem.append(selectedItem)
                self.tree.setCurrentItem(selectedItem)

        # 更新上标
        self.UpdateRootBar()

        if self.currentNode != self.rootNode:
            self.backArrow.setEnabled(True)

        self.forwardArrow.setEnabled(False)
        self.lastLoc = -1


    def updateLoc(self):
        self.loadCurFile()
        self.listView.curNode=self.currentNode

    #打开文件
    def openTheFile(self,modelindex: QModelIndex)->None:
        #获取点击item
        self.listView.close_edit()

        try:
            item = self.listView.item(modelindex.row())
        except:
            #报错，则说明是右键打开方式
            if len(self.listView.selectedItems())==0:
                return
            item=self.listView.selectedItems()[-1]

        #如果可以前进
        if self.lastLoc!=-1 and self.nextStep:
            item=self.listView.item(self.lastLoc)
            self.lastLoc=-1
            self.forwardArrow.setEnabled(False)
        self.nextStep=False

        newNode=None
        for i in self.currentNode.children:
            if i.name==item.text():
                newNode=i
                break

        if newNode.isFile:
            data=newNode.data.read(self.fat,self.disk)
            self.child=FileEditDisplay(newNode.name, data)
            self.child._signal.connect(self.getData)
            self.child.show()
            self.writeFile=newNode
        else:
            #进下一级目录前，如果处于编辑状态，一定要取消编辑
            self.listView.close_edit()

            self.currentNode=newNode
            self.updateLoc()
            self.RootUrl.append(newNode.name)

            #更新路径
            for i in range(self.treeItem[-1].childCount()):
                if self.treeItem[-1].child(i).text(0)==newNode.name:
                    selectedItem=self.treeItem[-1].child(i)
            self.treeItem.append(selectedItem)
            self.tree.setCurrentItem(selectedItem)
            self.backArrow.setEnabled(True)

            self.UpdateRootBar()

    def UpdateRootBar(self):
        self.statusBar().showMessage(str(len(self.currentNode.children))+' projects')
        root=self.calculateCurrentRoot()        
        self.curLocation.setText(root)

    def calculateCurrentRoot(self):
        RootName='> root'
        for i,item in enumerate(self.RootUrl):
            if i==0:
                continue
            RootName+=" > "+item
        return RootName

    def renameTheFile(self):
        if len(self.listView.selectedItems())==0:
            return
        #获取最后一个被选中的
        self.listView.editSelected(self.listView.selectedIndexes()[-1].row())
        self.updateTree()
        
    def deleteTheFile(self):
        # 检查是否有选中项
        if len(self.listView.selectedItems()) == 0:
            return #如果没有选中的项则直接返回

        # 获取选中项和索引
        item = self.listView.selectedItems()[-1]
        index = self.listView.selectedIndexes()[-1].row()

        # 显示确认对话框
        message = QMessageBox()
        message.setWindowTitle('Reminder')
    
        # 根据选中项的类型设置不同的提示文本
        if self.currentNode.children[index].isFile:  #如果选择删除的是文件类型
            message.setText("Are you sure you want to delete the file " + item.text() + "?")
        else:          #如果选择删除的是文件夹类型
            message.setText("Are you sure you want to delete the folder " + item.text() + " and all its contents?")
    
        # 设置对话框按钮
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        Yes = message.button(QMessageBox.Yes)
        Yes.setText('Yes')
        No = message.button(QMessageBox.No)
        No.setText('No')

        message.exec_()

        # 如果点击了取消按钮，则返回
        if message.clickedButton() == No:
            return
        else:
            # 从列表视图中移除选中项
            self.listView.takeItem(index)
            del item

            # 递归删除文件或目录及其子项
            self.deleteFileRecursive(self.currentNode.children[index])

            # 从当前节点的子节点列表中删除选中项
            self.currentNode.children.remove(self.currentNode.children[index])

            # 更新目录表
            self.catalog = self.updateCatalogFile(self.rootNode)

            # 更新树形视图
            self.updateTree()
    #删除文件系统中的文件或目录
    def deleteFileRecursive(self,node):
        if node.isFile:
            node.data.delete(self.fat,self.disk)
        else:
            for i in node.children:
                self.deleteFileRecursive(i)
   

    def updateCatalogFile(self,node):
        if node.isFile:
            return [node]
        else:
            x=[node]
            for i in node.children:
                x+=self.updateCatalogFile(i)
            return x

    def createFolder(self):

        self.item_1=QListWidgetItem(QIcon("img/Filefolder.png"), "新建文件夹")
        self.listView.addItem(self.item_1)
        self.listView.editLast()

        #添加到目录表中
        newNode=CatalogNode(self.item_1.text(),False,self.fat,self.disk,time.localtime(time.time()),self.currentNode)
        self.currentNode.children.append(newNode)
        self.catalog.append(newNode)

        #更新树
        self.updateTree()

    def createFile(self):
        self.item_1=QListWidgetItem(QIcon("img/FileImg.png"), "新建文件")
        self.listView.addItem(self.item_1)
        self.listView.editLast()

        #添加到目录表中
        newNode=CatalogNode(self.item_1.text(),True,self.fat,self.disk,time.localtime(time.time()),self.currentNode)
        self.currentNode.children.append(newNode)
        self.catalog.append(newNode)

        #更新树
        self.updateTree()

    def viewAttribute(self):
        #查看当前路径属性
        if len(self.listView.selectedItems())==0:
            self.child=attributeFormDisplay(self.currentNode.name, False,self.currentNode.createTime,self.currentNode.updateTime,len(self.currentNode.children))

            self.child.show()
            return
        else:
            #获取选中的最后一个
            node=self.currentNode.children[self.listView.selectedIndexes()[-1].row()]
            if node.isFile:
                self.child=attributeFormDisplay(node.name, node.isFile,node.createTime,node.updateTime,0)
            else:
                self.child=attributeFormDisplay(node.name, node.isFile,node.createTime,node.updateTime,len(node.children))
            self.child.show()
            return

    
    def show_menu(self, point):
        menu = QMenu(self.listView)
    
        # 如果有选中的项
        if len(self.listView.selectedItems()) != 0:
            """
            打开文件
            """
            openTheFile = QAction(QIcon(), 'open')
            openTheFile.triggered.connect(self.openTheFile)
            menu.addAction(openTheFile)

            deleteAction = QAction(QIcon(), 'delete')
            deleteAction.triggered.connect(self.deleteTheFile)
            menu.addAction(deleteAction)

            renameAction = QAction(QIcon(), 'rename')
            renameAction.triggered.connect(self.renameTheFile)
            menu.addAction(renameAction)

            viewAttributeAction = QAction(QIcon('img/attribute.png'), 'attribute')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            dest_point = self.listView.mapToGlobal(point)
            menu.exec_(dest_point)
        else:
            
            #查看
            viewMenu = QMenu(menu)
            viewMenu.setTitle('Look')
        
            # 大图标
            bigIconAction = QAction(QIcon(), 'Large')
            bigIconAction.triggered.connect(lambda: self.listView.setIconSize(QSize(180, 180)) or self.listView.setGridSize(QSize(200, 200)))
            viewMenu.addAction(bigIconAction)

            # 中等图标
            middleIconAction = QAction(QIcon(), 'Medium')
            middleIconAction.triggered.connect(lambda: self.listView.setIconSize(QSize(72, 72)) or self.listView.setGridSize(QSize(100, 100)))
            viewMenu.addAction(middleIconAction)

            # 小图标
            smallIconAction = QAction(QIcon(), 'Small')
            smallIconAction.triggered.connect(lambda: self.listView.setIconSize(QSize(56, 56)) or self.listView.setGridSize(QSize(84, 84)))
            viewMenu.addAction(smallIconAction)

            menu.addMenu(viewMenu)

            
            #新建
            createMenu = QMenu(menu)
            createMenu.setTitle('Add')

            # 新建文件夹
            createFolderAction = QAction(QIcon('img/Filefolder.png'), 'Folder')
            createFolderAction.triggered.connect(self.createFolder)
            createMenu.addAction(createFolderAction)

            # 新建文件
            createFileAction = QAction(QIcon('img/FileImg.png'), 'File')
            createFileAction.triggered.connect(self.createFile)
            createMenu.addAction(createFileAction)

            createMenu.setIcon(QIcon('img/create.png'))
            menu.addMenu(createMenu)

            
            viewAttributeAction = QAction(QIcon('img/attribute.png'), 'Attribute')
            viewAttributeAction.triggered.connect(self.viewAttribute)
            menu.addAction(viewAttributeAction)

            self.nextStep = False

            dest_point = self.listView.mapToGlobal(point)
            menu.exec_(dest_point)

    def updateTree(self):
        node=self.rootNode
        item=self.rootItem

        if item.childCount()<len(node.children):
            #增加一个新item即可
            child=QTreeWidgetItem(item)
        elif item.childCount()>len(node.children):
            #一个一个找，删除掉对应元素
            for i in range(item.childCount()):
                if i==item.childCount()-1:
                    item.removeChild(item.child(i))
                    break
                if item.child(i).text(0)!=node.children[i].name:
                    item.removeChild(item.child(i))
                    break

        for i in range(len(node.children)):
            self.updateTreeRecursive(node.children[i], item.child(i))

        self.updateTreeRecursive(node, item)

    def updateTreeRecursive(self,node:CatalogNode,item:QTreeWidgetItem):
        item.setText(0, node.name)
        if node.isFile:
            item.setIcon(0, QIcon('img/FileImg.png'))
        else:
            #根据是否有子树设置图标
            if len(node.children)==0:
                item.setIcon(0, QIcon('img/Filefolder.png'))
            else:
                item.setIcon(0, QIcon('img/Filefolder.png'))
            if item.childCount()<len(node.children):
                #增加一个新item即可
                child=QTreeWidgetItem(item)
            elif item.childCount()>len(node.children):
                #一个一个找，删除掉对应元素
                for i in range(item.childCount()):
                    if i==item.childCount()-1:
                        item.removeChild(item.child(i))
                        break
                    if item.child(i).text(0)!=node.children[i].name:
                        item.removeChild(item.child(i))
                        break
            for i in range(len(node.children)):
                self.updateTreeRecursive(node.children[i], item.child(i))

    def buildTree(self):
        self.tree.clear()
        self.rootItem=self.buildTreeRecursive(self.catalog[0],self.tree)
        #加载根节点的所有子控件
        self.tree.addTopLevelItem(self.rootItem)
        self.tree.expandAll()

    def getData(self, parameter):
        """
        向文件中写入新数据
        """
        self.writeFile.data.update(parameter,self.fat,self.disk)
        self.writeFile.updateTime=time.localtime(time.time())
            
    # 递归建立目录树    
    def buildTreeRecursive(self,node:CatalogNode,parent:QTreeWidgetItem):
        child=QTreeWidgetItem(parent)
        child.setText(0,node.name)

        #如果这个节点是一个文件的话，就给文件的图标
        if node.isFile:
            child.setIcon(0,QIcon('img/FileImg.png'))
        #否则给文件夹的图标
        else:
            child.setIcon(0, QIcon('img/Filefolder.png'))
            for i in node.children:
                self.buildTreeRecursive(i,child)
        
        return child

    #加载当前路径的文件
    def loadCurFile(self):
        self.listView.clear()

        for i in self.currentNode.children:
            if i.isFile:
                self.item_1=QListWidgetItem(QIcon("img/FileImg.png"), i.name)
                self.listView.addItem(self.item_1)
            else:
                if len(i.children)==0:
                    self.item_1=QListWidgetItem(QIcon("img/Filefolder.png"), i.name)
                else:
                    self.item_1=QListWidgetItem(QIcon("img/Filefolder.png"), i.name)
                self.listView.addItem(self.item_1)
   
    #格式化磁盘
    def FormatDisk(self):
        #结束编辑
        self.listView.close_edit()

        #提示框
        reply=QMessageBox()
        reply.setWindowTitle('Reminder')
        reply.setText('Are you sure you want to format the disk? This will erase all data on your disk!')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        Yes = reply.button(QMessageBox.Yes)
        Yes.setText('Yes')
        No = reply.button(QMessageBox.No)
        No.setText('No')
        reply.exec_()
        reply.show()

        if reply.clickedButton()==No:
            return
        
        self.fat=FAT()
        self.fat.fat=[-2]*blockNum
        #存储fat表
        with open('fat','wb') as f:
            f.write(pickle.dumps(self.fat))

        self.disk=[]
        for i in range(blockNum):
            self.disk.append(Block(i))
        #存储disk表
        with open('disk','wb') as f:
            f.write(pickle.dumps(self.disk))
        
        self.catalog=[]
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        #存储
        with open('catalog','wb') as f:
            f.write(pickle.dumps(self.catalog))

        self.hide()
        self.winform=MainWindow()
        self.winform.show()
    
    #将文件保存到本地的disk文件中
    def saveFile(self):
        #存储fat表
        with open('fat','wb') as f:
            f.write(pickle.dumps(self.fat))
        #存储disk表
        with open('disk','wb') as f:
            f.write(pickle.dumps(self.disk))
        #存储
        with open('catalog','wb') as f:
            f.write(pickle.dumps(self.catalog))

#读取之前的信息。
#如果之前没有运行过这个程序，那么会在这里新建fat，disk，catalog的文件
#如果之前运行过了，那就直接读取
    def ReadFilesFromDisk(self):
        #读取fat表
        if not os.path.exists('fat'):
            self.fat=FAT()
            self.fat.fat=[-2]*blockNum
            #存储fat表
            with open('fat','wb') as f:
                f.write(pickle.dumps(self.fat))
        else:
            with open('fat','rb') as f:
                self.fat=pickle.load(f)

        #读取disk表
        if not os.path.exists('disk'):
            self.disk=[]
            for i in range(blockNum):
                self.disk.append(Block(i))
            #存储disk表
            with open('disk','wb') as f:
                f.write(pickle.dumps(self.disk))
        else:
            with open('disk','rb') as f:
                self.disk=pickle.load(f)

        #读取catalog表
        if not os.path.exists('catalog'):
            self.catalog=[]
            self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
            #存储
            with open('catalog','wb') as f:
                f.write(pickle.dumps(self.catalog))
        else:
            with open('catalog','rb') as f:
                self.catalog=pickle.load(f)

    def initial(self):
        # fat表
        self.fat=FAT()
        self.fat.fat=[-2]*blockNum
        #存储fat表
        with open('fat','ab') as f:
            f.write(pickle.dumps(self.fat))
        
        #disk表
        self.disk=[]
        for i in range(blockNum):
            self.disk.append(Block(i))
        #存储disk表
        with open('disk','ab') as f:
            f.write(pickle.dumps(self.disk))
        
        #catalogNode
        self.catalog=[]
        self.catalog.append(CatalogNode("root", False, self.fat, self.disk, time.localtime(time.time())))
        #存储
        with open('catalog','ab') as f:
            f.write(pickle.dumps(self.catalog))
 
    #返回上一级    
    def backToTheLastFolder(self):
        self.listView.close_edit()

        if self.rootNode==self.currentNode:
            #根节点无法返回
            return False

        #记录上次所在位置
        for i in range(len(self.currentNode.parent.children)):
            if self.currentNode.parent.children[i].name==self.currentNode.name:
                self.lastLoc=i
                self.forwardArrow.setEnabled(True)
                break

        self.currentNode=self.currentNode.parent
        self.updateLoc()
        self.RootUrl.pop()
        self.treeItem.pop()
        self.tree.setCurrentItem(self.treeItem[-1])
        self.updateTree()
        self.UpdateRootBar()

        if self.currentNode==self.rootNode:
            self.backArrow.setEnabled(False)
        return True

    def forwardEvent(self):
        self.nextStep=True
        self.openFile(QModelIndex())

    #处理结束事件，用户关闭文件管理器的时候应该要有弹窗
    def closeEvent(self,event):
        self.listView.close_edit()

        reply=QMessageBox()
        reply.setWindowTitle('Reminder')
        reply.setText('Do you want to write this operation to the disk?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
        buttonY = reply.button(QMessageBox.Yes)
        buttonY.setText('Yes')
        buttonN = reply.button(QMessageBox.No)
        buttonN.setText('Cancel')
        buttonI=reply.button(QMessageBox.Ignore)
        buttonI.setText('No')

        reply.exec_()

        if reply.clickedButton()==buttonI:
            event.accept()
        elif reply.clickedButton()==buttonY:
            self.saveFile()
            event.accept()
        else:
            event.ignore()

if __name__=='__main__':
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

