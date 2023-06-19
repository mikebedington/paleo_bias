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
    static_poly2 = pygp.FeatureCollection(f'~/test_pt.shp')
    
    # Get plate ids
    #assigned_point_features = pygp.partition_into_plates(static_polygons,
                rotation_model, point_features, properties_to_copy = [pygp.PartitionProperty.reconstruction_plate_id])

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


"""
