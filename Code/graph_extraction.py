############################################
#Author of code: Pintu and Vivek
#Roll.No.: 181CO139 and 181CO159
############################################

import os
import pickle
import sys
import graph
from vne import create_vne

#class to generate VN requests and substrate network.
class Extract:
    def get_graphs(self):
        
        substrate, sn_adj_list = create_vne(10, 18, 1, .2)#pass large param.
        vne_list, vn_adj_list = create_vne()
        # print("substrate", substrate)
        # print("\nvne=", vne_list)
        return substrate, vne_list, vn_adj_list, sn_adj_list

#####################################################################
if __name__ == "__main__":
    x = Extract()
    x.get_graphs()

