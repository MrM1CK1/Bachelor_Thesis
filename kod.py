##comparison of Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##


import os
import pprint
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import pandas as pa
import tifffile as tf
from fiona.crs import from_epsg
from rasterio.mask import mask
from scipy import ndimage
from shapely.geometry import box

import calc_kod

#print('The import was successful!')

SCRIPT_DIR = os.path.dirname((os.path.abspath(__file__)))   #Directory of the script
IN_FOLDER = (os.path.join(SCRIPT_DIR, r'input'))            #Input folder in the same directory
OUT_FOLDER = (os.path.join(SCRIPT_DIR, r'output'))          #Output folder in the same directory
CLIPPED = (os.path.join(SCRIPT_DIR, r'output'))             #Clipped folder in the output folder

SQUARE = box(17.1895, 49.4985, 17.4593, 49.6712) #Coordinates of the area of interest
EPSG_CODE = 32633       #EPSG code of the area of interest
L8_dict = {}
L9_dict = {}

#Function to find the path of the files
def find_path(input_folder, file_name):
    path_list_folder = []
    for root, dics, files in os.walk(input_folder, topdown=False):
        for name in files:
            if name.endswith(file_name) :
                path_list_folder.append(os.path.join(root, name))
    return path_list_folder

landsat_tif = find_path(IN_FOLDER, ".TIF")


#Finding the Landsat images (Landsat Level 1)
for landsat_path in landsat_tif:
    L8_metadata = {}
    landsat_name = os.path.basename(landsat_path)
    if 'L1SP' in landsat_name:
        date = landsat_name.split('_')[3]
        if date in L8_dict:
            L8_dict[date].append(landsat_path)
        else:
            L8_dict[date] = [landsat_path]      

# Extracting the metadata file
for dates, list_of_paths in L8_dict.items():
    list_of_paths_clipped = []
    txt_path = ''
    for path in list_of_paths_clipped:
        list_of_paths.append(path)

    for path in list_of_paths:
        if 'B1.TIF' in path:
            txt_path = path.replace('B1.TIF', 'MTL.txt')
            metadata_file = open(txt_path, 'r')
            for line in metadata_file:
                if '=' in line:
                    key, value = line.strip().split(' = ')
                    L8_metadata[key] = value                                 
            metadata_file.close()
            break
    
    # Clipping the images
    for path in list_of_paths:
        image_name = os.path.basename(path).replace('.TIF', '')
        out_path = CLIPPED + '\\' + image_name + '_Clipped.TIF'
        calc_kod.Raster_clip(path, out_path, SQUARE)

        list_of_paths_clipped.append(out_path)

    # Extracting information from the metadata file
    for path in list_of_paths_clipped:
        if 'B1_' in path:
            b1 = path
        if 'B2' in path:
            b2 = path
            reflectance_MULT_B2 = float((L8_metadata['REFLECTANCE_MULT_BAND_2']))
            reflectance_ADD_B2 = float((L8_metadata['REFLECTANCE_ADD_BAND_2']))
        if 'B3' in path:
            b3 = path
        if 'B4' in path:
            b4 = path
            reflectance_MULT_B4 = float((L8_metadata['REFLECTANCE_MULT_BAND_4']))
            reflectance_ADD_B4 = float((L8_metadata['REFLECTANCE_ADD_BAND_4']))
        if 'B5' in path:
            b5 = path
            reflectance_MULT_B5 = float((L8_metadata['REFLECTANCE_MULT_BAND_5']))
            reflectance_ADD_B5 = float((L8_metadata['REFLECTANCE_ADD_BAND_5']))
        if 'B6' in path:
            b6 = path
            reflectance_MULT_B6 = float((L8_metadata['REFLECTANCE_MULT_BAND_6']))
            reflectance_ADD_B6 = float((L8_metadata['REFLECTANCE_ADD_BAND_6']))
        if 'B7' in path:
            b7 = path
            reflectance_MULT_B7 = float((L8_metadata['REFLECTANCE_MULT_BAND_7']))
            reflectance_ADD_B7 = float((L8_metadata['REFLECTANCE_ADD_BAND_7']))
        if 'B10' in path:
            b10 = path
            radiance_MULT_B10 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
            radiance_ADD_B10 = float((L8_metadata['RADIANCE_ADD_BAND_10']))
            K1_CONSTANT_BAND_10 = float((L8_metadata['K1_CONSTANT_BAND_10']))
            K2_CONSTANT_BAND_10 = float((L8_metadata['K2_CONSTANT_BAND_10']))


    TOA_refle_b2 = calc_kod.TOA_Reflectance(b2, reflectance_ADD_B2, reflectance_MULT_B2, OUT_FOLDER, 'TOARef_b2_' + dates)
    TOA_refle_b4 = calc_kod.TOA_Reflectance(b4, reflectance_ADD_B4, reflectance_MULT_B4, OUT_FOLDER, 'TOARef_b4_' + dates)
    TOA_refle_b5 = calc_kod.TOA_Reflectance(b5, reflectance_ADD_B5, reflectance_MULT_B5, OUT_FOLDER, 'TOARef_b5_' + dates)
    TOA_refle_b6 = calc_kod.TOA_Reflectance(b6, reflectance_ADD_B6, reflectance_MULT_B6, OUT_FOLDER, 'TOARef_b6_' + dates)
    TOA_refle_b7 = calc_kod.TOA_Reflectance(b7, reflectance_ADD_B7, reflectance_MULT_B7, OUT_FOLDER, 'TOARef_b7_' + dates)
    Albedo_liang = calc_kod.Albedo_liang(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b6, TOA_refle_b7, OUT_FOLDER, 'Albedo_L8_Liang_' + dates)
    Albedo_Tasumi = calc_kod.Albedo_Tasumi(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b7, OUT_FOLDER, 'Albedo_L8_Tasumi_' + dates)

    TOA_radiance_B10 = calc_kod.TOA_Radiance(b10, radiance_ADD_B10, radiance_MULT_B10, OUT_FOLDER, 'TOA_Radiance_B10_' + dates)

    ndvi_TIF = calc_kod.NDVI(b4, b5, OUT_FOLDER, 'NDVI_' + dates)

    #LST_b10 = calc_kod.LST(TOA_radiance_B10, K1_CONSTANT_BAND_10_L8, K2_CONSTANT_BAND_10_L8, OUT_FOLDER, 'LST_L8_B10_' + dates)

    VegC = calc_kod.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + dates)
    #Emis = calc_kod.Emissivity(ndvi_TIF_L8,LST_b10_L8, OUT_FOLDER, 'Emissivity_L8_' + dates)
    #BrighTemp = calc_kod.Brightness_Temperature(TOA_radiance_B10, Emis_L8, OUT_FOLDER, 'BrightTemp_L8_' + dates)



#Finding the Landsat images (Landsat Level 2)
for landsat_path in landsat_tif:
    L9_metadata = {}
    landsat_name = os.path.basename(landsat_path)
    if 'L2SP' in landsat_name:
        date = landsat_name.split('_')[3]
        if date in L9_dict:
            L9_dict[date].append(landsat_path)
        else:
            L9_dict[date] = [landsat_path]      

# Extracting the metadata file
for dates, list_of_paths in L9_dict.items():
    list_of_paths_clipped = []
    txt_path = ''
    for path in list_of_paths_clipped:
        list_of_paths.append(path)

    for path in list_of_paths:
        if 'B1.TIF' in path:
            txt_path = path.replace('B1.TIF', 'MTL.txt')
            metadata_file = open(txt_path, 'r')
            for line in metadata_file:
                if '=' in line:
                    key, value = line.strip().split(' = ')
                    L9_metadata[key] = value                                 
            metadata_file.close()
            break 

    # Clipping the images
    for path in list_of_paths:
        image_name = os.path.basename(path).replace('.TIF', '')
        out_path = CLIPPED + '\\' + image_name + '_Clipped.TIF'
        calc_kod.Raster_clip(path, out_path, SQUARE)

        list_of_paths_clipped.append(out_path) 

    # Extracting information from the metadata file
    for path in list_of_paths_clipped:
        if 'B1_' in path:
            b1_2 = path
        if 'B2' in path:
            b2_2 = path
            reflectance_MULT_B2_2 = float((L9_metadata['REFLECTANCE_MULT_BAND_2']))
            reflectance_ADD_B2_2 = float((L9_metadata['REFLECTANCE_ADD_BAND_2']))
        if 'B3' in path:
            b3_2 = path
        if 'B4' in path:
            b4_2 = path
            reflectance_MULT_B4_2 = float((L9_metadata['REFLECTANCE_MULT_BAND_4']))
            reflectance_ADD_B4_2 = float((L9_metadata['REFLECTANCE_ADD_BAND_4']))
        if 'B5' in path:
            b5_2 = path
            reflectance_MULT_B5_2 = float((L9_metadata['REFLECTANCE_MULT_BAND_5']))
            reflectance_ADD_B5_2 = float((L9_metadata['REFLECTANCE_ADD_BAND_5']))
        if 'B6' in path:
            b6_2 = path
            reflectance_MULT_B6_2 = float((L9_metadata['REFLECTANCE_MULT_BAND_6']))
            reflectance_ADD_B6_2 = float((L9_metadata['REFLECTANCE_ADD_BAND_6']))
        if 'B7' in path:
            b7_2 = path
            reflectance_MULT_B7_2 = float((L9_metadata['REFLECTANCE_MULT_BAND_7']))
            reflectance_ADD_B7_2 = float((L9_metadata['REFLECTANCE_ADD_BAND_7']))
        if 'B10' in path:
            b10_2 = path
            radiance_MULT_B10_2 = float((L9_metadata['RADIANCE_MULT_BAND_10']))
            radiance_ADD_B10_2 = float((L9_metadata['RADIANCE_ADD_BAND_10']))
            K1_CONSTANT_BAND_10 = float((L9_metadata['K1_CONSTANT_BAND_10']))
            K2_CONSTANT_BAND_10 = float((L9_metadata['K2_CONSTANT_BAND_10']))


#    TOA_refle_b2_2 = calc_kod.TOA_Reflectance(b2_2, reflectance_ADD_B2_2, reflectance_MULT_B2_2, OUT_FOLDER, 'TOARef_b2_' + dates)
#    TOA_refle_b4_2 = calc_kod.TOA_Reflectance(b4_2, reflectance_ADD_B4_2, reflectance_MULT_B4_2, OUT_FOLDER, 'TOARef_b4_' + dates)
#    TOA_refle_b5_2 = calc_kod.TOA_Reflectance(b5_2, reflectance_ADD_B5_2, reflectance_MULT_B5_2, OUT_FOLDER, 'TOARef_b5_' + dates)
 #   TOA_refle_b6_2 = calc_kod.TOA_Reflectance(b6_2, reflectance_ADD_B6_2, reflectance_MULT_B6_2, OUT_FOLDER, 'TOARef_b6_' + dates)
  #  TOA_refle_b7_2 = calc_kod.TOA_Reflectance(b7_2, reflectance_ADD_B7_2, reflectance_MULT_B7_2, OUT_FOLDER, 'TOARef_b7_' + dates)
    #Albedo_liang = calc_kod.Albedo_liang(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b6, TOA_refle_b7, OUT_FOLDER, 'Albedo_L9_Liang_' + dates)
    #Albedo_Tasumi = calc_kod.Albedo_Tasumi(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b7, OUT_FOLDER, 'Albedo_L9_Tasumi_' + dates)


    TOA_radiance_B10 = calc_kod.TOA_Radiance(b10_2, radiance_ADD_B10_2, radiance_MULT_B10_2, OUT_FOLDER, 'TOA_Radiance_L9_B10_' + dates)

    ndvi_TIF = calc_kod.NDVI(b4_2, b5_2, OUT_FOLDER, 'NDVI_' + dates)

    LST_b10 = calc_kod.LST(TOA_radiance_B10, K1_CONSTANT_BAND_10,K2_CONSTANT_BAND_10,  OUT_FOLDER, 'LST_L9_B10_' + dates)

#    VegC = calc_kod.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + dates)
    Emis = calc_kod.Emissivity(ndvi_TIF,LST_b10, OUT_FOLDER, 'Emis_L9_' + dates)
    BrighTemp = calc_kod.Brightness_Temperature(TOA_radiance_B10, Emis, OUT_FOLDER, 'BrightTemp_L9_' + dates)


   # GroundHeatFlux_path = calc_stch.GroundHF(Albedo_liang, ndvi_TIF, LST_b10, TotalRadiation_path, OUT_FOLDER, 'GroundHeatFlux_' + dates)

pprint.pprint('All done and in order :)')
