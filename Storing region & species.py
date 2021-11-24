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

cyt = rxd.Region([dend], dx=0.05 * um, name="cyt", geometry=rxd.FractionalVolume(volume_fraction=0.8, surface_fraction=1))
er = rxd.Region([dend], dx=0.05 * um, name="er", geometry=rxd.FractionalVolume(0.2))
c = rxd.Species(cyt, d=0.1 * um ** 2 / ms, name="c")
db = rxd.Species([cyt, er], d=0.05 * um ** 2 / ms, name="db")

#na = rxd.Species(cyt, d=0.1 * um ** 2 / ms, name="na")

#magic = rxd.Reaction(c + 2 * na > 2 * c + na, 1, 0.1)

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



def library_data(filename):
    species_records = {}
    for sp in rxd.species._all_species:
        species_name = sp()
        if species_name:
            individual_rg = {}
            individual_sp = {}
            for rg in rxd.region._all_regions:
                region_name = rg()
                
                # storing the regions' position values
                records = [region_name._mesh_grid]
                for node in species_name.nodes(region_name):
                    position = [str(node.segment), str(node.sec), node._i, node._j, node._k, node.surface_area, node.volume]
                    records.append(position) 
                full_attributes = dict(records[0])
                new_records = records[1:]
                full_attributes['attributes'] = new_records
                individual_rg[region_name.name] = full_attributes

                # storing the species'concentration values
                records2 = []
                for node in species_name.nodes(region_name):
                    position2 = node.value
                    records2.append(position2) 

                individual_sp[region_name.name] = records2

            species_records[species_name.name] = individual_sp


    all_records = {}
    all_records['regions'] = individual_rg
    all_records['species'] = species_records


    #save the dictionary as text 
    with open(filename, "w") as apple:
        apple.write(json.dumps(all_records))




library_data("data_resion & species.json")