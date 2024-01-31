##comparison of Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##


try: 
    import os
    import pprint
    import earthpy.spatial as es
    import geopandas as gpd
    import numpy as np
    import pandas as pa
    import tifffile as tf

    import calc_kod
    print('The import was successful!')
except:
    print('Import FAIL')


SCRIPT_DIR = os.path.dirname((os.path.abspath(__file__)))
IN_FOLDER = (os.path.join(SCRIPT_DIR, r'input'))
OUT_FOLDER = (os.path.join(SCRIPT_DIR, r'output'))

L8_dict = {}
L9_dict = {}

def find_path(input_folder, file_name):
    path_list_folder = []
    for root, dics, files in os.walk(input_folder, topdown=False):
        for name in files:
            if name.endswith(file_name) :
                path_list_folder.append(os.path.join(root, name))
    return path_list_folder

landsat_tif = find_path(IN_FOLDER, ".TIF")

for landsat_path in landsat_tif:
    L8_metadata = {}
    landsat_name = os.path.basename(landsat_path)
    if 'LC08_L2SP' in landsat_name:
        date = landsat_name.split('_')[3]
        if date in L8_dict:
            L8_dict[date].append(landsat_path)
        else:
            L8_dict[date] = [landsat_path]      

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

    for path in list_of_paths:
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

    TOA_refle_b2 = calc_kod.TOA_Refl(b2, reflectance_ADD_B2, reflectance_MULT_B2, OUT_FOLDER, 'TOARef_b2_L8_' + dates)
    TOA_refle_b4 = calc_kod.TOA_Refl(b4, reflectance_ADD_B4, reflectance_MULT_B4, OUT_FOLDER, 'TOARef_b4_L8_' + dates)
    TOA_refle_b5 = calc_kod.TOA_Refl(b5, reflectance_ADD_B5, reflectance_MULT_B5, OUT_FOLDER, 'TOARef_b5_L8_' + dates)
    TOA_refle_b6 = calc_kod.TOA_Refl(b6, reflectance_ADD_B6, reflectance_MULT_B6, OUT_FOLDER, 'TOARef_b6_L8_' + dates)
    TOA_refle_b7 = calc_kod.TOA_Refl(b7, reflectance_ADD_B7, reflectance_MULT_B7, OUT_FOLDER, 'TOARef_b7_L8_' + dates)
    Albedo_liang = calc_kod.Albedo_liang(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b6, TOA_refle_b7, OUT_FOLDER, 'Albedo_L8_Liang_' + dates)
    Albedo_Tasumi_2 = calc_kod.Albedo_Tasumi(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b7, OUT_FOLDER, 'Albedo_L8_Tasumi_' + dates)


for landsat_path in landsat_tif:
    L9_metadata = {}
    landsat_name = os.path.basename(landsat_path)
    if 'LC09_L2SP' in landsat_name:
        date = landsat_name.split('_')[3]
        if date in L9_dict:
            L9_dict[date].append(landsat_path)
        else:
            L9_dict[date] = [landsat_path]      

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

    for path in list_of_paths:
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

    TOA_refle_b2_2 = calc_kod.TOA_Refl(b2_2, reflectance_ADD_B2_2, reflectance_MULT_B2_2, OUT_FOLDER, 'TOARef_b2_L9_' + dates)
    TOA_refle_b4_2 = calc_kod.TOA_Refl(b4_2, reflectance_ADD_B4_2, reflectance_MULT_B4_2, OUT_FOLDER, 'TOARef_b4_L9_' + dates)
    TOA_refle_b5_2 = calc_kod.TOA_Refl(b5_2, reflectance_ADD_B5_2, reflectance_MULT_B5_2, OUT_FOLDER, 'TOARef_b5_L9_' + dates)
    TOA_refle_b6_2 = calc_kod.TOA_Refl(b6_2, reflectance_ADD_B6_2, reflectance_MULT_B6_2, OUT_FOLDER, 'TOARef_b6_L9_' + dates)
    TOA_refle_b7_2 = calc_kod.TOA_Refl(b7_2, reflectance_ADD_B7_2, reflectance_MULT_B7_2, OUT_FOLDER, 'TOARef_b7_L9_' + dates)
    Albedo_liang_2 = calc_kod.Albedo_liang(TOA_refle_b2_2, TOA_refle_b4_2, TOA_refle_b5_2, TOA_refle_b6_2, TOA_refle_b7_2, OUT_FOLDER, 'Albedo_L9_Liang_' + dates)
    Albedo_Tasumi_2 = calc_kod.Albedo_Tasumi(TOA_refle_b2_2, TOA_refle_b4_2, TOA_refle_b5_2, TOA_refle_b7_2, OUT_FOLDER, 'Albedo_L9_Tasumi_' + dates)


pprint.pprint('All done and in order :)')