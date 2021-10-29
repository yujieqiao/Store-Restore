# Query: 
# ContextLines: 1

from neuron import h, rxd
from neuron.units import um, ms, mV, uM
import plotly.graph_objects as go
import numpy as np
import plotnine as p9
import pandas as pd
import json as json

h.load_file("stdrun.hoc")

rxd.set_solve_type(dimension=3)
dend = h.Section(name="dend")
dend.L = 5 * um
dend.diam = 2 * um

cyt = rxd.Region([dend], dx=0.05 * um)
c = rxd.Species(cyt, d=0.1 * um ** 2 / ms)

# pick a node and verify that it is on the surface
my_nodes = c.nodes((2.5, 0.975, 0.275))
assert len(my_nodes) == 1
my_node = my_nodes[0]
assert my_node.surface_area > 0

nearby_nodes = [c.nodes((my_node.x3d + dx, my_node.y3d, my_node.z3d))[0] for dx in [0.1, 0.5, 1, 2]]

r = h.RxDSyn(my_node.segment)
my_node.include_flux(r._ref_g)
ns = h.NetStim()
ns.number = 1
ns.start = 5 * ms

nc = h.NetCon(ns, r)
nc.weight[0] = 10000
nc.delay = 0

t = h.Vector().record(h._ref_t)
my_c = h.Vector().record(my_node._ref_concentration)
nearby_cs = [h.Vector().record(node._ref_concentration) for node in nearby_nodes]

h.finitialize(-65 * mV)
h.continuerun(5.05 * ms)


def storing_data(region_name, species_name, filename):

    #save the lowest values of x, y, z & dx, dy as a dictionary
    records = [region_name._mesh_grid]
    #save the properties of each node as a list
    for node in species_name.nodes:
        position = [str(node.segment), str(node.sec), node._i, node._j, node._k, node.surface_area, node.value, node.volume]
        records.append(position) 

    #combine the above dictionary & list into a big dictionary
    full_attributes = dict(records[0])
    #make the list of properties as a giant element named 'attributes' in the dictionary
    new_records = records[1:]
    full_attributes['attributes'] = new_records

    #save the dictionary as text 
    with open(filename, "w") as apple:
        apple.write(json.dumps(full_attributes))



storing_data(cyt, c, "Properties9.json")