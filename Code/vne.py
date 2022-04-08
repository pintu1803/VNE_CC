############################################
#Author of code: Pintu and Vivek
#Roll.No.: 181CO139 and 181CO159
############################################

import networkx as nx
import random
import graph
from graph import Parameters
from matplotlib import pyplot as plt

#this function creates the VN: Virtual networks.
#min_nodes: minimum nodes in a request.
# max_nodes: maximum nodes in a reques.
# no_requests: number of requests known in advance
# probability: prob.
# if no_requests: 1 then it is substrate.
def create_vne(min_nodes=4, max_nodes=8, no_requests=5, probability=0.4):
    #create a list of N embedding request with randomly selected no. of nodes.
    random_node_list = [random.randint(min_nodes, max_nodes) for i in range(no_requests)]

    #the Erdos–Rényi model is method in networkx for generating random graph.
    #it takes two parameters: n=nodes, p=probability, total edges= p*n(n-1)/2
    #to_dict_of_lists(), Returns adjacency representation of graph as a dictionary of lists.
    #it takes 2 arg, 1: Graph, 2: nodelist, optional.
    #v1:[v2, v4, v8], dictionary of lists: value is the list, not key.
    new_vne_req = []
    for req in random_node_list:
        # the Erdos–Rényi model is method in networkx for generating random graph.
        # it takes two parameters: n=nodes, p=probability, total edges= p*n(n-1)/2
        G = nx.erdos_renyi_graph(req, probability, directed=False)
        nx.draw(G, with_labels=True)
        #plt.show()
        # to_dict_of_lists(), Returns adjacency representation of graph as a dictionary of lists.
        # v1:[v2, v4, v8], dictionary of lists: value is the list, not key.
        ng = nx.to_dict_of_lists(G)
        #print(ng)

        #copy this adj list of graph into another dict {g}
        #node value begins with 1, so add 1.
        g = {}
        for i in ng:
            g[i + 1] = []
            for j in ng[i]:
                g[i + 1].append(j + 1)

        #if graph is not connected then do following.
        if not nx.is_connected(G):

            # create a list of all nodes which don't have any edge or empty adj list
            null_node_list = [key for key, val in g.items() if not val]

            # count the edge of each node, size of adj list of each node.
            # create a dict=> node:no_of_edges, for all nodes.
            graph_node_count = {_key: len(_val) for _key, _val in g.items()}

            # sort the dict in decreasing order of number of edges of nodes.
            sorted_dict_list = sorted(graph_node_count.items(), key=lambda x: x[1], reverse=True)

            #if no. of null nodes != total no. of nodes ->
            if len(null_node_list) != len(g):
                #assign an index to each node.
                for index, empty_node in enumerate(null_node_list):
                    #add this null node to the first adj node
                    #of indexed node from sorted dict.
                    #cause: we want connected graphs, and automatic tool may fail to do so,
                    #due to prob. restriction.
                    g[sorted_dict_list[index][0]].append(empty_node)
                    g[empty_node].append(sorted_dict_list[index][0])

            # if no. of null nodes == total no. of nodes ->
            else:
                for i in range(len(g)):
                    for j in range(len(g) - i - 1):
                        #if [j+1] does not belong to adj list of [j] ->
                        if null_node_list[j + 1] not in g[null_node_list[j]]:
                            g[null_node_list[j]].append(null_node_list[j + 1])

                        #if [j] does not belong to adj list of [j+1] ->
                        if null_node_list[j] not in g[null_node_list[j + 1]]:
                            g[null_node_list[j + 1]].append(null_node_list[j])
        # print(g)
        # list of req; just graphs, no weightage.
        new_vne_req.append(g)

    # print("new VNE REQ is=",new_vne_req)

    # weightage is assigned here.

    #this returns the list of requested networks.
    vne = []

    #i: ith req.
    for i in range(len(new_vne_req)):
        edges = set()
        nodes = len(new_vne_req[i])

        #j: jth node of ith req.
        for j in range(nodes):

            #k: kth edge of jth node of ith req.
            for k in new_vne_req[i][j + 1]:
                edges.add((str(j), str(k - 1)))

        #Graph assigns the weight and appends in vne list of REQUESTS.
        vne.append(graph.Graph(nodes, edges, Parameters(10, 25, 10, 25)) )  # for vne request only

        # this returns the substrate networks.
        if (no_requests == 1):
            return graph.Graph(nodes, edges, Parameters(100, 250, 100, 250)), new_vne_req  # for substrate.

    return vne, new_vne_req

################################################################################################
if __name__ == "__main__":
    create_vne()
