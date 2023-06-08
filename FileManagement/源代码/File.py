
#每个物理块大小
blockSize=512
#磁盘中物理块个数
blockNum=512

#磁盘中的物理块
class Block:
    def __init__(self,blockIndex:int,data=""):
        #编号
        self.blockIndex=blockIndex
        #数据
        self.data=data
    
    def isFull(self):
        return len(self.data)==blockSize
    
    def read(self):
        return self.data

    def append(self,newData:str)->str:
        remainSpace=blockSize-len(self.data)
        if remainSpace>=newData:
            return ""
        else:
            self.data+=newData[:remainSpace]
            return newData[remainSpace:]
    
    def clear(self):
        self.data=""

    def write(self,newData:str):
        self.data=newData[:blockSize]
        return newData[blockSize:]

class FAT:

#它创建一个空的FAT表，长度为blockNum，并将所有表项初始化为-2。
    def __init__(self):
        self.fat=[]
        for i in range(blockNum):
            self.fat.append(-2)

#这个方法用于在FAT表中查找空闲的表项（块）。
# 它遍历FAT表，找到第一个值为-2（表示空闲）的表项，并返回其索引。
# 如果找不到空闲表项，则返回-1。
    def findBlank(self):
        for i in range(blockNum):
            if self.fat[i]==-2:
                return i
        return -1
    
#这个方法用于将数据写入FAT表和磁盘。
# 它接收要写入的数据和磁盘对象作为参数。并更新FAT表中的相应表项。方法会在FAT表中建立起一个链表结构，记录文件数据在磁盘上的存储位置。
    def write(self,data,disk):        
        start=-1
        cur=-1

        while data!="":
           # 方法首先查找空闲表项（调用findBlank()方法）
            newLoc=self.findBlank()
            #如果磁盘空间不足，会引发异常。
            if newLoc==-1:  #返回-1说明磁盘满了
                raise Exception(print('磁盘空间不足!'))
                return
            if cur!=-1:    
                self.fat[cur]=newLoc
            else:
                start=newLoc
            cur=newLoc
            #如果找到空闲表项，则将数据写入磁盘的对应块中（调用disk[cur].write(data)）
            data=disk[cur].write(data)
            self.fat[cur]=-1

        return start
        
    #这个方法用于删除FAT表和磁盘上的文件数据。
    def delete(self,start,disk):
        if start==-1:
            return

        while self.fat[start]!=-1:
            disk[start].clear()
            las=self.fat[start]
            self.fat[start]=-2
            start=las

        self.fat[start]=-2
        disk[start].clear()
# 清空以start开始的fat表以及磁盘空间，然后再重新写入
    def update(self,start,data,disk):
        self.delete(start, disk)
        return self.write(data, disk)
#读取从start开始的文件内容
    def read(self,start,disk):
        data=""
        while self.fat[start]!=-1:
            data+=disk[start].read()
            start=self.fat[start]
        data+=disk[start].read()
        return data
        
class FCB:
    def __init__(self,name,createTime,data,fat,disk):
        #文件名
        self.name=name
        #创建时间
        self.createTime=createTime
        #最后修改时间
        self.updateTime=self.createTime

        #根据data为其分配空间
        self.start=-1
    
    def read(self,fat,disk):
        if self.start==-1:
            return ""
        else:
            return fat.read(self.start,disk)
    
    def update(self,newData,fat,disk):
        self.start=fat.update(self.start,newData,disk)
    
    def delete(self,fat,disk):
        fat.delete(self.start,disk)
    
#多级目录结点   
class CatalogNode:
    def __init__(self,name,isFile,fat,disk,createTime,parent=None,data=""):
        #路径名
        self.name=name
        #是否为文件类型
        self.isFile=isFile
        #父结点
        self.parent=parent
        #创建时间
        self.createTime=createTime
        #更新时间
        self.updateTime=self.createTime

        #文件夹类型
        if not self.isFile:
            self.children=[]
        else:
            self.data=FCB(name, createTime, data, fat, disk)
    
        