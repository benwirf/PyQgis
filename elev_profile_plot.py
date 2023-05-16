
import matplotlib.pyplot as plt

line_lyr = QgsProject.instance().mapLayersByName('New scratch layer')[0]
rl = QgsProject.instance().mapLayersByName('srtm_64_18')[0]

line_geom = [f.geometry() for f in line_lyr.getFeatures()][0]

line_length = line_geom.length()
print(line_length)

################################################
rl_stats = rl.dataProvider().bandStatistics(1)
rl_extent = rl_stats.extent
extent_width = rl_extent.width()
extent_height = rl_extent.height()
row_count = rl_stats.height
col_count = rl_stats.width
pixel_height = extent_height/row_count
pixel_width = extent_width/col_count
pixel_size = (pixel_height + pixel_width)/2
################################################

total_dist = pixel_size

sample_geoms = []

while total_dist < line_length:
    sample_geoms.append(line_geom.interpolate(total_dist))
    total_dist+=pixel_size

plot_vals = [rl.dataProvider().sample(geom.asPoint(), 1)[0] for geom in sample_geoms]

plt.plot(plot_vals, label='Profile', color='brown', linewidth=2)

plt.show()
#plt.cla()