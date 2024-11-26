import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm, ticker,colors
import matplotlib.gridspec as gridspec

import read_dat

from spectra import spectralmap

def depth_wl_contourf_lin(ds, data_var="eu"):
    ds["depth_int"] = ds.depth.astype(int)
    dsd = ds.groupby(ds.depth_int).mean()
    plt.clf()
    ax = plt.subplot(111)
    cticks = np.arange(1,160,20)
    plt.contourf(dsd.wavelength, dsd.depth, dsd[data_var], cticks)
    plt.ylim(60,2)
    ax2 = ax.twinx()
    ax2.set_yticks([]) ##No ticks for the secondary axis

    cbar = plt.colorbar()
    cbar.set_ticks(ticks=[1, 40, 80, 120, 140])
    if data_var=="eu":
        dv_str = "Downwelling Irridiance (E$_u$, $\\mu$W cm$^{-2}$ nm$^{-1}$)"
    ax2.set_ylabel(dv_str)
    #cbar.set_label(dv_str, rotation=270)
    ax.set_ylabel("Depth (m)")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_facecolor('0.3')
    plt.title(pd.to_datetime(ds.time[0].item()).strftime("%Y-%m-%d %H:%M"))
    spectrum_stripe(ax)


def depth_wl_contourf_log(ds, data_var="eu"):
    ds["depth_int"] = ds.depth.astype(int)
    dsd = ds.groupby(ds.depth_int).mean()
    plt.clf()
    ax = plt.subplot(111)
    #plt.contourf(dsd.wavelength, dsd.depth, np.log(dsd.eu), np.linspace(-1,5,10))
    cticks = np.arange(-1,2.5,0.25) #np.logspace(np.log10(0.1), np.log10(150), 10)
    cf = ax.contourf(dsd.wavelength, dsd.depth, np.log10(dsd[data_var]), cticks)
    
    #                 locator=ticker.LogLocator(10))
    #                 norm=colors.LogNorm())
    #             locator=ticker.LogLocator(), cmap=cm.PuBu_r)
    ax.set_ylim(60,2)
    ax2 = ax.twinx()
    ax2.set_yticks([]) ##No ticks for the secondary axis

    cbar = plt.colorbar(cf)
    cbar.set_ticks(ticks=[-1, 0, 1, 2], labels=['0.1', '1', '10', '100'])
    if data_var=="eu":
        dv_str = "Downwelling Irridiance (E$_u$, $\\mu$W cm$^{-2}$ nm$^{-1}$)"
    ax2.set_ylabel(dv_str)
    #cbar.set_label(dv_str, rotation=270)
    ax.set_ylabel("Depth (m)")
    #plt.xlabel("Wavelength (nm)")
    ax.set_facecolor('0.3')
    spectrum_stripe(ax)
    plt.suptitle(pd.to_datetime(ds.time[0].item()).strftime("%Y-%m-%d %H:%M"))
    

def all_log_contours():

    for fn in glob.glob("ascii/ftk240412-*-*_L2.dat"):
        dflist = read_dat.load(filename=fn)
        ds = read_dat.to_xarray(dflist)
        depth_wl_contourf_log(ds, data_var="eu")
        figname = pd.to_datetime(ds.time[0].item()).strftime("%Y-%m-%d_%H-%M")
        figname = "EU_contourf_" + figname
        plt.savefig(f"figs/log_contours/png/{figname}.png")
        plt.savefig(f"figs/log_contours/pdf/{figname}.pdf")


def all_lin_contours():

    for fn in glob.glob("ascii/ftk240412-*-*_L2.dat"):
        dflist = read_dat.load(filename=fn)
        ds = read_dat.to_xarray(dflist)
        depth_wl_contourf_lin(ds, data_var="eu")
        figname = pd.to_datetime(ds.time[0].item()).strftime("%Y-%m-%d_%H-%M")
        figname = "EU_contourf_" + figname
        plt.savefig(f"figs/lin_contours/png/{figname}.png")
        plt.savefig(f"figs/lin_contours/pdf/{figname}.pdf")

def fig():
    plt.clf()
    #ax1 = plt.subplot2grid((20, 1), (0, 0), rowspan=19)
    #ax2 = plt.subplot2grid((20, 1), (19, 0))#, sharex=ax1)

    wavelengths = np.linspace(350, 800, 1000)
    y = np.linspace(0, 6, 100)
    X,Y = np.meshgrid(wavelengths, y)
    extent = (350.0, 800.0, 0.0, 6.0)

    gs = gridspec.GridSpec(20, 1)
    ax1 = plt.subplot(gs[:19, 0])
    ax2 = plt.subplot(gs[-1, 0])
    ax1.set_xlim(350,800)
    ax1.set_xticklabels([])
    ax2.axes.get_yaxis().set_visible(False)
    ax2.set_xlim(350,800)
    ax2.imshow(X, clim=(350, 780), extent= extent, 
               cmap=spectralmap(), aspect='auto')

    plt.gcf().tight_layout(w_pad=0.01)
    gs.update(wspace=-0.1)

    return ax1,ax2


def pcolor_spectra(ax):
    wavelengths = np.linspace(350, 800, 1000)
    y = np.linspace(0, 6, 100)
    X,Y = np.meshgrid(wavelengths, y)
    extent = (350.0, 800.0, 0.0, 6.0)
    ax.imshow(X, clim=(350, 780), extent= extent,
              cmap=spectralmap(), aspect='auto')

def colfig():
    plt.close(1)
    fig,axes = plt.subplots(2,1, num=1)
    pos1 = [0.1, 0.1,  0.8, 0.8]
    axes[0].set_position(pos1)
    pos2 = [0.1, 0.12,  0.8, 0.04]
    axes[1].set_position(pos2)
    axes[1].axes.get_yaxis().set_visible(False)
    axes[1].axes.get_xaxis().set_visible(False)
    axes[0].set_xlim(350,800)
    axes[1].set_xlim(350,800)
    pcolor_spectra(axes[1])
    axes[0].set_xlabel("Wavelength (nm)")
    return axes[0]

def spectrum_stripe(ax, fig=None):
    fig = plt.gcf() if fig is None else fig
    pos1 = ax.get_position()
    pos2 = [pos1.x0, pos1.y0+0.02,  pos1.width, pos1.height / 40] 

    ax2 = fig.add_subplot(sharex=ax)
    ax2.set_position(pos2)
    ax2.axes.get_yaxis().set_visible(False)
    ax2.axes.get_xaxis().set_visible(False)
    ax2.set_xlim(350,800)
    pcolor_spectra(ax2)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_xlim(350,800)


