#encoding=utf-8

import random
import struct
from graph import Graph
from community import Community
import csv
import sys

def Test():
    f = open("C:/Users/CBD_20/Desktop/community/Community_c++/graph.bin","rb")
    size = struct.unpack('i', f.read(4))
    g = Graph()
    
    for i in range(0, size[0]):
       #print "degree: %d"%(struct.unpack('l', f.read(8))[0])
        i

    print "size: %d"%(size[0])
    for i in range(0, size[0]):
        start = struct.unpack('l', f.read(4))
        end = struct.unpack('l', f.read(4))
        g.addEdge(i, start[0], end[0], 1)
        #print "edge: %d -> %d"%(start[0], end[0])
    f.close()
    print "node size:%d"%(g.nodeSize())
    comm = Community(g, 0.5, 5, 5)
    comm.oneLevel()
    comm.printCommunity()

if (__name__ == "__main__"): 
    csvReader = csv.reader(file(sys.argv[1],'rb'), csv.excel_tab)
    i = 0
    g = Graph()
    for line in csvReader:
        edgeArr = line
        g.addEdge(i, edgeArr[0], edgeArr[1], 1.0)
        i+=1

    comm = Community(g, 0.01, 10, 3)
    comm.startCluster() 

