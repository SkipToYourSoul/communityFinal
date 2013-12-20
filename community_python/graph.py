#encoding=utf-8

# graph.py
# simple undirected graph implemenataion with weighted edge
# 初始化graph
#

import csv
import sys

class Graph():

    # __init__
    def __init__(self):
        self.nodeAdj={}                        # node的邻接表 nodeID -> [nodeID,edgeID]
        self.nodeWeight={}                     # node与其他node的边的权重 nodeID -> edgeCount(其中应包含nodeselfWeight)
        self.nodeSelfWeight={}                 # node内部的边的权重
        self.edges={}                          # edge信息 edgeID -> [edgeID,start,end,weight]
        self.totalWeight = float(0.0)          
        
    # addEdge
    # 插入一条边
    def addEdge(self,id, start, end, weight):
        if self.existEdge(start, end):
            return
        self.totalWeight +=  float(weight)
        if start == end:                        # 插入内部链接的点,适用于第二个level以后
            self.nodeSelfWeight[start]=weight
            self.insertNode(start,weight)
        else:
            self.edges[id]=(id, start, end, float(weight))      
            self.installNodeEdge(start, id, end, weight)
            self.installNodeEdge(end, id, start, weight)

    
    # existEdge 
    # 判断该边是否存在
    def existEdge(self, start, end):
        if self.nodeAdj.has_key(start) and self.nodeAdj[start].has_key(end):
            return True
        return False

    # insertNode
    # 为node初始化nodeAdj
    def insertNode(self, node,w=0):
        if self.nodeAdj.has_key(node) == False:
            self.nodeAdj[node] = {}
            self.nodeWeight[node]=0.0
        self.nodeWeight[node]+=w

    # installNodeEdge
    # 完整加入node
    def installNodeEdge(self, node, edgeID, end, weight):
        self.insertNode(node) 
        if self.nodeAdj[node].has_key(end)==False:
            self.nodeAdj[node][end] = edgeID
            self.nodeWeight[node]+=float(weight)

    # getSelfWeight
    
    # 获得node的selfweight
    def getSelfWeight(self, node) :
        if (self.nodeSelfWeight.has_key(node)):
            return self.nodeSelfWeight[node]
        else:
            return 0.0

    # getTotalWeight
    # 每进行一次pass之后totalWeight会增加，因为node的inWeight呈double增加
    def getTotalWeight(self):
        return self.totalWeight
    
    # nodes
    # 获取节点集
    def nodes(self):
        return self.nodeAdj.keys()

    # neighbours
    # 获取一个节点相邻的节点，返回(node, edgeID)
    def neighbours(self, node):
        return self.nodeAdj[node].items()

    # neighWeight
    # 获得node的边的权重和，应该包括selfloop以及跟其他点链接的边
    def neighWeight(self, node):
        return self.nodeWeight[node]

    # getEdge
    def getEdge(self, id):
        return self.edges[id]

    # nodeSize
    def nodeSize(self):
        return len(self.nodeAdj)

    # edgeSize
    def edgeSize(self):
        return len(self.edges)

    # printGraph
    def printGraph(self):
        print "graph:*****************"
        for node in self.nodes():
            print node,": ",self.nodeAdj[node]
            adjStr = str.format("%s -> "%(node))
            for edgePair in self.neighbours(node):
                edge = self.getEdge(edgePair[1])
                adjStr+=str.format("(%s|%f),"%(edgePair[0], edge[3]))
            if self.getSelfWeight(node) > 0.0:
                adjStr += str.format("(%s|%f),"%(str(node), self.getSelfWeight(node)))
            print adjStr
            print "nodeWeight: ",self.nodeWeight[node]
            print "----------------"
        print "***********************"

def csvTest():
    csvReader = csv.reader(file(sys.argv[1],'rb'), csv.excel_tab)
    i = 0
    g = Graph()
    for line in csvReader:
        edgeArr = line
        g.addEdge(i, edgeArr[0], edgeArr[1], 1.0)
        i+=1
    g.printGraph()

def Test():
    g = Graph()
    g.addEdge(0 ,1 ,2, 3)
    g.addEdge(1, 2, 3, 3) 
    g.addEdge(2, 1, 3, 3)
    g.addEdge(3, 4, 4, 3)
    g.printGraph()
    print g.edgeSize()
    print g.getSelfWeight(1)
    print g.getSelfWeight(2)
    print g.getSelfWeight(3)
    print g.getSelfWeight(4)

if __name__ == "__main__":
    # csvTest()
    Test()
    
