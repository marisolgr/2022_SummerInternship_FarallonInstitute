# import necessary packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings

# load map packages
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.feature as cfeature
import cartopy.crs as ccrs

warnings.simplefilter('ignore')


def trajectory_plot(dataset, var_to_plot, show=True, save_path=None, func_dpi=300):
    # dataset: the dataset to get data from (Dataset)
    # var_to_plot: the variable to be represented by color (String)
    # show: should the plot be displayed (Bool)
    # save_path: the path to save the image. '.png' will be added automatically. (string)
    # func_dpi: the DPI of the returned image (int)
    # does not return anything

    # reformat dates
    # dataset['date'] = mdates.date2num(dataset['time'].dt.date)

    # make sure that variable is in the list
    if var_to_plot in dataset.data_vars:

        # define latitude and longitude boundaries
        latr = [np.nanmin(dataset['lat'].values), np.nanmax(dataset['lat'].values)]
        lonr = [np.nanmax(dataset['lon'].values), np.nanmin(dataset['lon'].values)]

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
        fig = plt.figure(figsize=(16, 9), dpi=func_dpi)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='10m', linewidth=1, color='black')
        ax.add_feature(cfeature.LAND, color='grey', alpha=0.3)
        ax.add_feature(states_provinces, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS)
        ax.set_extent([region[1, 0], region[1, 1], region[0, 0], region[0, 1]], crs=ccrs.PlateCarree())
        ax.set_xticks(np.round([*np.arange(region[1, 1], region[1, 0] + 1, 25)][::-1], 0), crs=ccrs.PlateCarree())
        ax.set_yticks(np.round([*np.arange(np.floor(region[0, 0]), region[0, 1] + 1, 15)], 1), crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.gridlines(linestyle='--', linewidth=0.5)

        # Plot track data, color by temperature

        sc = plt.scatter(x=dataset['lon'], y=dataset['lat'], c=dataset[var_to_plot], cmap='jet')

        # make the colorbar with 20 evenly spaced labels
        clb = plt.colorbar(sc, ticks=np.linspace(np.nanmin(dataset[var_to_plot]), np.nanmax(dataset[var_to_plot]), 20))
        # fraction=0.046, pad=0.1)
        clb.ax.set_title(var_to_plot)

        # title the graph
        plt.title('Sampling Track for Cruise', fontdict={'fontsize': 16})

        # save file
        if save_path is not None:
            print("save attempt")
            plt.savefig(save_path + '.png')
        if show:  # show and clear the plt object
            plt.show()
        else:
            plt.clf()

    else:  # if the variable the user wants to plot is not in the dataset, give an error
        raise Exception("variable must be in the list")
    return "mogus"
