# Compile data and plot some stuff
# By: Paul 7/05/22


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
import glob

warnings.simplefilter('ignore')

# Set currentYear to the current year. This is used for bounds on certain graphs
currentYear = int(date.today().year)

# load map packages
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from calendar import month_abbr


def Compile_Data_Set_And_Graph(fn_list_in, variable_to_plot, save_folder="Saved Graphs", show_plot=False, ):

    # fn_list: a list of strings for the directory of the datasets. Give "All" to read all
    # variable_to_plot: the variable to plot. must be a string that is a variable in the compiled dataset
    # save_folder: a string for a folder that the graphs should be saved in.
    # show_plot: should the graphs be displayed?
    # Returns the compiled list of data

    # set the 'root' directory for all saildrone data
    ddir = "/shared/users/mgarciareyes/saildrone_data"
    
    if(fn_list_in == "all"):
        fn_list = glob.glob(ddir+ '*.nc')
    elif(type(fn_list_in) == 'list' and type(fn_list_in[0]) == 'string'):
        fn_list = fn_list_in
    elif(type(fn_list_in) == 'string'):
        fn_list[0] = fn_list_in
    else: 
        raise Exception("first argument to 'Compile_Data_Set_And_Graph' function must be; a list of file names, a file name, or \"all\"")
    
    # open the first dataset
    sail = xr.open_dataset(ddir + fn_list[0])
    # give the first dataset a relative ID so all datasets can be differentiated
    sail["relativeID"] = 0
    # make lists for certain variables that remain constant for each dataset. these are used later in the last two cells
    yearList = [sail["time"][0].dt.year]
    durationList = [sail["time"][len(sail["time"]) - 1] - sail["time"][0]]
    # take the actual cruise ID from the dataset attributes and put it in a new list
    realID = [int(sail.attrs["id"])]
    # add the duration back to the dataset
    sail["duration"] = durationList[0]

    # repeat previous steps for other datasets that need to be combined.

    if len(fn_list) > 1:
        for i in range(1, len(fn_list)):
            temp = xr.open_dataset(ddir + fn_list[i])
            temp["relativeID"] = i
            yearList.append(temp["time"][0].dt.year)
            realID.append(int(temp.attrs["id"]))
            tempDuration = temp["time"][len(temp["time"]) - 1] - temp["time"][0]
            temp["duration"] = tempDuration
            durationList.append(tempDuration)
            sail = xr.concat([sail, temp], dim="time")
            temp.close()

    # reformat dates
    sail['date'] = mdates.date2num(sail['time'].dt.date)

    # ask what variable should be plotted

    var_to_plot = variable_to_plot
    # make sure that variable is in the list
    if var_to_plot in sail.data_vars:

        # default_x_ticks = range(0,max(sail[var_to_plot]),divmod(max(sail[var_to_plot]), 10)[0]) #selects out 10 evenly spaced dates from the data
        # define latitude and longitude boundaries
        latr = [min(sail['lat']), max(sail['lat'])]
        lonr = [max(sail['lon']), min(sail['lon'])]

        # Select a region of our data, giving it a margin
        margin = 0.5
        region = np.array([[latr[0] - margin, latr[1] + margin], [lonr[0] + margin, lonr[1] - margin]])

        # add state outlines
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')

        # Create and set the figure context
        fig = plt.figure(figsize=(16, 10), dpi=300)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='10m', linewidth=1, color='black')
        ax.add_feature(cfeature.LAND, color='grey', alpha=0.3)
        ax.add_feature(states_provinces, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS)
        ax.set_extent([region[1, 0], region[1, 1], region[0, 0], region[0, 1]], crs=ccrs.PlateCarree())
        ax.set_xticks(np.round([*np.arange(region[1, 1], region[1, 0] + 1, 2)][::-1], 0), crs=ccrs.PlateCarree())
        ax.set_yticks(np.round([*np.arange(np.floor(region[0, 0]), region[0, 1] + 1, 1.5)], 1), crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.gridlines(linestyle='--', linewidth=0.5)

        # Plot track data, color by temperature

        sc = plt.scatter(x=sail['lon'], y=sail['lat'], c=sail[var_to_plot], cmap='jet')

        # make the colorbar with 20 evenly spaced labels
        clb = fig.colorbar(sc, ticks=np.linspace(min(sail[var_to_plot]), max(sail[var_to_plot]), 20))
        clb.ax.set_title(var_to_plot)

        # title the graph
        plt.title('Sampling Track for Cruise', fontdict={'fontsize': 16})

        # remove slashes from variable name to make sure it it saved correctly
        sanitized_var_to_plot = var_to_plot.replace("/", "")

        # save file
        plt.savefig(save_folder + '/Sampling Track of ' + sanitized_var_to_plot + '.png')

        # show and clear the plt object
        if (show_plot):
            plt.show()
        else:
            plt.clf

    else:  # if the variable the user wants to plot is not in the dataset, give an error
        raise Exception("variable must be in the list: " + str(sail.data_vars))

    # PLOT 2    
    
    # initialize variables and objects
    fig = plt.figure(figsize=(20, 10), dpi=300)
    ax = plt.axes()
    # plot the data
    pl_obj = plt.scatter(x=sail["relativeID"], y=sail['time'].dt.year, s=sail['duration'].dt.days * 100,
                         c=sail['time'].dt.dayofyear, cmap='jet', vmin=0, vmax=365)  #
    # Add the colorbar
    clb = fig.colorbar(pl_obj, ticks=range(0, 365, 10))
    clb.ax.set_title("day of year")
    # Label and add tick marks to the axes
    ax.set(xlim=(-1, max(sail["relativeID"]) + 1), xticks=np.arange(-1, max(sail["relativeID"])) + 1,
           ylim=(2015, currentYear), yticks=np.arange(2015, currentYear))
    ax.set_ylabel("year")
    ax.set_xlabel("relative IDs")

    # annotate points with more information
    # Because the Cruise IDs are so arbitrary and spread out, they can't be plotted without the graph looking weird

    annotate = True
    if (annotate):
        # for each original dataset
        for i in range(len(realID)):
            # get the duration in days. (durationList stores nanoseconds)
            duration = float(durationList[i]) / 86400000000000
            # calculate the offset the text should be from the center of the point. Purely visual calculation.
            xOffset = np.sqrt(duration) / 40
            # annotate the cruise ID
            plt.annotate(("Cruise ID: " + str(realID[i]))
                         , (i + xOffset, yearList[i]))
            # annotate the duration
            plt.annotate(("duration (days): " + str(round(duration)))
                         , (i + xOffset, yearList[i] - 0.15))

    # title the graph
    plt.title('When are cruise', fontdict={'fontsize': 16})
    # save the plot as a png
    plt.savefig(save_folder + '/When are cruise.png')
    # show and clear the plt object
    plt.show()

    if (show_plot):
        plt.show()
    else:
        plt.clf

        
    # PLOT 3 
    
    # initialize variables and objects
    fig = plt.figure(figsize=(20, 10), dpi=300)
    ax = plt.axes()
    # plot the data
    pl_obj = plt.scatter(x=sail['time'].dt.dayofyear, y=sail["relativeID"], s=100, c=sail['lat'], cmap='jet')
    # Add the colorbar
    clb = fig.colorbar(pl_obj, ticks=np.linspace(min(sail['lat']), max(sail['lat']), 10))
    clb.ax.set_title("Flatitude")
    # Label and add tick marks to the axes
    ax.set(xlim=(-40, 365), xticks=range(0, 365, 20),
           ylim=(-1, max(sail["relativeID"]) + 1), yticks=np.arange(0, max(sail["relativeID"]) + 1))
    ax.set_ylabel("Cruise ID within dataset")
    ax.set_xlabel("Day of year")

    # add real cruise IDs to the left of the graph
    for i in range(len(realID)):
        duration = float(durationList[i]) / 86400000000000

        xOffset = np.sqrt(duration) / 40

        plt.annotate(("Cruise ID: " + str(realID[i]))
                     , (-39, i))

    # title the graph
    plt.title('When are cruise', fontdict={'fontsize': 16})
    # save the plot as a png
    plt.savefig(save_folder + '/When are cruise - part 2 electric bugaloo.png')
    # show and clear the plt object
    

    if (show_plot):
        plt.show()
    else:
        plt.clf
        
        
        
    # PLOT 4
    
    # initialize variables and objects
    fig = plt.figure(figsize=(20,10), dpi = 300) 
    ax = plt.axes()
    # plot the data
    pl_obj = plt.scatter(x =sail['time'] , y =sail["relativeID"], s = 100, c = sail['lat'], cmap='jet')
    # Add the colorbar
    clb = fig.colorbar(pl_obj, ticks=np.linspace(min(sail['lat']),max(sail['lat']),10))
    clb.ax.set_title("Flatitude")
    # make a variable with the timedelta of graph
    td = max(sail['time']) - min(sail['time'])
    # Label and add tick marks to the axes 
    ax.set(xlim=(min(sail['time'])-(td/9), max(sail['time'])+td/100),
        ylim=(-1, max(sail["relativeID"])+1), yticks = np.arange(0, max(sail["relativeID"])+1))
    ax.set_ylabel("Cruise ID within dataset")
    ax.set_xlabel("Day of year")

    # add real cruise IDs to the left of the graph
    for i in range(len(realID)):

        duration = float(durationList[i])/86400000000000

        xOffset = np.sqrt(duration)/40

        plt.annotate(("Cruise ID: " + str(realID[i]))
                     , (-39, i))


    # title the graph
    plt.title('When are cruise', fontdict = {'fontsize' : 16})
    # save the plot as a png
    plt.savefig(save_folder + '/When are cruise - part 3.png')
    # show and clear the plt object
    if (show_plot):
        plt.show()
    else:
        plt.clf
        
        
    return(sail)
