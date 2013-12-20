#encoding=utf-8

# community.py
# 包含了关于community的所有操作
#
# Cluster的modularity的值:
# A(ij)(内部边的权重之和)
# k(i)*k(j)/m2: 所有内部节点的边的权重和的平方除以m2
#
#TODO: 目前初始的community是随机决定的，如果根据用户打的label计算一个初始的community,
#      或者每条边的权重等于两个节点label的jaccard距离，那么结果会不会更好?
#

import random
from graph import Graph

class Community():
    
    # __init__
    # min_modularity:modularity增加的最小值，增加的值必须大于该值步骤才有意义
    # minC:最多存在k个cluster
    # maxLevel:level执行的最大次数
    def __init__(self, graph, min_modularity, minC, maxLevel):
        self.g = graph
        self.n2c={}                                       # node -> community_id
        self.tot={}                                       # cluster中所有节点的nodeWeight之和
        self.inw={}                                       # cluster内部的边之和
        self.min_modularity = min_modularity 
        self.minC = minC
        self.neigh_weight={}                              # node_neigh_comm -> weight 某个node跟其所有neigh_comm中边的条数
        self.maxLevel = maxLevel
        
        #初始化一个community的分配
        for node in self.g.nodes():
            self.n2c[node]= node
            self.tot[node] = self.g.neighWeight(node)
            self.inw[node] = self.g.getSelfWeight(node)
            self.neigh_weight[node]=-1
        #运行状态
        self.neigh_last = 0                               # node的邻community的个数
        self.neigh_pos={}                                 # 存储node的邻community的community_id
        

    # modularity_gain
    # comm:该node所加入的community
    # dnodecomm:该node与要加入的community里所有的node链接的边的权重
    # w_degree:一个node的nodeWeight
    def modularity_gain(self, node, comm, dnodecomm, w_degree):
        totc=self.tot[comm]
        m2=self.g.getTotalWeight()*2
        return dnodecomm - totc*w_degree/(m2)

    # printCommunity
    
    def printCommunity(self):
        for i in self.g.nodes():
            print "node %s: cluster %s"%(i, self.n2c[i])

    # remove
    def remove(self, node, comm, dnodecomm):
        self.tot[comm] -= self.g.neighWeight(node)
        self.inw[comm] -= 2*dnodecomm + self.g.getSelfWeight(node)
        self.n2c[node] = -1

    # insert 
    # node:节点
    # comm:要插入的comm
    # dnodecomm:该node与要加入的community里所有的node链接的边的权重
    def insert(self, node,  comm, dnodecomm):
        self.tot[comm] += self.g.neighWeight(node)
        self.inw[comm]  += 2*dnodecomm + self.g.getSelfWeight(node)
        self.n2c[node]=comm

    # modularity
    # 计算modularity
    def modularity(self):
        q = 0.0
        m2 = self.g.getTotalWeight()*2.0
        for node in self.g.nodes():
            if (self.tot[node] > 0):
                q +=self.inw[node]/m2 - (self.tot[node]/m2)*(self.tot[node]/m2)
        return q

    # neigh_comm
    
# 计算node邻近的neighbor community的权重
    def neigh_comm(self, node):
        # 将运行状态初始化
        for i in range(0, self.neigh_last):
           self.neigh_weight[self.neigh_pos[i]]= -1
        self.neigh_last = 0
        # 该node本身的信息
        self.neigh_pos[0]=self.n2c[node]
        self.neigh_weight[self.neigh_pos[0]]=0
        self.neigh_last = 1

        for (neighbor, edgeID) in self.g.neighbours(node):
            edge = self.g.getEdge(edgeID)
            neigh_comm=self.n2c[neighbor]
            neigh_w=edge[3]
            if (neighbor!= node):
                if (self.neigh_weight[neigh_comm]== -1):               # 若为新的community  
                    self.neigh_weight[neigh_comm] = 0.0
                    self.neigh_pos[self.neigh_last] = neigh_comm
                    self.neigh_last += 1
                self.neigh_weight[neigh_comm]+=neigh_w                 # 若不是新community,叠加neigh_weight

    # oneLevel
    # 执行一遍community detection算法
    # 控制条件cont,improvement.其中improvement值得考虑
    def oneLevel(self):
        improvement=False
        nb_moves=0
        nb_pass_done=0
        new_mod = self.modularity()
        size = self.g.nodeSize()

        # 生成一个随机顺序
        random_order=[]
        for node in self.g.nodes():
            random_order.append(node)
        for i in range(0, size):
            #随机一个i之后的位置
            rand_pos = random.randint(0, size-i - 1) + i 
            tmp = random_order[i]
            random_order[i] = random_order[rand_pos]
            random_order[rand_pos]=tmp
            
        cont = True
        while (cont):
            cur_mod = new_mod
            nb_moves= 0
            nb_pass_done+=1
            
            for node_tmp in range(0, size):                                         #遍历每个节点，try to switch它的community
                node = random_order[node_tmp] 
                node_comm = self.n2c[node]
                w_degree = self.g.neighWeight(node)
                
                self.neigh_comm(node)                                               # 找到该node的相邻community的信息
                self.remove(node, node_comm, self.neigh_weight[node_comm])          # 将该node从本来的community中移除
                
                best_comm = node_comm
                best_nblinks=0.0                                                    #更新modularity时用到，需要增加该comm的weight
                best_increase=0.0

                for i in range(0,  self.neigh_last):
                    increase = self.modularity_gain(node, self.neigh_pos[i], self.neigh_weight[self.neigh_pos[i]], w_degree)
                    if (increase > best_increase):                                  # 找到最佳的increase
                        best_comm = self.neigh_pos[i]
                        best_nblinks = self.neigh_weight[self.neigh_pos[i]]
                        best_increase = increase

                self.insert(node, best_comm, best_nblinks)                          # 将该点插入最佳的community
       
                if (best_comm != node_comm):                                        # 弱node加入了另一个community
                    nb_moves+=1

            #total_tot=0.0
            #total_inw=0
            #for node in self.g.nodes():
                #total_tot += self.tot[node]
                #total_inw += self.inw[node]
            
            new_mod = self.modularity()
            if (nb_moves > 0):
                improvement = True
            
            print "nb_moves:%d"%(nb_moves)
            print "pre:%f, cur:%f,modularity gap:%f"%(cur_mod, new_mod,new_mod - cur_mod)
            if (improvement and (new_mod - cur_mod) > self.min_modularity):
                cont = True
            else:
                cont= False
        # end while
        print "#### new graph size:%d"%(self.g.nodeSize())
        print "#### cluster size:%d"%(self.clusterSize())
        print  "#### actual cluster size:%d"%(self.actualClusterSize())
        print "-------------------------------------"
        return improvement

    # genNextCommTask
    # 生成由当前graph的cluster构成的图
    def genNextCommTask(self,edgeCount):
        # 节点: cluster
        # 边: selfloop和节点之间的边
        newEdgeMap={}                                       # newEdgeMap：{(start,end):weight}
        for node in self.g.nodes():                         # 遍历所有的点
            for edgePair in self.g.neighbours(node):        # 遍历该点的neighbor
                edge = self.g.getEdge(edgePair[1])
                oCluster= self.n2c[edgePair[0]]
                newNode=(self.n2c[node], oCluster)          # 以community为start或end来建立新的network
                if newEdgeMap.has_key(newNode):
                    newEdgeMap[newNode]+=edge[3]
                else:
                    newEdgeMap[newNode]=edge[3]
        
        graph=Graph()
        i = edgeCount+1
        for (edge, weight) in newEdgeMap.items():
            graph.addEdge(i, edge[0], edge[1],weight)
            #test print ,remember delete
            print i,edge[0],edge[1],weight
            i+=1

        comm = Community(graph, self.min_modularity, self.minC, self.maxLevel)
        print graph.printGraph()
        return comm

    #------------------------------------------------------------------
    # 以下4个函数为处理数目较少的cluster的函数,未用
    
    def clusterSize(self):
        clusters=set()
        for (node, cluster) in self.n2c.items():
            clusters.add(cluster)
        return len(clusters)
    
    def postProcess(self):
        outlier =self.outlierComm()
        for node in self.n2c:
            if self.n2c[node] in outlier:
                self.n2c[node]="$outlier$"

    #过小的community视为异常点
    def outlierComm(self):
        cSize={}
        
        #记录每个cluster有几个node
        for (node, cluster) in self.n2c.items():
            if cSize.has_key(cluster):
                cSize[cluster]+=1
            else:
                cSize[cluster]=1
        #按node升序排列
        cSize=sorted(cSize.iteritems(), key=lambda x:x[1], reverse=False)
        
        threshold = 0.1*self.g.nodeSize()
        i = 0
        sum=0
        outlier=set()
        for (c, s) in cSize:
            sum+= s
            i+=1
            if sum < threshold:
                outlier.add(c)
        return outlier

    def actualClusterSize(self):
        cSize={}
        for (node, cluster) in self.n2c.items():
            if cSize.has_key(cluster):
                cSize[cluster]+=1
            else:
                cSize[cluster]=1
        cSize=sorted(cSize.iteritems(), key=lambda x:x[1], reverse=True)
        
        threshold = 0.8*self.g.nodeSize()
        i = 0
        sum=0
        for (c, s) in cSize:
            sum+= s
            i+=1
            if sum >= threshold:
                break
        return i+1

    #--------------------------------------------------------------------------------

    # startCluster
    # 主要函数,执行所有操作
    def startCluster(self):
        self.oneLevel()
        self.g.printGraph()
        
        #将数量较少的cluster处理掉
        #self.postProcess()
        
        cMapChain=[]
        cMapChain.append(self.n2c)             # 存储所有的node->cluster的关系
        
        curTask = self
        i = 1
        curTask.printCommunity()
        #test print ,remember delete
        #self.g.printGraph()
        edgeCount = 0
        
        # 执行下一次level的判定条件,应与improve有关,后期需修改
        while curTask.clusterSize() > self.minC and i < self.maxLevel:    
            print "start level:%d"%(i)
            edgeCount += self.g.edgeSize()
            curTask = curTask.genNextCommTask(edgeCount)
            curTask.oneLevel()
            #curTask.postProcess()
            curTask.printCommunity()
            cMapChain.append(curTask.n2c)
            i+=1
        #print cMapChain
        lastMap = cMapChain.pop()            # 存储了最开始的所有node是属于最后的哪一个cluster
        while len(cMapChain) > 0:
            topMap = lastMap
            lastMap = cMapChain.pop()
            for node in lastMap.keys():
                if topMap.has_key(lastMap[node]):
                    lastMap[node]=topMap[lastMap[node]]
        #print lastMap

    def startCluster1(self):
        edgeCount = 0
        curTask = self
        while curTask.oneLevel() and curTask.clusterSize() > self.minC:
            edgeCount += self.g.edgeSize()
            curTask = curTask.genNextCommTask(edgeCount)
            curTask.printCommunity()
        curTask.printCommunity()
            
#
#  下面运行的是论文中的实例
#
if (__name__ == "__main__"):
    g = Graph()
    g.addEdge(1, 0, 2, 1)
    g.addEdge(2, 0, 3, 1)
    g.addEdge(3, 0, 4, 1)
    g.addEdge(4, 0, 5, 1)
    g.addEdge(5, 1, 2, 1)
    g.addEdge(6, 1, 4, 1)
    g.addEdge(7, 1, 7, 1)
    g.addEdge(8, 2, 4, 1)
    g.addEdge(9, 2, 5, 1)
    g.addEdge(10, 3, 7, 1)
    g.addEdge(11, 4, 10, 1)
    g.addEdge(12, 5, 7, 1)
    g.addEdge(13, 5, 11, 1)
    g.addEdge(14, 6, 7, 1)
    g.addEdge(15, 6, 11, 1)
    g.addEdge(16, 8, 9, 1)
    g.addEdge(17, 8, 10, 1)
    g.addEdge(18, 8, 11, 1)
    g.addEdge(19, 8, 14, 1)
    g.addEdge(20, 8, 15, 1)
    g.addEdge(21, 9, 12, 1)
    g.addEdge(22, 9, 14, 1)
    g.addEdge(23, 10, 11, 1)
    g.addEdge(24, 10, 12, 1)
    g.addEdge(25, 10, 13, 1)
    g.addEdge(26, 10, 14, 1)
    g.addEdge(27, 11, 13, 1)
      
    print "node size:%d"%(g.nodeSize())
    for i in g.nodes():
        print "node %d"%(i)
    comm = Community(g, 0.2, 2,3)
    comm.startCluster1()
    #comm.oneLevel()
    #comm.printCommunity()
    
    
