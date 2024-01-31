##calculations comparing Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##
 

import os
import earthpy as et
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import tifffile as tf
from osgeo import gdal, osr

print('Import done.')
    

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


def TOA_Refl(band_path, ADD, MULT, out_folder, name = "_TOA_Ref"):   
    
    band= tf.imread(band_path)
    
    result_toa = MULT * band + ADD
    result_toa_path = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(result_toa, band_path, result_toa_path)
    
    return result_toa_path

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

def Albedo_Tasumi(toa_band_2, toa_band_4, toa_band_5, toa_band_7, out_folder, name = 'albedo_tasumi'):
    B2_T = np.array(tf.imread(toa_band_2))
    B4_T = np.array(tf.imread(toa_band_4))
    B5_T = np.array(tf.imread(toa_band_5))
    B7_T = np.array(tf.imread(toa_band_7))

    albedo_tasumi = ((0.149 * B2_T) + (0.311 * B4_T) + (0.103 * B5_T)  + (0.036 * B7_T))-0.0018/0.599
    albedo_tasumi_path = os.path.join(out_folder, name + ".TIF")
    GeoRef(albedo_tasumi, toa_band_7, albedo_tasumi_path)

    return albedo_tasumi_path
