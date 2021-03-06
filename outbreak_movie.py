"""
outbreak_movie.py makes an mp4-encoded animation of an outbreak from data in an HDF5-encoded event file.  This requires a separately installed mpeg encoder such as ffmpeg.

animation process uses the following previous work:

Rain simulation: Simulates rain drops on a surface by animating the scale and opacity
of 50 scatter points. (Author: Nicolas P. Rougier)
"""
import logging
import sys
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from  matplotlib.animation import FuncAnimation
import locations

_degrees_to_radians=np.pi/180
_radians_km=180*60*1.852/np.pi

logger=logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

def datasets(open_file):
    trajectories=open_file['/trajectory']
    names=list()
    for trajectory_name in trajectories:
        if trajectory_name.startswith("dset"):
            names.append(trajectory_name)
    return names

def transitions(open_file, herd_file):
    loc=locations.load_herd_locations(herd_file)
    trajectory_name=datasets(open_file)[0]
    dset=open_file["/trajectory/{0}".format(trajectory_name)]

    event=dset["Event"]
    who=dset["Who"]
    whom=dset["Whom"]
    when=dset["When"]
    ret=[np.array(loc)]
    ret.extend([np.array(x) for x in [event, who, whom, when]])
    return ret

def distancekm(latlon1, latlon2):
    """Distance computed on a spherical earth.
    Taken from http://williams.best.vwh.net/avform.htm."""
    ll1=latlon1*_degrees_to_radians
    ll2=latlon2*_degrees_to_radians
    return _radians_km*(2*np.arcsin(np.sqrt(np.power(np.sin((ll1[0]-ll2[0])/2),2)+
        np.cos(ll1[0])*np.cos(ll2[0])*np.power(np.sin((ll1[1]-ll2[1])/2), 2))))

def map_proj():
    import pyproj
    # This is a projection for South Carolina
    sc_proj='+proj=lcc +lat_1=32.5 +lat_2=34.83333333333334 +lat_0=31.83333333333333 +lon_0=-81 +x_0=609600 +y_0=0 +datum=NAD83 +units=ft +no_defs '
    projection=pyproj.Proj(sc_proj)
    return projection

def update(frame_number):
    # Get an index which we can use to re-spawn the oldest raindrop.
    logger.debug("frame_number {0}".format(frame_number))
    current_time = frame_number*end_time/frame_cnt

    # Make all colors more transparent as time progresses.
    rain_drops['color'][:, 3] -= 1.0/len(rain_drops)
    rain_drops['color'][:,3] = np.clip(rain_drops['color'][:,3], 0, 1)

    # Make all circles bigger.
    rain_drops['size'] += rain_growth_rate
    (einfect, eclinical, erecover, ewane)=(0, 1, 2, 3)

    global event_idx
    global locations_scaled
    global ax
    global event
    global when
    global who
    global whom
    while event_idx<len(event) and \
            when[event_idx]<current_time:
        farm_idx=whom[event_idx]-1
        source_idx=who[event_idx]-1
        now=when[event_idx]
        what=event[event_idx]
        if what==einfect:
            logger.debug("changing farm {0}".format(farm_idx))
            farms['color'][farm_idx] = color_code['infected']
            rain_drops['size'][farm_idx]=marker_size
            rain_drops['color'][farm_idx, 3]=1.0
            if source_idx != farm_idx:
                x0, y0=locations_scaled[source_idx,:]
                x1, y1=locations_scaled[farm_idx,:]
                dx=x1-x0
                dy=y1-y0
                r=np.sqrt(dx*dx+dy*dy)
                dr=0.04 # Want to reduce length by fixed distance
                g=(r-dr)/r
                if g<0:
                    g=0.1
                logger.info("x0 {0} x1 {1}".format(x0, x1))
                ax.arrow(x0, y0, g*dx, g*dy, head_width=0.01, head_length=0.02,
                    fc='k', ec='k')
        event_idx+=1


    # Update the scatter collection, with the new colors, sizes and positions.
    farms_scat.set_facecolors(farms['color'])
    rain_scat.set_edgecolors(rain_drops['color'])
    rain_scat.set_sizes(rain_drops['size'])

if __name__ == '__main__':
    import sys, os.path, getopt
    data_file = "run.h5"
    output_file = "run.mp4"
    herd_file = None
    initially_infected = []

    options, arguments = getopt.getopt(sys.argv[1:], "i:u:o:I:")

    for option, value in options:
        print(option,value)
        if option == "-i":
            data_file = value
        if option == "-u":
            herd_file = value
        if option == "-o":
            output_file = value
        if option == "-I":
            try:
                initially_infected = [int(e) for e in value.split(',')]
            except:
                raise IOError("list of initially infected units must be a comma-separated string of integers, e.g., 1,2,3")

    if herd_file is None:
        print("Error: must specify a unit (herd) file, using -u flag")
        exit()

    f=h5py.File(data_file)
    locations, event, who, whom, when=transitions(f, herd_file)
    logger.debug("event {0}".format(event))
    logger.debug("who {0}".format(who))
    logger.debug("whom {0}".format(whom))
    logger.debug("when {0}".format(when))

    color_choice={'susceptible' : 'black', 'infected' : 'orangered'}
    color_code=dict()
    for disease_name, cname in color_choice.items():
        r, g, b=mcolors.hex2color(mcolors.cnames[cname])
        color_code[disease_name]=np.array((r, g, b, 1.0))

    # Create new Figure and an Axes which fills it.
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    ax.set_xlim(0,1), ax.set_xticks([])
    ax.set_ylim(0,1), ax.set_yticks([])

    # Create rain data
    n_drops = locations.shape[0]
    projection=map_proj()
    projected=locations[:,:]
    for i in range(locations.shape[0]):
        projected[i,:]=np.array(projection(locations[i,1], locations[i,0]))
    logger.debug("projected {0}".format(projected))

    max_x=np.max(projected[:,0])
    min_x=np.min(projected[:,0])
    max_y=np.max(projected[:,1])
    min_y=np.min(projected[:,1])
    locations_scaled=(projected-np.array([min_x, min_y]))*np.array(
        [1.0/(max_x-min_x), 1.0/(max_y-min_y)])
    #logger.debug(locations_scaled)
    logger.debug("min farm {0} max farm {1}".format(np.min(whom), np.max(whom)))
    farm_cnt = n_drops
    last_infection=np.where(event==0)[0]
    end_time=when[last_infection[-1]]*1.05
    frame_cnt=int(end_time)+1
    frame_interval=int(10000/frame_cnt)
    logger.debug("end_time {0}".format(end_time))
    logger.debug("frame_cnt {0}".format(frame_cnt))
    logger.debug("frame_interval {0}".format(frame_interval))

    event_idx=0

    farms = np.zeros(n_drops,
                     dtype=[('position', float, 2),('size', float, 1), ('color', float, 4)])

    marker_size=100

    # Initialize the raindrops in random positions and with
    # random growth rates.
    farms['position'] = locations_scaled #np.random.uniform(0, 1, (n_drops, 2))
    farms['size'].fill(marker_size)
    farms['color'][:]=color_code['susceptible']

    rain_growth_rate=50

    rain_drops = np.zeros(n_drops, dtype=[('position', float, 2),
                                        ('size',     float, 1),
                                        ('color',    float, 4)])

    rain_drops['position'] = farms['position']
    rain_drops['size'].fill(marker_size)
    rain_drops['color'][:]=np.array((0.0, 0.0, 0.0, 0.0))

    # Construct the scatter which we will update during animation
    # as the raindrops develop.
    farms_scat = ax.scatter(farms['position'][:,0], farms['position'][:,1],
                    s=farms['size'], lw=0.5, facecolors=farms['color'],
                    edgecolors='none')
    rain_scat = ax.scatter(rain_drops['position'][:,0], rain_drops['position'][:,1],
                    s=rain_drops['size'], lw=0.5, facecolors='none',
                    edgecolors=rain_drops['color'])

    # Add infection for the initially infected sites
    for idx in initially_infected:
        farm_idx=idx-1
        farms['color'][farm_idx] = color_code['infected']
        rain_drops['size'][farm_idx]=marker_size
        rain_drops['color'][farm_idx, 3]=1.0

    # Construct the animation, using the update function as the animation
    # director.
    animation = FuncAnimation(fig, update, frames=frame_cnt,
        interval=frame_interval, repeat=False)
    plt.show()
    animation.save(output_file)
