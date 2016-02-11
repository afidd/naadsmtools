import logging
import numpy as np
import h5py
from default_parser import DefaultArgumentParser

logger=logging.getLogger(__file__)


def combine_counts(starting, combine):
    for k, v in combine.items():
        if k not in starting:
            starting[k]=v
        else:
            starting[k]+=v
    return starting

def read_multiple_naadsmsc(filename, outfile):
    hdf=h5py.File(outfile, "w")
    hdf.create_group("/trajectory")

    allowed=dict()
    vals=list()
    run=-1
    transitions_type=dict([(b,a+10) for (a,b) in enumerate([(s,d) for s in range(6) for d in range(6) if s!=d])])
    transitions_type.update({(0,1) : 0, (1,3) : 1, (3,4) : 3, (4,0) : 4, (0,3) : 5, (0,4) : 6, (1,4) : 8})
    # lookup table for states from naadsm/gui/NAADSMLibrary.pas
    lookup = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, \
              'S': 0, 'L': 1, 'B': 2, 'C': 3, 'N': 4, 'V': 5, 'D': 6}
    with open(filename, "r") as f:
        line=f.readline()
        if len(line)<2:
            print(line, len(line))
        if line.startswith("node"):
            while line is not "":
                if line.startswith("node"):
                    x, n, x, r=line.strip().split()
                    n=int(n)
                    r=int(r)

                    if r!=run:
                        if len(vals)>0:
                            vals=np.vstack(vals)
                            allowed=combine_counts(allowed, show_transitions(vals))
                            events=events_from_states(vals, transitions_type)
                            save_h5(hdf, events)
                        vals=list()
                        run=r

                    line=f.readline()
                    states=[int(y) for y in line.strip().split()]
                    vals.append(np.array(states))

                line=f.readline()

        elif line.startswith("Iteration"):
            while True:
                if line.startswith("Iteration"):
                    x, r=line.strip().split()
                    r=int(r)

                if r!=run:
                    if len(vals)>0:
                        vals=np.vstack(vals)
                        allowed=combine_counts(allowed, show_transitions(vals))
                        events=events_from_states(vals, transitions_type)
                        save_h5(hdf, events)
                    vals=list()
                    run=r

                line=f.readline()
                if not line: break

                while (len(line) != 1) and (not line.startswith("Iteration")):
                    states=[lookup[y] for y in line.strip().split()]
                    vals.append(np.array(states))
                    line=f.readline()
                    if not line: break

            line=f.readline()
                
    if len(vals)>0:
        vals=np.vstack(vals)
        allowed=combine_counts(allowed, show_transitions(vals))
        events=events_from_states(np.vstack(vals), transitions_type)
        save_h5(hdf, events)

    return allowed



def show_transitions(state_array):
    allowed=dict()
    for i in range(1, len(state_array)):
        for j in range(0, state_array.shape[1]):
            previous=state_array[i-1][j]
            next=state_array[i][j]
            if previous!=next:
                key=(previous, next)
                if key not in allowed:
                    allowed[key]=0
                allowed[key]+=1
    return allowed


def events_from_states(state_array, transitions_dict):
    events=list()
    for i in range(1, len(state_array)):
        for j in range(0, state_array.shape[1]):
            previous=state_array[i-1][j]
            next=state_array[i][j]
            if previous!=next:
                key=(previous, next)
                event=transitions_dict[key]    
                day=i
                who=j
                whom=j
                events.append((event, whom, who, day))
    return events


def next_dset(openh5):
    maxnum=-1
    for name in openh5["/trajectory"]:
        if name.startswith("dset"):
            maxnum=max(maxnum, int(name[4:]))
    return maxnum+1


def save_h5(openh5, events):
    dset_idx=next_dset(openh5)
    group=openh5.create_group("/trajectory/dset{0}".format(dset_idx))
    event=group.create_dataset("Event", (len(events),), dtype="i")
    whom=group.create_dataset("Who", (len(events),), dtype="i")
    who=group.create_dataset("Whom", (len(events),), dtype="i")
    when=group.create_dataset("When", (len(events),), dtype=np.float64)
    for eidx in range(len(events)):
        aevent, awhom, awho, aday=events[eidx]
        event[eidx]=aevent
        whom[eidx]=awhom
        who[eidx]=awho
        when[eidx]=aday



if __name__ == "__main__":
    parser=DefaultArgumentParser(description="Produces HDF5 event file from trace data")
    parser.add_argument("--input", dest="infile", action="store",
        default="naadsm.out", help="Input trace from NAADSM")
    parser.add_argument("--output", dest="outfile", action="store",
        default="naadsm.h5", help="HDF5 file with events")
    args=parser.parse_args()

    allowed_transitions=read_multiple_naadsmsc(args.infile, args.outfile)
    logger.info("allowed transitions are {0}.".format(allowed_transitions))


