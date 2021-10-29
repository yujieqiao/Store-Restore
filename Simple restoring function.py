# Query: 
# ContextLines: 1

import json
import numpy as np
import plotly.graph_objects as go
import plotnine as p9
import tqdm

def plot_reconstruct(title, filename):
    #reload the data from strings to dictionary
    with open(filename) as orange:
        reload_records_json=orange.read() 
    reload_records=json.loads(reload_records_json)

    xlo = reload_records.get('xlo')
    ylo = reload_records.get('ylo')
    zlo = reload_records.get('zlo')
    dx = reload_records.get('dx')
    dy = reload_records.get('dy')
    dz = reload_records.get('dz')

    print("finding the bounds")
    #find the furtherst point needed to reach to define the shape
    bound_i = max(i for _,_,i,_,_,_,_,_ in reload_records["attributes"])+1
    bound_j = max(j for _,_,_,j,_,_,_,_ in reload_records["attributes"])+1
    bound_k = max(k for _,_,_,_,k,_,_,_ in reload_records["attributes"])+1

    print("creating space_position")
    #make the initial value on every point within the shape being -1
    space_position = np.zeros((bound_i,bound_j,bound_k))-1 

    print("creating meshgrid")
    xs, ys, zs = np.meshgrid(
        [xlo + i * dx for i in range(bound_i)],
        [ylo + j * dy for j in range(bound_j)],
        [zlo + k * dz for k in range(bound_k)],
        indexing="ij",
    )


    #assign values to corresponding points from source data
    print("reloading records")
    for _,_,i,j,k,_,v,_ in tqdm.tqdm(reload_records["attributes"]):
        space_position[i, j, k] = v 


    print("calling go.Figure")
    fig = go.Figure(
        data=go.Volume(
            x=xs.flatten(),
            y=ys.flatten(),
            z=zs.flatten(),
            value=np.nan_to_num(space_position.flatten(), nan=-1), #convert nan to a normal number
            isomin=0,
            isomax=0.01, #here can adjust isomax to appropriate level
            opacity=0.1,
            surface_count=7,
        )
    )

    fig.update_layout(title=title)
    print("calling show")
    fig.show()

t=5.05 

plot_reconstruct(f"h.t = {t}", "Properties9.json")

