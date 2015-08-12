"""
These routines manipulate the NAADSM file format
and the event-based format used by pyfarms.

NAADSM output looks something like this:
node 0 run 5620
1 0 0 0
node 0 run 5620
3 0 0 0
node 0 run 5620
3 0 1 0
node 0 run 5620
3 0 3 0
"""
import logging
import collections
import numpy as np
import h5py

logger=logging.getLogger("pyfarms.format")

# The Numpy data type for event data.
g_event_dtype=[
        ("event", "i4"), ("who", "i4"), ("whom", "i4"), ("when", ">f4")]
g_naadsm_transitions={(0,1) : 0, (1,2) : 1, (2,3) : 2, (3,4) : 3,
        (4,0) : 4 }

class TransitionGraph(object):
    """
    This is a graph of which initial states connect to
    which final states, and each directed edge is associated
    with a transition. This solves the problem that
    there may be several transitions per time step, so it tells
    you the list of transitions that are associated with
    a state change.
    """
    def __init__(self, dictionary_form):
        """
        The dictionary form looks like:
        {(0,1) : 0, (1,3) : 1, (3,4) : 3,
        (4,0) : 4, (0,3) : 5, (0,4) : 6, (1,4) : 8}
        """
        self._compiled=False
        self.directed=collections.defaultdict(list) # map from initial to final
        self.transition=dict() # map from initial and final to transitions.
        self.source_states=dict() # map from state to all previous states.
        for k, v in dictionary_form.items():
            self.add(k[0], k[1], v)
        self._compile()

    def add(self, initial_state, final_state, transition_id):
        self.directed[initial_state].append(final_state)
        self.transition[(initial_state, final_state)]=[transition_id]

    def transitions(self, initial_state, final_state):
        """
        A pair of states can indicate several intermediate transitions
        during a single discrete time step.
        """
        if not self._compiled:
            self._compile()

        return self.transition[(initial_state, final_state)]

    def possible_previous_states(self, final_state):
        return self.source_states[final_state]

    def maximal_state(self, state_set):
        greatest=next(iter(state_set))
        for s in state_set:
            if (greatest, s) in self.transition:
                greatest=s
        return s

    def _compile(self):
        """
        This takes a graph with edges pointing to single transitions
        and adds an edge from among all pairs of reachable states,
        where the transitions are a list of transitions to get
        from one to the other.
        """
        self.__branch(0, [0])
        self.source_states[0]=[0]
        self.__previous(0, [0])
        self._compiled=True

    def __branch(self, initial_state, stack):
        if initial_state in self.directed:
            for f in self.directed[initial_state]:
                if f in stack:
                    continue
                this_transition=self.transition[(initial_state, f)]
                for s in stack[:-1]:
                    prev_transitions=self.transition[(s, initial_state)]
                    self.transition[(s, f)]=prev_transitions+this_transition
                self.__branch(f, stack+[f])
        else:
            return

    def __previous(self, initial_state, stack):
        for f in self.directed[initial_state]:
            if f not in stack:
                substack=stack[:]+[f]
                self.source_states[f]=substack
                self.__previous(f, substack)
            else:
                pass # Don't continue search


def events_from_states(state_array, graph, initial):
    """
    The initial argument is a list of states at time 0. The first
    output is at day 1.
    """
    events=list()
    previous=initial
    for i in range(0, len(state_array)):
        for j in np.where(state_array[i]!=previous)[0]:
            transitions=graph.transitions(previous[j], state_array[i][j])
            for event in transitions:
                day=i
                who=j
                whom=j
                events.append((event, whom, who, day))
        previous=state_array[i]
    logger.debug(events)
    return np.array(events, dtype=g_event_dtype)



def naadsm_stream_flow(instream):
    """
    Filename is the name of the text file listing states at each time.
    Outfile is the hdf5 file.
    Initial is the initial set of states at time 0.
    transition_graph is a graph of which initial states can lead
    to which final states. Each state pair is associated with a transition.
    """
    vals=list()
    run=-1
    for line in instream:
        while line is not "":
            if line.startswith("node"):
                x, n, x, r=line.strip().split()
                n=int(n)
                r=int(r)

                if r!=run:
                    if len(vals)>0:
                        yield np.vstack(vals)
                    vals=list()
                    run=r

                line=instream.readline()
                states=[int(y) for y in line.strip().split()]
                vals.append(np.array(states))
            line=instream.readline()
    if len(vals)>0:
        yield np.vstack(vals)


def guess_initial(instream, transition_graph):
    unit_cnt=None
    possible_states=list()
    for state_array in naadsm_stream_flow(instream):
        if unit_cnt is None:
            unit_cnt=state_array.shape[1]
            for j in range(unit_cnt):
                ps=transition_graph.possible_previous_states(state_array[0][j])
                possible_states.append(set(ps))
            logger.debug("possible_states {0}".format(possible_states))
        else:
            for j in range(unit_cnt):
                possible_states[j].intersection_update(
                    transition_graph.possible_previous_states(state_array[0][j]))
    logger.debug("possible_states {0}".format(possible_states))
    maximals=np.zeros(unit_cnt, dtype=np.int)
    for base_idx in range(unit_cnt):
        maximals[base_idx]=transition_graph.maximal_state(
            possible_states[base_idx])
    return maximals


def naadsm_stream_flow_events(instream, initial, transition_graph):
    """
    Filename is the name of the text file listing states at each time.
    Outfile is the hdf5 file.
    Initial is the initial set of states at time 0.
    transition_graph is a graph of which initial states can lead
    to which final states. Each state pair is associated with a transition.
    """
    for state_array in naadsm_stream_flow(instream):
        events=events_from_states(state_array, transition_graph, initial)
        yield events


def naadsm_file_flow(filename, initial_state):
    """
    This loops through a NAADSM state output file, returning
    a set of events for each run.
    """
    graph=TransitionGraph(g_naadsm_transitions)
    with open(filename, "r") as f:
        for event_set in naadsm_stream_flow_events(f, initial_state, graph):
            yield event_set


def h5_datasets(open_file):
    """
    Returns the name of every trajectory in an HDF5 file.
    """
    trajectories=open_file['/trajectory']
    names=list()
    for trajectory_name in trajectories:
        if trajectory_name.startswith("dset"):
            names.append(trajectory_name)
    return names


def h5_file_flow(data_file):
    """
    Loops through all runs in an HDF5 file.
    """
    open_file=h5py.File(data_file, "r")
    for trajectory_name in h5_datasets(open_file):
        dset=open_file["/trajectory/{0}".format(trajectory_name)]

        as_events=np.zeros(dset["Event"].shape[0], dtype=g_event_dtype)
        as_events["event"]=dset["Event"]
        as_events["who"]=dset["Who"]
        as_events["whom"]=dset["Whom"]
        as_events["when"]=dset["When"]
        yield ret


def next_dset(openh5):
    """
    Finds the next available dataset name in an HDF5 file.
    """
    maxnum=-1
    for name in openh5["/trajectory"]:
        if name.startswith("dset"):
            maxnum=max(maxnum, int(name[4:]))
    return maxnum+1


def save_h5(openh5, events, dset_idx):
    name="/trajectory/dset{0}".format(dset_idx)
    logger.debug("Writing dataset {0}".format(name))
    group=openh5.create_group(name)
    event_cnt=events.shape[0]
    event=group.create_dataset("Event", (event_cnt,), dtype="i")
    whom=group.create_dataset("Who", (event_cnt,), dtype="i")
    who=group.create_dataset("Whom", (event_cnt,), dtype="i")
    when=group.create_dataset("When", (event_cnt,), dtype=np.float64)
    event[eidx]=events["event"]
    whom[eidx]=events["whom"]
    who[eidx]=events["who"]
    when[eidx]=events["when"]



def naadsm_stream_to_hdf5_stream(in_file_stream, out_hdf_file, initial_state):
    """
    Given a NAADSM file, convert it to an HDF5 file with events.
    """
    dset_idx=next_dset(hdf)
    for events in naadsm_flow(in_file_stream, initial_state):
        save_h5(out_hdf_file, events, dset_idx)
        dset_idx+=1


def naadsm_file_to_hdf5_file(in_file_name, out_file_name, initial_state):
    """
    Given a NAADSM file, convert it to an HDF5 file with events.
    """
    in_file=open(in_file_name, "r")
    hdf=h5py.File(out_file_name, "w")
    hdf.create_group("/trajectory")
    naadsm_stream_to_hdf5_stream(in_file, hdf, initial_state)

