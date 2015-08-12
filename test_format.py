import numpy as np
import format

def test_graph():
    g=format.TransitionGraph(format.g_naadsm_transitions)
    assert(g.transitions(0, 1)==[0])
    assert(g.transitions(0, 2)==[0, 1])
    assert(g.transitions(0, 3)==[0, 1, 2])
    assert(g.transitions(4, 0)==[4])
    assert(g.transitions(1, 3)==[1, 2])
    assert(g.possible_previous_states(0)==[0])
    assert(g.possible_previous_states(1)==[0, 1])
    assert(g.possible_previous_states(2)==[0, 1, 2])
    assert(g.possible_previous_states(3)==[0, 1, 2, 3])
    assert(g.possible_previous_states(4)==[0, 1, 2, 3, 4])

def test_file_flow():
    infile=("/work/ajd27/naadsmdata/"+
        "HPAI_Kershaw_Parameters_no_controls_airborne_only_p5_runs1000_1.out")
    g=format.TransitionGraph(format.g_naadsm_transitions)
    #initial=format.guess_initial(open(infile, "r"), g)
    initial=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    event_cnt=0
    for events in format.naadsm_file_flow(infile, initial):
        event_cnt+=1
    print(event_cnt)


def test_initial():
    infile=("/work/ajd27/naadsmdata/"+
        "HPAI_Kershaw_Parameters_no_controls_airborne_only_p5_runs1000_1.out")
    g=format.TransitionGraph(format.g_naadsm_transitions)
    initial=format.guess_initial(open(infile, "r"), g)
    print(initial)

