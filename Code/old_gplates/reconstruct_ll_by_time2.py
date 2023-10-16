# Code nicked from Mats' script#
# Use conda env pygplates and add to python path export PYTHONPATH=$PYTHONPATH:/usr/lib
# Use Mats 2014 reconstruction http://www.earthdynamics.org/earthmodel/page1.html

import pygplates as pygp
import numpy as np

#ll = np.load('ll.npy')
input_dict = np.load('gplates_input.npy', allow_pickle=True).item()
ll = input_dict['orig_ll']

r_ll = {}
r_poly = {}

for time in np.arange(360, 425, 5):
    print(time)
    age_window = 10
    tmin = time-age_window
    tmax = time+age_window

    mat2014_dir = '/home/michael/Experiments/Paleo_bias/Data/Domeier2014_data'
    rotation_model = f'{mat2014_dir}/LP_TPW.rot'
    #static_polygons = pygp.FeatureCollection(f'{mat2014_dir}/LP_topos.gpml')
    static_polygons = pygp.FeatureCollection(f'{mat2014_dir}/LP_land.shp')

    # Convert to gplates feature format
    point_features = []
    for this_ll in ll:
        point = pygp.PointOnSphere(this_ll[1], this_ll[0]) # lat, lon
        point_feature = pygp.Feature()
        point_feature.set_geometry(point)
        #point_feature.set_valid_time(tmax, tmin)
        point_features.append(point_feature)

    # Get plate ids
    assigned_point_features = pygp.partition_into_plates(static_polygons,
                rotation_model, point_features, properties_to_copy = [pygp.PartitionProperty.reconstruction_plate_id])
    #assigned_point_features = point_features
    # Reconstruct

    reconstruction_time = time
    reconstructed_point_features = []
    reconstructed_static_polygons = []
    pygp.reconstruct(assigned_point_features, rotation_model, reconstructed_point_features, reconstruction_time)
    pygp.reconstruct(static_polygons, rotation_model, reconstructed_static_polygons, reconstruction_time)

    # Extract
    recon_ll = []
    for reconstructed_feature in reconstructed_point_features:
        recon_ll.append(reconstructed_feature.get_reconstructed_geometry().to_lat_lon())
    r_ll[time] = recon_ll

    recon_poly_lats, recon_poly_lons = [], []
    for reconstructed_feature in reconstructed_static_polygons:
        recon_poly = reconstructed_feature.get_reconstructed_geometry().to_lat_lon_array()
        recon_poly_lats.append([i[0] for i in recon_poly])
        recon_poly_lons.append([i[1] for i in recon_poly])

    r_poly[time] = [recon_poly_lons, recon_poly_lats]

np.save('r_ll.npy', r_ll)
np.save('r_poly.npy', r_poly)

#np.save('data.npy', {'points':reconstructed_point_features, 'polys':reconstructed_static_polygons})


"""
# Test plot

orig_ll = np.load('ll.npy')
rot_data = np.load('data_raw.npy', allow_pickle=True).item()
new_ll_raw = np.asarray([rot_data['recon_lons'], rot_data['recon_lats']]).T
new_ll = np.asarray([new_ll_raw[0,:,0], new_ll_raw[1,:,0]]).T

poly_list = []
for poly_lat, poly_lon in zip(rot_data['recon_poly_lons'], rot_data['recon_poly_lats']):
    poly_list.append(np.asarray([poly_lon, poly_lat]).T)

# Need to plot this on a proper projection

gplates_ll = np.load('r_ll.npy', allow_pickle=True).item()
   ...: gplates_poly = np.load('r_poly.npy', allow_pickle=True).item()

In [2]: for time in gplates_ll.keys():
   ...:     print(time)
   ...:     plt.figure(figsize=[18,16])
   ...:     plt.title(time)
   ...:     pt_ll = np.asarray(gplates_ll[time])
   ...:     plt.scatter(pt_ll[:,1], pt_ll[:,0], c='r')
   ...:     for plon, plat in zip(gplates_poly[time][0], gplates_poly[time][1]):
   ...:         plt.plot(plon, plat, c='darkgray', linewidth=0.5)
   ...:     plt.savefig(f'plot_{time}.png', dpi=180)
   ...:     plt.close()

"""
