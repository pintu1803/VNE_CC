############################################
#Author of code: Pintu and Vivek
#Roll.No.: 181CO139 and 181CO159
############################################

import random
import time

class Parameters:
    def __init__(self, lower_edge, upper_edge, lower_node, upper_node) -> None:
        self.lower_edge = lower_edge
        self.upper_edge = upper_edge
        self.lower_node = lower_node
        self.upper_node = upper_node


#this class assigns the weight to nodes and edges.
#weight for node: CPU power
#weight for edge: LINK capacity.
#nodes: [1,2,3,4] list of all nodes.
#edges: [(1,2), (3,4), (5,1)] list of all edges.
class Graph:
    def __init__(self, nodes, edges, parameters) -> None:
        lower_edge = parameters.lower_edge
        upper_edge = parameters.upper_edge
        lower_node = parameters.lower_node
        upper_node = parameters.upper_node
        self.nodes = nodes
        self.edges = edges
        self.neighbours = dict()
        self.node_weights = dict()
        self.edge_weights = dict()
        self.parameters = parameters

        #assign weight to edges.
        for a, b in edges:
            self.edge_weights[(a, b)] = random.randint(lower_edge, upper_edge)
            self.edge_weights[(b, a)] = self.edge_weights[(a, b)]

        #assign weight to nodes.
        for i in range(self.nodes):
            self.node_weights[i] = random.randint(lower_node, upper_node)

        #create adjacency list for each node.
        for i in range(self.nodes):
            self.neighbours[i] = set()
            for a, b in self.edges:
                if int(a) == i:
                    self.neighbours[i].add(b)


    #Returns all possible paths between src and dst.
    def findPaths(self, s, d, visited, path, all_paths, weight):
        #time_out = time.time()
        ##   return
        visited[int(s)] = True
        path.append(s)
        if s == d:
            # print("Path = ",path)#added
            all_paths.append(path.copy())
            #return#added
        else:
            for i in self.neighbours[int(s)]:
                if visited[int(i)] == False and self.edge_weights[(str(s), i)] >= weight:#changed:[(str(s), i)]
                    self.findPaths(i, d, visited, path, all_paths, weight)

        path.pop()
        visited[int(s)] = False

    #Returns any one path randomly b/w src and dst.
    def findPathFromSrcToDst(self, s, d, weight):

        all_paths = []
        visited = [False] * (self.nodes)
        path = []
        self.findPaths(s, d, visited, path, all_paths, weight)
        if all_paths == []:
            return []
        else:
            return all_paths[random.randint(0, len(all_paths) - 1)]

    #Returns true if there exist a path from src to dst.
    def BFS(self, src, dest, v, pred, dist, weight):
        queue = []
        visited = [False for i in range(v)]
        for i in range(v):
            dist[i] = 1000000
            pred[i] = -1
        visited[int(src)] = True
        dist[int(src)] = 0
        queue.append(src)
        while (len(queue) != 0):
            u = queue[0]
            queue.pop(0)
            for i in self.neighbours[int(u)]:
                if visited[int(i)] == False and self.edge_weights[(str(u), i)] >= weight:#changed: [(str(u), i)] 
                    visited[int(i)] = True
                    dist[int(i)] = dist[int(u)] + 1
                    pred[int(i)] = u
                    queue.append(i)
                    if (i == dest):
                        return True

        return False

    #Returns the shortest path from src to dst.
    def findShortestPath(self, s, dest, weight):
        v = self.nodes
        pred = [0 for i in range(v)]
        dist = [0 for i in range(v)]
        ls = []
        if (self.BFS(s, dest, v, pred, dist, weight) == False):
            return ls
        path = []
        crawl = dest
        crawl = dest
        path.append(crawl)

        while (pred[int(crawl)] != -1):
            path.append(pred[int(crawl)])
            crawl = pred[int(crawl)]

        for i in range(len(path) - 1, -1, -1):
            ls.append(path[i])

        return ls


#######################################################################