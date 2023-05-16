from osgeo import gdal

lyr = QgsProject.instance().mapLayersByName('KNP_slope')[0]

path = lyr.source()

ds = gdal.Open(path)

arr = ds.ReadAsArray()

class1_count = ((arr > 0)&(arr <= 10)).sum()
class2_count = ((arr > 10)&(arr <= 20)).sum()
class3_count = ((arr > 20)&(arr <= 30)).sum()
class4_count = ((arr > 30)&(arr <= 40)).sum()
class5_count = (arr > 40).sum()
no_data_count = (arr == -9999).sum()

#print(class 1 count)
print(f'0-10: {class1_count}')
#print(class 2 count)
print(f'10-20: {class2_count}')
#print(class 3 count)
print(f'20-30: {class3_count}')
#print(class 4 count)
print(f'30-40: {class4_count}')
#print(class 5 count)
print(f'40: {class5_count}')
#print(no_data_count)
print(f'No Data: {no_data_count}')

total_pixel_count = sum([class1_count, class2_count, class3_count, class4_count, class5_count, no_data_count])
total_valid_pixel_count = sum([class1_count, class2_count, class3_count, class4_count, class5_count])
print(f'Total pixels: {total_pixel_count}')
print(f'Total pixels excluding no data: {total_valid_pixel_count}')

class1_pcnt = round(class1_count/total_valid_pixel_count*100, 3)
class2_pcnt = round(class2_count/total_valid_pixel_count*100, 3)
class3_pcnt = round(class3_count/total_valid_pixel_count*100, 3)
class4_pcnt = round(class4_count/total_valid_pixel_count*100, 3)
class5_pcnt = round(class5_count/total_valid_pixel_count*100, 3)

print(f'Percentage of site with slope between 0 and 10 degrees: {class1_pcnt}')
print(f'Percentage of site with slope between 10 and 20 degrees: {class2_pcnt}')
print(f'Percentage of site with slope between 20 and 30 degrees: {class3_pcnt}')
print(f'Percentage of site with slope between 30 and 40 degrees: {class4_pcnt}')
print(f'Percentage of site with slope geater than 40 degrees: {class5_pcnt}')
print(f'Check Sum: {sum([class1_pcnt, class2_pcnt, class3_pcnt, class4_pcnt, class5_pcnt])}')
