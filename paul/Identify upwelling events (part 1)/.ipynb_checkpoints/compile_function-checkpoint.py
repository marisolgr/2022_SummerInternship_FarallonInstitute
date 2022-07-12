   
# import necessary packages
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime
from datetime import date
import warnings

warnings.simplefilter('ignore')

# load map packages
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from calendar import month_abbr    
import glob
    
    
    
    
    
    
def Compile_Datasets(fn_list_in):


    # fn_list_in: list of strings with the file names, or filename(string), or "all"
    # returns: compiled list
    fn_list = []
    
    ddir = "../../saildrone_data"
    
    # Make sure the fn_list_in is formatted correctly
    if(fn_list_in == "all"):
        
        fn_list = glob.glob(ddir+ '/*.nc')
    elif(type(fn_list_in) == 'list' and type(fn_list_in[0]) == 'string'):
        fn_list = fn_list_in
    elif(type(fn_list_in) == 'string'):
        fn_list[0] = fn_list_in
    else: 
        raise Exception("first argument to 'Compile_Data_Set_And_Graph' function must be; a list of file names, a file name, or \"all\"")
        

    
    # open the first dataset
    sail = xr.open_dataset(fn_list[0])
    
    sail = sail.drop_vars("trajectory", errors='ignore')
    
    # give the first dataset a relative ID so all datasets can be differentiated
    sail["relativeID"] = 0
    
    # normalize longitude
    # sail["lon"] = Normalize_Longitude(sail["lon"]) # busdvvfs
    sail["lon"] = (np.mod(sail["lon"] + 180,360) - 180)
    
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
            temp["lon"] = (np.mod(temp["lon"] + 180,360) - 180)
            
            temp["Delta_TEMP_CTD_MEAN"] = temp["TEMP_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
            temp["Delta_SAL_CTD_MEAN"] = temp["SAL_CTD_MEAN"].differentiate("time", edge_order=1, datetime_unit="D")
            
            sail = xr.concat([sail, temp], dim="time")
            temp.close()

    # reformat dates
    sail['date'] = mdates.date2num(sail['time'].dt.date)

    # ask what variable should be plotted
    return(sail)




def Normalize_Longitude(lon_list):
    out_list = []
    for lon in lon_list:
        if(lon>180):
            out_list.append(lon-180)
        else:
            out_list.append(lon-180)
    return(out_list)
    # return(np.mod(lon_list + 180,360) - 180)
