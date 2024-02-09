##calculations comparing Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##
 

import os
import earthpy as et
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import tifffile as tf
import rasterio
import json
import matplotlib.pyplot as plt
import sys
from osgeo import gdal, osr
from numpy import log
from rasterio.mask import mask
import fiona


print('Import done.')

def find_path(input_folder, file_name):
    path_list_folder = []
    for root, dics, files in os.walk(input_folder, topdown=False):
        for name in files:
            if name.endswith(file_name) :
                path_list_folder.append(os.path.join(root, name))
    return path_list_folder

#https://gist.github.com/mhweber/1af47ef361c3b20184455060945ac61b
def Raster_clip(inras, outras, SQUARE):
    src  = rasterio.open(inras)
    # Create a square GeoDataFrame from the square
    df = gpd.GeoDataFrame({'geometry': [SQUARE]}, crs="EPSG:4326")
    df = df.to_crs(src.crs)
    def getFeatures(gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        return [json.loads(gdf.to_json())['features'][0]['geometry']]
    coords = getFeatures(df)
    clipped_array, clipped_transform = mask(dataset=src, shapes=coords, crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": clipped_array.shape[1],
                    "width": clipped_array.shape[2],
                    "transform": clipped_transform,}
                    )
    
    with rasterio.open(outras, "w", **out_meta) as dest:
        dest.write(clipped_array)

    return clipped_array    


#https://gist.github.com/jkatagi/a1207eee32463efd06fb57676dcf86c8
def GeoRef(input_array, src_dataset_path, output_path):
        cols = input_array.shape[1]
        rows = input_array.shape[0]
        
        dataset = gdal.Open(src_dataset_path, gdal.GA_ReadOnly)
        originX, pixelWidth, b, originY, d, pixelHeight = dataset.GetGeoTransform() 
        driver = gdal.GetDriverByName('GTiff')
        band_num = 1
        GDT_dtype = gdal.GDT_Float32
        outRaster = driver.Create(output_path, cols, rows, band_num, GDT_dtype)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(band_num)
        outband.WriteArray(input_array)
        prj=dataset.GetProjection()
        outRasterSRS = osr.SpatialReference(wkt=prj)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        
        return True

#Top of Atmosphere Reflectance
def TOA_Reflectance(band, ADD, MULT, out_folder, name = "_TOA_Ref"):   
    
    band_p= tf.imread(band)
    
    result_toa = MULT * band_p + ADD
    result_toa_path = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(result_toa, band, result_toa_path)
    
    return result_toa_path


#Albedo Liang's method
def Albedo_liang(toa_band_2, toa_band_4, toa_band_5, toa_band_6, toa_band_7, out_folder, name = 'albedo'):
    B2_T = np.array(tf.imread(toa_band_2))
    B4_T = np.array(tf.imread(toa_band_4))
    B5_T = np.array(tf.imread(toa_band_5))
    B6_T = np.array(tf.imread(toa_band_6))
    B7_T = np.array(tf.imread(toa_band_7))
    
    result_albedo = ((0.356 * B2_T) + (0.130 * B4_T) + (0.373 * B5_T) + (0.085 * B6_T) + (0.072 * B7_T))-0.0018/1.016
    result_albedo_path = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(result_albedo, toa_band_5, result_albedo_path)
    
    return result_albedo_path


#Albedo Tasumi's method
def Albedo_Tasumi(toa_band_2, toa_band_4, toa_band_5, toa_band_7, out_folder, name = 'albedo_tasumi'):
    B2_T = np.array(tf.imread(toa_band_2))
    B4_T = np.array(tf.imread(toa_band_4))
    B5_T = np.array(tf.imread(toa_band_5))
    B7_T = np.array(tf.imread(toa_band_7))

    albedo_tasumi = ((0.149 * B2_T) + (0.311 * B4_T) + (0.103 * B5_T)  + (0.036 * B7_T))-0.0018/0.599
    albedo_tasumi_path = os.path.join(out_folder, name + ".TIF")
    GeoRef(albedo_tasumi, toa_band_7, albedo_tasumi_path)

    return albedo_tasumi_path
 

#Top of Atmosphere Radiance
#TIRS = Thermal Infrared Sensor
#ADD = Additive rescaling factor
#MULT = Multiplicative rescaling factor
def TOA_Radiance(TIRS, ADD, MULT, out_folder, name = "TOA_Radiance"):   
        
    thermal= tf.imread(TIRS)
    
    cal_radiance = (MULT  * thermal) + ADD
    res_cal_radiance = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(cal_radiance, TIRS, res_cal_radiance)
    
    return res_cal_radiance


#Normalized Difference Vegetation Index
#NIR = Near Infrared Band
#RED = Red Band
def NDVI(red, nir, out_folder, name = "_NDVI"):

    red_band = tf.imread(red)
    nir_band = tf.imread(nir)
    r = np.array(red_band).astype(rasterio.float32)#Convert to float32 to avoid overflows
    n = np.array(nir_band).astype(rasterio.float32)#Convert to float32 to avoid overflows
    
    overflows = np.seterr(divide='ignore', invalid='ignore') # Ignore the divided by zero or Nan appears

    ndvi = (n - r) / (n + r) # The NDVI formula
    ndvi_TIF = os.path.join(out_folder, name + ".TIF")

    GeoRef(ndvi, red, ndvi_TIF)

    return ndvi_TIF


#Vegetation Cover
#VC = 0.5 * NDVI + 0.5
#NDVI = Normalized Difference Vegetation Index		
def VC(ndvi, out_folder, name = "VC"):
    ndvi_arr = np.array(tf.imread(ndvi))
    calc_VC= 0.5 * ndvi_arr + 0.5
  
    result_VC = os.path.join(out_folder, name +".TIF")

    GeoRef(calc_VC, ndvi, result_VC)

    return result_VC


#Land Surface Temperature
def LST(Rad_b10,k1,k2, out_folder, name = "LST"):
    toa_rad_band10 = np.array(tf.imread(Rad_b10))
    k1_c = np.array(k1)
    k2_c = np.array(k2)
      
    calc_LST = (k2_c / log(k1_c / toa_rad_band10 + 1)) - 273.15
        
    result_LST = os.path.join(out_folder, name + ".TIF")
        
    GeoRef(calc_LST, toa_rad_band10, result_LST)

    return result_LST


#Emissivity
def Emissivity(ndvi, LST, out_folder, name = "EMISS"):
    # Calculate emissivity based on NDVI and land surface temperature
    ndvi_arr = np.array(tf.imread(ndvi))
    LST_arr = np.array(LST)

  # Coefficients based on studies and band selection
    a = 0.0046
    b = -0.0841

    calc_Emiss = 0.92 + a * (1 - ndvi_arr) + b * (1 - ndvi_arr)**2 + (0.92 - 0.98) * np.exp(-LST_arr / 300)
  # Calculate emissivity
    result_Emissivity = os.path.join(out_folder, name + ".TIF") 
    
    GeoRef(calc_Emiss, LST, result_Emissivity)

    return result_Emissivity




#Brightness Temperature
def Brightness_Temperature(TOA_rad_B10,Emissi , out_folder, name = "BriTemp"):
    toa_rad_band10 = tf.imread(TOA_rad_B10)
    Emiss = tf.imread(Emissi)

    stefan_boltzmann = 5.6704e-8  # W/m^2/K^4
    calc_BriTemp = (toa_rad_band10 / stefan_boltzmann / Emiss)**0.5 - 273.15
    
    result_BriTemp = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_BriTemp, TOA_rad_B10, result_BriTemp)

    return result_BriTemp
