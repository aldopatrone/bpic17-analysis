# Self-implemented Petri-net simplicity metrics. §3.3 task 2.
# 
# Reference: Carmona, van Dongen, Solti, Weidlich,
# "Conformance Checking - Relating Processes and Models", Springer 2018.


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pm4py.objects.petri_net.obj import PetriNet


def size(net: "PetriNet") -> int:
    # Size = |P| + |T| + |F|
    return len(net.places) + len(net.transitions) + len(net.arcs)


def control_flow_complexity(net: "PetriNet") -> int:

    # Cardoso Control-Flow Complexity: sum over all splits of
    # XOR-split (place, >1 out-arcs),
    # AND-split (transition, >1 out-arcs).
    
    cfc = 0
    for place in net.places:
        out_degree = len(place.out_arcs)
        if out_degree > 1:
            cfc += out_degree  # XOR-split
    for transition in net.transitions:
        out_degree = len(transition.out_arcs)
        if out_degree > 1:
            cfc += 1  # AND-split
    return cfc
