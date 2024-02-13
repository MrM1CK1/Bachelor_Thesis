##comparison of Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##


import os
from pprint import pprint
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
import sys
#print('The import was successful!')


### postup pro výpocet LST
# 1. BT - potřebná data: Kelvin consrant 1, Kelvin constant 2, Radiance add Band, Radiance Multi Band, pásmo L1_B10
#       - uroven zpracovani L1 !!!!
#       - pásmo: B10
# 
# 2. NDVI - potrebna data: B4, B5     
#       - úroveň zpracování L2
# 
# 3. VegC - potrebná data: ndvi
#       -úroven zpracovani: L2

# 5. LSE - Surface Emissivity
#       - úroven zpracování: L2
#       - potrebná data: B4, NDVI, VegC
#
# 6. LST - potrebna data: LSE, BT, B10_L1
#        - úroven zpracovani: L1/L2
#


SCRIPT_DIR = os.path.dirname((os.path.abspath(__file__)))   #Directory of the script
IN_FOLDER = (os.path.join(SCRIPT_DIR, r'input'))            #Input folder in the same directory
OUT_FOLDER = (os.path.join(SCRIPT_DIR, r'output'))          #Output folder in the same directory
CLIPPED = (os.path.join(SCRIPT_DIR, r'output'))             #Clipped folder in the output folder

SQUARE = box(17.0846,49.5122,18.5743,49.9015) #Coordinates of the area of interest
EPSG_CODE = 32633       #EPSG code of the area of interest
L8_dict = {}
L9_dict = {}
L8_metadata = {}
landsate_date = []


landsat_tif = calc_kod.find_path(IN_FOLDER, ".TIF")   ###L1 i L2
# 'input/LC08_L1TP_190025_20220627_20220706_02_T1/LC08_L1TP_190025_20220627_20220706_02_T1_SAA.TIF'


#Finding the Landsat images (Landsat Level 1)
for landsat_path in landsat_tif:
    
    landsat_name = os.path.basename(landsat_path) #'LC08_L1TP_190025_20220627_20220706_02_T1_SAA.TIF'
    if 'L1TP' in landsat_name:
        date = landsat_name.split('_')[3] #20220627
        if date not in landsate_date:
            landsate_date.append(date)

        if date in L8_dict:
            L8_dict[date].append(landsat_path)
        else:
            L8_dict[date] = [landsat_path]      

#for landsat_path in landsat_tif: #'input/LC08_L1TP_190025_20220627_20220706_02_T1/LC08_L1TP_190025_20220627_20220706_02_T1_B6.TIF'
for landsat_path in landsat_tif:
    
    #'/home/tereza/Documents/GitHub/repos/Bachelor_Thesis/output\\LC08_L1TP_190025_20220627_20220706_02_T1_B5_Clipped.TIF'
    if 'B1.TIF' in landsat_path:
        txt_path = landsat_path.replace('B1.TIF', 'MTL.txt')
        
        metadata_file = open(txt_path, 'r')
        for line in metadata_file:
            if '=' in line:
                key, value = line.strip().split(' = ')
                L8_metadata[key] = value                                 
        metadata_file.close()
        #{'CLOUD_COVER': '5.20',
            #'CLOUD_COVER_LAND': '5.20'...}
        break
    
# Clipping the images
#for path in landsat_path:
list_of_paths_clipped = []
for landsat_path in landsat_tif:
    image_name = os.path.basename(landsat_path).replace('.TIF', '')   
    if 'B' in image_name.split('_')[-1]: ## vyfiltruje pouze pásma s DATY (Bx)
        out_path = os.path.join(CLIPPED, image_name + '_Clipped.TIF') #output/LC08_L1TP_190025_20220627_20220706_02_T1_B9_Clipped.TIF
        calc_kod.Raster_clip(landsat_path, out_path, SQUARE)
        list_of_paths_clipped.append(out_path) # pripojit oklipovane paths do seznamu
        #['output/LC08_L2SP_190025_20220627_20220706_02_T1_ST_B10_Clipped.TIF',
        #'/output/LC08_L2SP_190025_20220627_20220706_02_T1_SR_B1_Clipped.TIF']

for date in landsate_date:
    for path in list_of_paths_clipped:
        if date in path:
            if 'SR_B1' in path:
                b1_l2 = path
                
            elif 'SR_B2' in path:
                b2_l2 = path
                reflectance_MULT_B2 = float((L8_metadata['REFLECTANCE_MULT_BAND_2']))
                reflectance_ADD_B2 = float((L8_metadata['REFLECTANCE_ADD_BAND_2']))
                
            elif 'SR_B3' in path:
                b3_l2 = path
                
            elif 'SR_B4' in path:
                b4_l2 = path
                reflectance_MULT_B4 = float((L8_metadata['REFLECTANCE_MULT_BAND_4']))
                reflectance_ADD_B4 = float((L8_metadata['REFLECTANCE_ADD_BAND_4']))
                
            elif 'SR_B5' in path:
                b5_l2 = path
                reflectance_MULT_B5 = float((L8_metadata['REFLECTANCE_MULT_BAND_5']))
                reflectance_ADD_B5 = float((L8_metadata['REFLECTANCE_ADD_BAND_5']))
                
            elif 'SR_B6' in path:
                b6_l2  = path
                reflectance_MULT_B6 = float((L8_metadata['REFLECTANCE_MULT_BAND_6']))
                reflectance_ADD_B6 = float((L8_metadata['REFLECTANCE_ADD_BAND_6']))
                
            elif 'SR_B7' in path:
                b7_l2  = path
                reflectance_MULT_B7 = float((L8_metadata['REFLECTANCE_MULT_BAND_7']))
                reflectance_ADD_B7 = float((L8_metadata['REFLECTANCE_ADD_BAND_7']))
                
            elif 'ST_B10' in path:
                b10_l2  = path
                radiance_MULT_B10 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10 = float((L8_metadata['RADIANCE_ADD_BAND_10']))

                K1_CONSTANT_BAND_10 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10 = float((L8_metadata['K2_CONSTANT_BAND_10']))
                
            elif 'L1TP' and 'B10' in path:
                b10_l1  = path
                radiance_MULT_B10_l1 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10_l1 = float((L8_metadata['RADIANCE_ADD_BAND_10']))
                K1_CONSTANT_BAND_10_L1 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10_L1 = float((L8_metadata['K2_CONSTANT_BAND_10']))
    
    ndvi_TIF = calc_kod.NDVI(b4_l2, b5_l2, OUT_FOLDER, 'NDVI_' + date)   
    VegC = calc_kod.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + date)

    TOA_radiance_B10_L1 = calc_kod.TOA_Radiance(b10_l1, radiance_ADD_B10_l1, radiance_MULT_B10_l1, OUT_FOLDER, 'TOA_Radiance_B10_' + date)
    BrighTemp = calc_kod.Brightness_Temperature(radiance_ADD_B10_l1,radiance_MULT_B10_l1, b10_l1, OUT_FOLDER, 'BrightTemp_' + date)

    Emmisivity = calc_kod.LSE(b4_l2, ndvi_TIF, VegC, OUT_FOLDER, 'Emiss_' + date)
    LSTemperature = calc_kod.LST(Emmisivity, BrighTemp, b10_l1, OUT_FOLDER, 'LST_' + date)

# Extracting information from the metadata file
## neexistuje tady zadne rozdeleni mezi L1 a L2, zadny filtr.. nevime na co python saha
## tady je potreba presne definovat, jestli pracuju s L1 nebo L2, jinak se to bude motat

#for date in landsate_date: #timto se pojistime, ze stale sahame pro soubory ktere patri do stale stejneho datumu
    #for path in list_of_paths_clipped: #'output/LC08_L2SP_190025_20220627_20220706_02_T1_SR_B5_Clipped.TIF'
       # ndvi_TIF = calc_kod.NDVI(b4_l2, b5_l2, OUT_FOLDER, 'NDVI_' + date)
        #VegC = calc_kod.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + date)





"""TOA_refle_b4 = calc_kod.TOA_Reflectance(b4, reflectance_ADD_B4, reflectance_MULT_B4, OUT_FOLDER, 'TOARef_b4_' + dates)
TOA_refle_b2 = calc_kod.TOA_Reflectance(b2_l2, reflectance_ADD_B2, reflectance_MULT_B2, OUT_FOLDER, 'TOARef_b2_' + date)
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


pprint.pprint('All done and in order :')
"""
