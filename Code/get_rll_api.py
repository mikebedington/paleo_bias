import numpy as np
import numpy as np
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt

model = 'PALEOMAP'
input_dict = np.load('gplates_input.npy', allow_pickle=True).item()
ll = input_dict['orig_ll']

time_list = np.arange(360, 425, 5)
output_pts = {}
for this_time in time_list:
    output_pts[this_time] = []
output_poly = {}

first = True
block_size = 100
last_step = int(np.ceil(len(ll)/block_size))
for this_block in np.arange(1, last_step):
    if this_block == last_step - 1:
        this_ll = ll[this_block*block_size:,:]
    else:
        this_ll = ll[this_block*block_size:(this_block+1)*block_size,:]


    ll_str = ''
    for this_this_ll in this_ll:
        ll_str = ll_str + f'{this_this_ll[0]:3.4f},{this_this_ll[1]:3.4f},'
    ll_str = ll_str[0:-1]

    print(this_block)
    for time in time_list:
        print(f'Fetching data time: {time}')
        url = f"https://gws.gplates.org/reconstruct/reconstruct_points/?points={ll_str}&time={time}&model={model}"
        coast_url = f"https://gws.gplates.org/reconstruct/coastlines/?&time={time}&model={model}"
        response = urlopen(url)
        data_pts = json.loads(response.read())
        output_pts[time].append(data_pts['coordinates'])

        if first:
            response_poly = urlopen(coast_url)
            data_poly_raw = json.loads(response_poly.read())

            data_poly = []
            for this_feature in data_poly_raw['features']:
                data_poly.append(np.squeeze(this_feature['geometry']['coordinates']))
            output_poly[time] = data_poly
    first = False

for this_time in output_pts.keys():
    output_pts[this_time] = np.vstack(output_pts[this_time])

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

