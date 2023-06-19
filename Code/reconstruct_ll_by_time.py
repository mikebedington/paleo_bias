# Code nicked from Mats' script#
# Use conda env pygplates and add to python path export PYTHONPATH=$PYTHONPATH:/usr/lib
# Use Mats 2014 reconstruction http://www.earthdynamics.org/earthmodel/page1.html

import pygplates as pygp
import numpy as np

#ll = np.load('ll.npy')
input_dict = np.load('gplates_input.npy', allow_pickle=True).item()
ll = input_dict['orig_ll']
mm_age = [input_dict['min_age'], input_dict['max_age']]
base = 5 # round to nearest 5 in age

mat2014_dir = '/home/michael/Experiments/Paleo_bias/Data/Domeier2014_data'
rotation_model = f'{mat2014_dir}/LP_TPW.rot'
#static_polygons = pygp.FeatureCollection(f'{mat2014_dir}/LP_topos.gpml')
static_polygons = pygp.FeatureCollection(f'{mat2014_dir}/LP_land.shp')

recon_lats, recon_lons = [], []
recon_poly_times = []
recon_polys = {}

for this_ll, this_mm in zip(ll, mm_age):
    # Convert to gplates feature format
    point = pygp.PointOnSphere(this_ll[1], this_ll[0]) # lat, lon
    point_feature = pygp.Feature()
    point_feature.set_geometry(point)
    point_feature.set_valid_time(this_mm[1], this_mm[0])

    # Get plate ids
    assigned_point_features = pygp.partition_into_plates(static_polygons,
                rotation_model, [point_feature], properties_to_copy = [pygp.PartitionProperty.reconstruction_plate_id])

    # Reconstruct

    reconstruction_time = base * round(np.mean(this_mm)/base)
    reconstructed_point_features = []
    reconstructed_static_polygons = []
    pygp.reconstruct(assigned_point_features, rotation_model, reconstructed_point_features, reconstruction_time)
    pygp.reconstruct(static_polygons, rotation_model, reconstructed_static_polygons, reconstruction_time)

    # Extract
    for reconstructed_feature in reconstructed_point_features:
        recon_lats.append(reconstructed_feature.get_reconstructed_geometry().to_lat_lon())
        recon_lons.append(reconstructed_feature.get_reconstructed_geometry().to_lat_lon())

    if reconstruction_time not in recon_poly_times:
        recon_poly_lats, recon_poly_lons = [], []
        for reconstructed_feature in reconstructed_static_polygons:
            recon_poly = reconstructed_feature.get_reconstructed_geometry().to_lat_lon_array()
            recon_poly_lats.append([i[0] for i in recon_poly])
            recon_poly_lons.append([i[1] for i in recon_poly])
        recon_polys[reconstruction_time] = [recon_poly_lons, recon_poly_lats]
        recon_poly_times.append(reconstruction_time)
        

np.save('data_raw.npy', {'recon_lats': recon_lats, 'recon_lons': recon_lons, 'recon_poly_times':recon_poly_times, 'recon_polys':recon_polys})

#np.save('data.npy', {'points':reconstructed_point_features, 'polys':reconstructed_static_polygons})


# Test plot
"""
orig_ll = np.load('ll.npy')
rot_data = np.load('data_raw.npy', allow_pickle=True).item()
new_ll_raw = np.asarray([rot_data['recon_lons'], rot_data['recon_lats']]).T
new_ll = np.asarray([new_ll_raw[0,:,0], new_ll_raw[1,:,0]]).T

poly_list = []
for poly_lat, poly_lon in zip(rot_data['recon_poly_lons'], rot_data['recon_poly_lats']):
    poly_list.append(np.asarray([poly_lon, poly_lat]).T)

# Need to plot this on a proper projection


"""
