import matplotlib.pyplot as plt

line_lyr = QgsProject.instance().mapLayersByName('New scratch layer')[0]
rl = QgsProject.instance().mapLayersByName('srtm_63_16')[0]

line_geom = [f.geometry() for f in line_lyr.getFeatures()][0]

da = QgsDistanceArea()
da.setSourceCrs(line_lyr.sourceCrs(), QgsProject.instance().transformContext())
da.setEllipsoid(line_lyr.sourceCrs().ellipsoidAcronym())

line_length = line_geom.length()

converted_line_length = da.convertLengthMeasurement(da.measureLength(line_geom), QgsUnitTypes.DistanceKilometers)

num_profile_pts = 50

interp_dist = line_length/num_profile_pts

converted_interp_dist = converted_line_length/num_profile_pts
td = converted_interp_dist

total_dist = interp_dist

sample_geoms = []

distances = []

while total_dist < line_length:
    sample_geoms.append(line_geom.interpolate(total_dist))
    total_dist+=interp_dist
    td+=converted_interp_dist
    distances.append(td)
    
#print(sample_pts)

plot_vals = [rl.dataProvider().sample(geom.asPoint(), 1)[0] for geom in sample_geoms]

plt.plot(distances, plot_vals, label='Profile', color='brown', linewidth=2)

plt.xlabel("Distance (Kilometers)")
plt.ylabel("Elevation (Meters)")

plt.show()