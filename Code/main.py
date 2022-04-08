############################################
#Author of code: Pintu and Vivek
#Roll.No.: 181CO139 and 181CO159
############################################

from re import S, T
from numpy import delete
from graph_extraction import Extract
import random
import copy
import sys
import time
import pickle

# create a text file for storing the result
file = open('mappingfile.txt', 'w')


#################################################
#substrate network and virtual n/w request
#are passed as parameters, the candidate
#sets are generated for each virtual node.
#################################################
# Generate the list of candidate nodes for mapping
def candidate_search(substrate, vn):
    # no. of nodes in substrate network.
    subs_nodes = substrate.nodes
    # weight of each node of subs. n/w.
    subs_weights = substrate.node_weights

    # get no. of nodes in req.
    vn_nodes = vn.nodes
    # get weights of VN req.
    vn_node_weights = vn.node_weights
    # subs candidate for each node of this req.
    candidate_set = dict()

    # assume req is not rejected.
    rejected = False

    # traverse the req.
    for j in range(vn_nodes):
        # subs candidates of each node of this req.
        candidates = []

        # traverse the substrate n/w.
        for k in range(subs_nodes):
            if subs_weights[k] >= vn_node_weights[j]:
                candidates.append(k)

        # if candidate set is empty then reject the req.
        if len(candidates) == 0:
            rejected = True
            break
        else:
            candidate_set[j] = candidates

    return candidate_set, rejected
####################################################



####################################################
#substrate: object of Graph, used to call findPaths() function
#candidate_set: input for validating cand. set
#vir_net_adj_list: to get neighbours of virtual nodes.
#vn_edge_weights: to get link capacity, b/w two v.nodes
####################################################
def candidate_validation(substrate, candidate_set, vir_net_adj_list, vn_edge_weights):
    Candidate_Set = dict()
    for i in range(len(candidate_set)):
        candidates = []
        # print(vir_net_adj_list)
        # print(vn_edge_weights)
        neighbours = vir_net_adj_list[i + 1]  ##keyerror, use increased index
        for cand in candidate_set[i]:
            should_I_reject = False
            for neighbour in neighbours:
                # print("Neighbour = ",neighbour)
                candidates_of_neighbour = candidate_set[neighbour - 1]  ##keyerror, use decreased index
                link_cap = vn_edge_weights[(str(i), str(neighbour - 1))]  ##keyerror, use decreased index
                should_I_drop_this_cand = True
                for cand_of_neigh in candidates_of_neighbour:
                    visited = {i: False for i in range(substrate.nodes)}
                    path = []
                    all_paths = []
                    weight = link_cap
                    time_in = time.time()
                    substrate.findPaths(cand, cand_of_neigh, visited, path, all_paths, weight)#, time_in
                    # make sure there is no loop in the graph.
                    # print("Paths= ",all_paths)
                    #path exist from v1 to Vi neigbour, check for other neighbours.
                    if len(all_paths) > 0:
                        should_I_drop_this_cand = False
                        break
                    #break this loop, no need to check for other candidates for this neigbour.

                #if path from cand. v1 to cand. Vi does not exist, then cand is invalid.   
                if should_I_drop_this_cand == True:
                    should_I_reject = True
                    break
                #if path exist, then this neighbour is clear, go for others.
                else:
                    continue
            if should_I_reject == False:
                candidates.append(cand)
        Candidate_Set[i] = candidates
    return Candidate_Set
###############################################


###############################################
#function to sort dict in increasing order of length of its values.
def sort(Candidate_Set):
    CandidateSet=dict()
    Set=sorted(Candidate_Set, key=lambda k: len(Candidate_Set[k]))
    for key in Set:
        CandidateSet[key]=Candidate_Set[key]
    return CandidateSet
###
#it will assign the common candidate node
#to that virtual node which has least
#number of candidates in its list.
###
def candidate_uniquify(Candidate_Set):
    Candidate_Set=sort(Candidate_Set)
    # print("Sorted dict=",Candidate_Set)
    # print("Type of dict=",type(Candidate_Set))
    while(1):
        first_pair=next(iter((Candidate_Set.items())) )
        key=first_pair[0]
        items=first_pair[1]
        # print("\nBegin:: For key:items ={}:{}".format(key,items))
        index=0
        deleted=0
        for k,i in Candidate_Set.items():
            index+=1
            if(index==1):
                continue
            for item in items:
                if item in i:
                    i.remove(item)
                    deleted+=1
                    break
        # print("Deleted=",deleted)
        if deleted ==0:
            return Candidate_Set
        # print("After this iteration=",Candidate_Set)
        Candidate_Set=sort(Candidate_Set)
###############################################



###############################################
#path=[[1,4,2], [0,3]]
#two disjoint path segments.
def path_decomposition(virtual_network):
    n=virtual_network.nodes
    edges=list(virtual_network.edges)
    # print("Edges=",type(edges),len(edges))
    visited=[]
    path_seg=[]
    # start='0'
    while len(visited)!=n:
        #find the start node.
        for edge in edges:
            edge=list(edge)
            if edge[0] not in visited:
                start=edge[0]
        ##
        path=[]
        path.append(start)
        visited.append(start)

        m=len(edges)
        
        # print("Edges count=",m)
        while (1):
            i=-1
            found_next_node=False
            for edge in edges:
                i+=1
                # print("i=edge=",i)
            
                edge=list(edge)
                # print("Edges accessed=",edge)
                if start == edge[0]:
                    if edge[1] not in visited:
                        visited.append(edge[1])
                        path.append(edge[1])
                        start=edge[1]
                        edges.pop(i)
                        m=len(edges)
                        # print("M value up=",m)
                        found_next_node=True
                        break
            if found_next_node==True:
                continue
            else:
                path_seg.append(path)
                #path terminated, find next
                break
            
    return path_seg
##################################



###############################################
def forward_propagation(Cand_Set_util, substrate, vn, path_seg):
    Cand_Set=dict()
    #create multi-layer graph.
    for i in path_seg:
        Cand_Set[int(i)]=Cand_Set_util[int(i)]
    ##
    local_state=dict()
    global_state=dict()
    # path_segment=path_seg[]
    #calc local state of each node of each layer.
    index=0
    temp_dict=dict()
    temp_ind=-1
    for ind, nodes in Cand_Set.items():
        sum=0
        for node in nodes:
            sum+=substrate.node_weights[node]
        for node in nodes:
            local_state[node]=substrate.node_weights[node]/sum
            #calc global states for first layer
            if index==0:
                temp_ind=ind
                temp_dict[node]=local_state[node]
        index+=1

    #insert global state of first layer in dict format.
    global_state[temp_ind]=temp_dict

    #declare the intermediate data str.
    path_length=dict()
    link_weights=dict()
    multi_layers = list(Cand_Set.items())
    prev_layer=multi_layers[0][1]
    layers=len(Cand_Set)

    #computation for 2nd layer onwards.
    for i in range(1, layers):
        vn_index=multi_layers[i][0]
        # print("vn=",vn_index, type(vn_index))
        vn_global=dict()
        next_layer=multi_layers[i][1]
        #campute path lengths.
        max_path=0
        for prev in prev_layer:
            for next in next_layer:
                ls=substrate.findShortestPath(prev, next, vn.edge_weights[(path_seg[i-1], path_seg[i])])#[(str(prev), str(next))]
                path_length[(prev, next)]=len(ls)
                if len(ls)>max_path:
                    max_path=len(ls)
        #compute link weights.
        for prev in prev_layer:
            for next in next_layer:
                link_weights[(prev, next)]=1-(path_length[(prev, next)]/(max_path+2*pow(10,-6)))
        #compute global states.
        for next in next_layer:
            node=prev_layer[0]
            mx_wt=link_weights[(node,next)]
            for prev in prev_layer:
                if link_weights[(prev, next)]>mx_wt:
                    mx_wt=link_weights[(prev, next)]
                    node=prev
            vn_global[next]=[local_state[next]*mx_wt, node]
        #insert the global list into dict
        global_state[vn_index]=vn_global
        #make this layer as prev and move on to next layer.
        prev_layer=next_layer
    
    #return the result.
    return global_state
####################################################################




###############################################
def backward_propagation(fp, map_dict, substrate, virtual):
    rev=[]
    for key,item in fp.items():
        rev.append([key,item])
    n=len(rev)
    # print("Straight=",fp)
    # print("Reverse=",rev)
    prev_subs_node=-1
    for i in range(n-1, n-2, -1):
        virtual_node=rev[i][0]
        possible_map_cand=rev[i][1]#it is dict()
        # print("first =",virtual_node,possible_map_cand)
        max_global_state=-1        
        map_subs_node=-1
        ##glob_st is a list of 2.
        for subs_node,glob_st in possible_map_cand.items():
            flag=0
            try:
                len(glob_st)>1
                flag=1
            except:
                flag=0
            if flag==1:
                glob_st=list(glob_st)
            ###if this is the single layer.
            else:
                mx=-1
                ind=-1
                for sn,gs in possible_map_cand.items():
                    if gs>mx:
                        mx=gs
                        ind=sn
                map_dict[virtual_node]=ind
                substrate.node_weights[ind]-=virtual.node_weights[virtual_node]
                return map_dict
            ###
            # print("Type=",type(glob_st))
            if glob_st[0]>max_global_state:
                max_global_state=glob_st[0]
                prev_subs_node=glob_st[1]
                map_subs_node=subs_node
        ##got the mapping for last layer
        map_dict[virtual_node]=map_subs_node
        substrate.node_weights[map_subs_node]-=virtual.node_weights[virtual_node]

    for i in range(n-2, -1, -1):
        virtual_node=rev[i][0]
        map_dict[virtual_node]=prev_subs_node

        substrate.node_weights[prev_subs_node]-=virtual.node_weights[virtual_node]
        if i!=0:
            possible_map_cand=rev[i][1]
            # print("next =",virtual_node,possible_map_cand)
            for key, item in possible_map_cand.items():
                if key==prev_subs_node:
                    prev_subs_node=item[1]

    #########For the first layer#######
    mx=-1
    ind=-1
    virtual_node=rev[0][0]
    possible_map_cand=rev[0][1]
    # print("last =",virtual_node,possible_map_cand)
    for sn,gs in possible_map_cand.items():
        if gs>mx:
            mx=gs
            ind=sn
    map_dict[virtual_node]=ind
    substrate.node_weights[ind]-=virtual.node_weights[virtual_node]
    return map_dict
    ##all vn are mapped to sn.
    return map_dict
###############################################



###############################################
# mapping function: VN -> PN mapping
def mapping():
    # time when VNE starts.
    start_time = time.time()

    x = Extract()
    # substrate is the object of Graph.
    # vne_list is the list of objects of Graph.
    # vn_adj_list: required for candidate_validation
    substrate, vne_list, vn_adj_list, _ = x.get_graphs()
    print("Number of nodes in Substrate Network =", substrate.nodes)
    file.write(f"\nNumber of nodes in Substrate Network = {substrate.nodes}")
    print("Number of edges in Substrate Network =", len(substrate.edges))
    file.write(f"\nNumber of edges in Substrate Network = {len(substrate.edges)}")
    print("Substrate nodes min cpu power =", substrate.parameters.lower_node)
    file.write(f"\nSubstrate nodes min cpu power = {substrate.parameters.lower_node}")
    print("Substrate nodes max cpu power =", substrate.parameters.upper_node)
    file.write(f"\nSubstrate nodes max cpu power = {substrate.parameters.upper_node}")
    print("Substrate edge min link capacity =", substrate.parameters.lower_edge)
    file.write(f"\nSubstrate edge min link capacity = {substrate.parameters.lower_edge}")
    print("Substrate edge max link capacity =", substrate.parameters.upper_edge)
    file.write(f"\nSubstrate edge max link capacity = {substrate.parameters.upper_edge}")

    print("\n\nNumber of nodes in substrate graph = ",substrate.nodes)
    file.write(f"\n\nNumber of nodes in substrate graph = {substrate.nodes}")
    print("\nSubstrate graph = ",substrate.edges)
    file.write(f"\nSubstrate graph = {substrate.edges}")

    
    # print("\nvne=",vne_list)
    for i in range(len(vne_list)):
        # take one VN req object.
        virtual_network = vne_list[i]
        vn_edge_weights = virtual_network.edge_weights
        vir_net_adj_list = vn_adj_list[i]

        print("\n\nREQUEST-",i+1)
        file.write(f"\n\nREQUEST- {i+1}")
        print("Number of virtual nodes = ",virtual_network.nodes)
        file.write(f"\nNumber of virtual nodes =  {virtual_network.nodes}")
        print("Number of edges in VN = ",len(virtual_network.edges))
        file.write(f"\nNumber of edges in VN =  {len(virtual_network.edges)}")
        print("Virtual Network Request= ", virtual_network.edges)
        file.write(f"\nVirtual Network Request=  {virtual_network.edges}")
        print("\n\n")
        file.write(f"\n\n")

        candidate_set, rejected = candidate_search(substrate, virtual_network)
        if rejected == True:
            print("***The request {} is rejected due to lack of resources***".format(i+1))
            file.write(f"\n***The request {i+1} is rejected due to lack of resources***\n")
            continue
        Candidate_Set = candidate_validation(substrate, candidate_set, vir_net_adj_list, vn_edge_weights)
        Cand_Set=candidate_uniquify(Candidate_Set)
        print("Candidate set-1, Generated candidates: ")
        file.write(f"\nCandidate set-1, Generated candidates: ")
        for node, cands in candidate_set.items():
            print("{}:{}".format(node, cands))
            file.write(f"\n{node}:{cands}")
        print("\nCandidate set-2, Validated candidates: ", Candidate_Set)
        file.write(f"\n\nCandidate set-2, Validated candidates: {Candidate_Set}")
        print("\nCandidate set-3, uniquified candidates: ", Cand_Set)
        file.write(f"\n\nCandidate set-3, uniquified candidates:  {Cand_Set}")

        path_seg=path_decomposition(virtual_network)
        print("Path decomposition = ",path_seg)
        file.write(f"\nPath decomposition = {path_seg}")

        map_dict=dict()
        for path in path_seg:
            fp=forward_propagation(Cand_Set, substrate, virtual_network, path)
            backward_propagation(fp, map_dict, substrate, virtual_network)
        
        print("\nMapping=",map_dict)
        file.write(f"\nMapping= {map_dict}")
    
    # time when VNE is finished.
    end_time = time.time()

    # total duration
    duration = end_time - start_time

    print("\nVNE time = %.3f seconds"%duration)
    file.write(f"\n\nVNE time = {format(duration, '.3f')} seconds")

    print("\nLog file is also generated in the current directory with file name mappingfile.txt\n")
    # f=open("mappingfile.txt","r")
    # print(f.read())
####################################################################################################


if __name__ == "__main__":
    mapping()
