#!/usr/bin/env python 
#   Author: Christopher Bull. 
#   Affiliation: Climate Change Research Centre and ARC Centre of Excellence for Climate System Science.
#                Level 4, Mathews Building
#                University of New South Wales
#                Sydney, NSW, Australia, 2052
#   Contact: z3457920@student.unsw.edu.au
#   www:     christopherbull.com.au
#   Date created: Tue, 08 Mar 2016 01:43:11
#   Machine created on: chris-VirtualBox2
#
"""
Main file for plthacks package
"""

from _cblogger import _LogStart
_lg=_LogStart().setup()

import itertools
from matplotlib import gridspec
import matplotlib.pyplot as plt
import os
import numpy as np

#for inset axes
#hacked from:
#http://matplotlib.org/examples/axes_grid/inset_locator_demo.html
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

#for multiple plots
#from:http://stackoverflow.com/questions/18266642/multiple-imshow-subplots-each-with-colorbar 
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MultipleLocator

import math
import copy
from matplotlib import colors
import matplotlib

def mkdir(p):
    """make directory of path that is passed"""
    try:
       os.makedirs(p)
       _lg.info("output folder: "+p+ " does not exist, we will make one.")
    except OSError as exc: # Python >2.5
       import errno
       if exc.errno == errno.EEXIST and os.path.isdir(p):
          pass
       else: raise

def inset_title_box(ax,title,bwidth="20%",location=1):
    """
    Function that puts title of subplot in a box
    
    :ax:    Name of matplotlib axis to add inset title text box too
    :title: 'string to put inside text box'
    :returns: @todo
    """

    axins = inset_axes(ax,
                       width=bwidth, # width = 30% of parent_bbox
                       height=.30, # height : 1 inch
                       loc=location)

    plt.setp(axins.get_xticklabels(), visible=False)
    plt.setp(axins.get_yticklabels(), visible=False)
    axins.set_xticks([])
    axins.set_yticks([])

    axins.text(0.5,0.3,title,
            horizontalalignment='center',
            transform=axins.transAxes,size=10)

def cmap_center_point_adjust(cmap, range, center):
    '''
    converts center to a ratio between 0 and 1 of the
    range given and calls cmap_center_adjust(). returns
    a new adjusted colormap accordingly

    NB: nicked from https://sites.google.com/site/theodoregoetz/notes/matplotlib_colormapadjust
    '''

    def cmap_center_adjust(cmap, center_ratio):
        '''
        returns a new colormap based on the one given
        but adjusted so that the old center point higher
        (>0.5) or lower (<0.5)
        '''
        if not (0. < center_ratio) & (center_ratio < 1.):
            return cmap
        a = math.log(center_ratio) / math.log(0.5)
        return cmap_powerlaw_adjust(cmap, a)

    def cmap_powerlaw_adjust(cmap, a):
        '''
        returns a new colormap based on the one given
        but adjusted via power-law:

        newcmap = oldcmap**a
        '''
        if a < 0.:
            return cmap
        cdict = copy.copy(cmap._segmentdata)
        fn = lambda x : (x[0]**a, x[1], x[2])
        for key in ('red','green','blue'):
            cdict[key] = map(fn, cdict[key])
            cdict[key].sort()
            assert (cdict[key][0]<0 or cdict[key][-1]>1), \
                "Resulting indices extend out of the [0, 1] segment."
        return colors.LinearSegmentedColormap('colormap',cdict,1024)

    if not ((range[0] < center) and (center < range[1])):
        return cmap
    return cmap_center_adjust(cmap,
        abs(center - range[0]) / abs(range[1] - range[0]))

class Grid(object):
    """
    Class to create a gridded set of subplots from a dictionary.

    Parameters
    ----------
    pdict: dictionary containing the arrays to plot, titles are taken from the key
    pdims: tuple with (rowdim,coldim)
    sharex (optional): share all the x axis in the grid
    sharey (optional): share all the y axis in the grid
    dimlabels (optional): dictionary containing tuples of xlabel and ylabels 
    sepcbar (optional): separate colorbars for each subplot (True or False)
    globalclimits (optional): a single colorbar for the whole plot, where you manually specify the colour range
    globalcbar (optional): a single colorbar for the whole plot (string where the options are: 'True' which will use default colormap or name of matplotlib colormap). The format is: (cmin,cmax)
    globalcbarmiddle (optional): set the middle of the single colorbar for the whole plot
    cbars (optional): dictionary containing matplotlib colourbars to use
    clevels (optional): integer for the number of contour levels
    zoom (optional): integer tuple to zoom in on the plots of the form ((xmin,xmax),(ymin,ymax))
    outputpath (optional): full path of file to put plot in (if left out it won't be created)

    Returns
    -------
    
    Notes
    -------
    * If you use sepcbar, then best not to use sharex or sharey.
    * Many of the globalcbar options depend on a colour or 'True' being passed to globalcbar.
    

    Example
    --------
    >>> plotdict=collections.OrderedDict()
    >>> dimlab=collections.OrderedDict()
    >>> #create something to plot...
    >>> cnts=[str(cnt) for cnt in np.arange(11)+1]
    >>> for cnt in cnts:
    >>>     plotdict[cnt]=np.random.rand(20,15)
    >>>     dimlab[cnt]=('xlabel','ylabel')

    >>> Grid(plotdict,(4,3),sharex=True,outputpath=plotoutputs+'GridEgShareX.png')
    >>> Grid(plotdict,(4,3),sharey=True,outputpath=plotoutputs+'GridEgSHareY.png')
    >>> Grid(plotdict,(4,3),sharex=True,sharey=True,outputpath=plotoutputs+'GridEgShareXShareY.png')
    >>> Grid(plotdict,(4,3),dimlabels=dimlab,outputpath=plotoutputs+'GridEgDimLab.png')
    >>> Grid(plotdict,(4,3),sharex=True,sharey=True,dimlabels=dimlab,outputpath=plotoutputs+'GridEgShareXShareYDimLab.png')
    >>> plth.Grid(plotdict,(4,3),sharex=True,sharey=True,dimlabels=dimlab,globalcbar='True',globalcbarmiddle=0.8,zoom=((3,5),(5,10)),outputpath=plotoutputs+'GridEgShareXShareYDimLabGlobalcbarCustomGlobalcbarmiddleZoom.png')
    >>> plth.Grid(plotdict,(4,3),sharex=True,sharey=True,dimlabels=dimlab,globalcbar='True',globalcbarmiddle=0.8,globalclimits)
    >>> plth.Grid(plotdict,(4,3),sharex=True,sharey=True,dimlabels=dimlab,globalcbar='seismic',globalcbarmiddle=0.3,globalclimits=(0.15,0.78))
    """
    def __init__(self, pdict,pdims,sharex=False,sharey=False,clevels=0,dimlabels={},sepcbar=False,globalclimits=None,globalcbar='False',globalcbarmiddle=False,cbars={},zoom=None,outputpath=''):
        _lg.info("Creating a gridded plot from your passed dict")
        self.pdict,self.pdims = pdict,pdims
        self.sharex,self.sharey=sharex,sharey
        self.dimlabels=dimlabels
        self.sepcbar=sepcbar
        self.globalclimits=globalclimits
        self.globalcbar=globalcbar
        self.globalcbarmiddle=globalcbarmiddle
        self.cbars=cbars
        self.clevels=clevels
        self.outputpath=outputpath
        self.zoom=zoom
        self.mkplot()

    def mkplot(self):
        """@todo: Docstring for mkplot
        :returns: @todo
        """
        #set up for gridspec plot...

        subplotnum=len(self.pdict)

        plt.close('all')
        #width then height
        fig=plt.figure(figsize=(self.pdims[0]*4, self.pdims[1]*4))

        if self.sepcbar:
            fig=plt.figure(figsize=(self.pdims[0]*4, self.pdims[1]*5))

        if self.sharex:
            hs=.06

        else:
            hs=.225

        #make more space for separate colorbar..
        if self.sepcbar:
            hs+=.06

        if self.sharey:
            ys=.06
        else:
            ys=.08

        #make more space for lots of ylabels..
        if not self.sharey:
            ys+=.08

        #working out the global min and maxes of all fields so we can have one colourbar
        if self.globalcbar!='False':
            fgmin=np.min([np.min(field) for field in self.pdict.values()])
            fgmax=np.max([np.max(field) for field in self.pdict.values()])

            if self.globalclimits is not None:
                fgmin=self.globalclimits[0]
                fgmax=self.globalclimits[1]
            
            gs = gridspec.GridSpec(self.pdims[0], self.pdims[1]+1,\
                    width_ratios=[15]*self.pdims[1]+[1],hspace=hs,wspace=ys)
        else:
            gs = gridspec.GridSpec(self.pdims[0], self.pdims[1],hspace=hs,wspace=ys)

        names=itertools.cycle(self.pdict.keys())
        fields=itertools.cycle(self.pdict.values())
        if len(self.dimlabels.keys())!=0:
            labels=itertools.cycle(self.dimlabels.values())
            labelme=True
        else:
            labelme=False

        ax_xshares=[]
        ax_yshares=[]
        self.paxis={}
        pnum=1
        for rownum in range(self.pdims[0]):
            for colnum in range(self.pdims[1]):
                if pnum<=subplotnum:
                    # print rownum,colnum
                    # print pnum,subplotnum

                    #contour plot
                    name=names.next()
                    field=fields.next()
                    if labelme:
                        label=labels.next()

                    #put it in a list so we can append
                    #bad idea messing with the passed items if we iterate on the object (see tests)
                    # self.pdict[name]=[self.pdict[name]]

                    if rownum==0:
                        ax=plt.subplot(gs[rownum,colnum])
                        ax_xshares.append(ax)

                    #this if needs to be separate from the one above
                    if colnum==0:
                        ax=plt.subplot(gs[rownum,colnum])
                        ax_yshares.append(ax)

                    if self.sharex and rownum>0:
                        ax=plt.subplot(gs[rownum,colnum],sharex=ax_xshares[colnum])

                    if self.sharey and colnum>0:
                        ax=plt.subplot(gs[rownum,colnum],sharey=ax_yshares[rownum])

                        # make labels invisible
                        plt.setp(ax.get_yticklabels(),visible=False)

                    if not self.sharey and not self.sharex:
                        ax=plt.subplot(gs[rownum,colnum])
                        if labelme:
                            ax.set_xlabel(label[0])
                            ax.set_ylabel(label[1])

                    # self.pdict[name]=self.pdict[name].append(ax)
                    self.paxis[name]=ax

                    #
                    if self.globalcbar=='False': #when we are NOT using globalcbar
                        if len(self.cbars.keys())!=0:
                            if self.clevels!=0:
                                cs1=ax.contourf(field,levels=np.linspace(np.min(field),np.max(field),self.clevels),cmap=self.cbars[name])
                            else:
                                cs1=ax.contourf(field,cmap=self.cbars[name])
                        else:
                            if self.clevels!=0:
                                cs1=ax.contourf(field,levels=np.linspace(np.min(field),np.max(field),self.clevels))
                            else:
                                cs1=ax.contourf(field)
                    else: #when a globalcbar is being used

                        #what if we wanted a new centre?
                        if self.globalcbarmiddle:
                            if self.globalcbar=='True':
                                self.globalcbar='jet'
                            colourmap=cmap_center_point_adjust(matplotlib.cm.get_cmap(self.globalcbar),(fgmin,fgmax),self.globalcbarmiddle)
                        else:
                            colourmap=self.globalcbar

                        if self.clevels!=0:
                            if self.globalcbar=='True':
                                cs1=ax.contourf(field,levels=np.linspace(fgmin,fgmax,self.clevels))
                            else:
                                    cs1=ax.contourf(field,levels=np.linspace(fgmin,fgmax,self.clevels),cmap=colourmap)
                        else:
                            if self.globalcbar=='True':
                                cs1=ax.contourf(field,levels=np.linspace(fgmin,fgmax,7)) #defaulting to seven here!
                            else:
                                cs1=ax.contourf(field,levels=np.linspace(fgmin,fgmax,7),cmap=colourmap) #defaulting to seven here!


                    if self.sepcbar or len(self.cbars.keys())!=0:
                        #separate colorbars
                        # Create divider for existing axes instance
                        divider = make_axes_locatable(ax)
                        # Append axes to the right of ax, with 20% width of ax
                        caxis = divider.append_axes("bottom", size="10%", pad=0.45)
                        plt.colorbar(cs1,cax=caxis,orientation='horizontal')

                    # make xlabels invisible
                    if self.sharex and rownum<self.pdims[0]-1:
                        plt.setp(ax.get_xticklabels(),visible=False)

                    #labeling when we are sharing axis
                    if labelme:
                        if colnum==0:
                            ax.set_ylabel(label[1])

                        if rownum==self.pdims[0]-1:
                            ax.set_xlabel(label[0])

                    if self.zoom is not None:
                        ax.set_xlim([self.zoom[0][0],self.zoom[0][1]])
                        ax.set_ylim([self.zoom[1][0],self.zoom[1][1]])

                    # ax.set_title(name)
                    inset_title_box(ax,name)

                    pnum+=1

        if self.globalcbar!='False':
            ax1 = plt.subplot(gs[0:self.pdims[0]+1,self.pdims[1]])
            plt.colorbar(cs1,cax=ax1,orientation='vertical')

        if self.outputpath!='':
            mkdir(os.path.dirname(self.outputpath))
            plt.savefig(self.outputpath,dpi=300)
        else:
            plt.show()

        return self
    

if __name__ == "__main__": 
    pass

