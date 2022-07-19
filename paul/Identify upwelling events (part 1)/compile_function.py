# import necessary packages
import numpy as np

import xarray as xr

import matplotlib.dates as mdates

import warnings

warnings.simplefilter('ignore')

import glob


def Compile_Datasets(fn_list_in, lon_min=-180, lon_max=180, lat_min=-90, lat_max=90, remove_bay=True,
                     remove_anomalies=True):
    # fn_list_in: list of strings with the file names, or filename(string), or "all"
    # returns: compiled list
    fn_list = []

    ddir = "../../saildrone_data/"

    # Make sure the fn_list_in is formatted correctly
    if fn_list_in == "all":

        fn_list = glob.glob(ddir + '/*.nc')
    elif type(fn_list_in) is list and type(fn_list_in[0]) is str:
        for fn_item in fn_list_in:
            fn_list.append(ddir + fn_item)
    elif type(fn_list_in) == 'string':
        fn_list[0] = fn_list_in
    else:
        raise Exception(
            "first argument to 'Compile_Data_Set_And_Graph' "
            "function must be; a list of file names, a file name, or \"all\"")

    # open the first dataset
    sail = xr.open_dataset(fn_list[0])

    sail = sail.drop_vars("trajectory", errors='ignore')

    # give the first dataset a relative ID so all datasets can be differentiated
    sail["relativeID"] = 0

    # normalize longitude
    # sail["lon"] = Normalize_Longitude(sail["lon"]) # busdvvfs
    sail["lon"] = (np.mod(sail["lon"] + 180, 360) - 180)

    # make lists for certain variables that remain constant for each dataset. these are used later in the last two cells
    yearList = [sail["time"][0].dt.year]
    durationList = [sail["time"][len(sail["time"]) - 1] - sail["time"][0]]
    # take the actual cruise ID from the dataset attributes and put it in a new list
    try:
        realID = [int(sail.attrs["id"])]
    except:
        realID = [fn_list[0]]
    sail["realID"] = realID[0]
    # add the duration back to the dataset
    sail["duration"] = durationList[0]
    # extrapolate some extra variables
    sail["Delta_TEMP_CTD_MEAN"] = sail["TEMP_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
    sail["Delta_SAL_CTD_MEAN"] = sail["SAL_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
    sail = sail.drop_dims("obs", errors="ignore")
    sail = sail.drop_vars("obs", errors="ignore")

    # repeat previous steps for other datasets that need to be combined.

    if len(fn_list) > 1:
        for i in range(1, len(fn_list)):
            temp = xr.open_dataset(fn_list[i])
            temp = temp.drop_vars("trajectory", errors='ignore')
            temp["relativeID"] = i
            yearList.append(temp["time"][0].dt.year)

            try:
                realID.append(int(temp.attrs["id"]))
            except:
                realID.append(fn_list[i])

            tempDuration = temp["time"][len(temp["time"]) - 1] - temp["time"][0]
            temp["duration"] = tempDuration
            durationList.append(tempDuration)
            temp["realID"] = realID[i]

            # normalize longitude
            # temp["lon"] = Normalize_Longitude(temp["lon"]) #nsfbigb
            temp["lon"] = (np.mod(temp["lon"] + 180, 360) - 180)
            temp = temp.drop_vars("obs", errors="ignore")
            temp = temp.drop_dims("obs", errors="ignore")
            temp["Delta_TEMP_CTD_MEAN"] = temp["TEMP_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
            temp["Delta_SAL_CTD_MEAN"] = temp["SAL_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
            sail = xr.concat([sail, temp], dim="time", coords="minimal", compat="override",
                             combine_attrs="drop_conflicts")
            temp.close()

    # reformat dates
    sail['date'] = mdates.date2num(sail['time'].dt.date)

    # constrain region

    sail = sail.where((sail.lat <= lat_max) &
                      (sail.lat >= lat_min) &
                      (sail.lon <= lon_max) &
                      (sail.lon >= lon_min))

    # Removes SF bay data
    if remove_bay:
        sail = sail.where(~(((sail.lon > -122.5938) &
                             (sail.lat > 37.72783)) &
                            ((sail.lon < -122.2506620424831) &
                             (sail.lat < 38.094658646550556))) |
                          ~(((sail.lon > -122.38678630116495) &
                             (sail.lat > 37.430464705762226)) &
                            ((sail.lon < -121.99799777841487) &
                             (sail.lat < 37.81408437558721))))

    sail["Delta_TEMP_CTD_MEAN_STDEV"] = sail.std("time", True)["Delta_TEMP_CTD_MEAN"]
    sail["Delta_SAL_CTD_MEAN_STDEV"] = sail.std("time", True)["Delta_SAL_CTD_MEAN"]
    sail["VWND_MEAN_STDEV"] = sail.std("time", True)["VWND_MEAN"]

    if remove_anomalies:
        sail = sail.where((sail.Delta_TEMP_CTD_MEAN_STDEV < 6) &
                          (sail.Delta_SAL_CTD_MEAN_STDEV < 6) &
                          (sail.VWND_MEAN_STDEV < 6))
    return sail


def Normalize_Longitude(lon_list):
    out_list = []
    for lon in lon_list:
        if lon > 180:
            out_list.append(lon - 180)
        else:
            out_list.append(lon - 180)
    return out_list
    # return(np.mod(lon_list + 180,360) - 180)
