# Change 'test_points' to your layer name
lyr = QgsProject.instance().mapLayersByName('test_points')[0]

fld_name_1 = 'Effort'
fld_name_2 = 'Beaufort'

fld_1_idx = lyr.fields().lookupField(fld_name_1)
fld_2_idx = lyr.fields().lookupField(fld_name_2)

def get_last_non_null(lyr, fid, fld_name):
    val = NULL
    if fid == 0:
        return val
    while val == NULL:
        prev_ft = lyr.getFeature(fid-1)
        if prev_ft[fld_name] == NULL:
            fid -= 1
        else:
            val = prev_ft[fld_name]
    return val
    
atts = {}

for ft in lyr.getFeatures():
    if ft[fld_name_1] == NULL and ft[fld_name_2] != NULL:
        prev_val = get_last_non_null(lyr, ft.id(), fld_name_1)
        atts[ft.id()] = {fld_1_idx: prev_val}
    elif ft[fld_name_2] == NULL and ft[fld_name_1] != NULL:
        prev_val = get_last_non_null(lyr, ft.id(), fld_name_2)
        atts[ft.id()] = {fld_2_idx: prev_val}
    elif ft[fld_name_2] == NULL and ft[fld_name_1] == NULL:
        prev_val_fld_1 = get_last_non_null(lyr, ft.id(), fld_name_1)
        prev_val_fld_2 = get_last_non_null(lyr, ft.id(), fld_name_2)
        atts[ft.id()] = {fld_1_idx: prev_val_fld_1, fld_2_idx: prev_val_fld_2}
    else:
        continue
                
lyr.dataProvider().changeAttributeValues(atts)
        