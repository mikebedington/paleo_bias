import numpy as np
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt

model = 'PALEOMAP'
input_dict = np.load('gplates_input.npy', allow_pickle=True).item()
ll = input_dict['orig_ll']

ll = ll[0:50,:]
ll_str = ''
for this_ll in ll:
    ll_str = ll_str + f'{this_ll[0]},{this_ll[1]},'
ll_str = ll_str[0:-1]

time_list = np.arange(360, 425, 5)
output_pts = {}
output_poly = {}

for time in time_list:
    print(f'Fetching data time: {time}')
    url = f"https://gws.gplates.org/reconstruct/reconstruct_points/?points={ll_str}&time={time}&model={model}"
    coast_url = f"https://gws.gplates.org/reconstruct/coastlines/?&time={time}&model={model}"
    response = urlopen(url)
    data_pts = json.loads(response.read())
    response_poly = urlopen(coast_url)
    data_poly_raw = json.loads(response_poly.read())

    data_poly = []
    for this_feature in data_poly_raw['features']:
        data_poly.append(np.squeeze(this_feature['geometry']['coordinates']))


    output_pts[time] = data_pts['coordinates']
    output_poly[time] = data_poly


for time in time_list:
    print(f'Plotting time: {time}')
    plt.figure(figsize=[18,16])
    plt.title(time)
    pt_ll = np.asarray(output_pts[time])
    plt.scatter(pt_ll[:,0], pt_ll[:,1], c='r', zorder=2)
    for poly_ll in output_poly[time]:
        plt.plot(poly_ll[:,0], poly_ll[:,1], c='darkgray', linewidth=0.5)
    plt.savefig(f'plot_new_{time}.png', dpi=180)
    plt.close()

