# -*- coding: utf-8 -*-
#
# Copyright 2015 Federico Ficarelli
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from automaton import *


@pytest.fixture
def traffic_light():
    class TrafficLight(Automaton):
        __default_initial_state__ = "red"
        __default_accepting_states__ = ("red", "green")
        go = Event("red", "green")
        slowdown = Event("green", "yellow")
        stop = Event("yellow", "red")

    return TrafficLight


def test_definition():
    class Simple(Automaton):
        __default_initial_state__ = "state_a"
        event1 = Event("state_a", "state_b")
        event2 = Event("state_b", "state_c")

    # Class properties
    assert Simple.get_default_initial_state() == "state_a"
    assert "event1" in Simple.events()
    assert "event2" in Simple.events()
    assert "event3" not in Simple.events()
    assert "state_a" in Simple.states()
    assert "state_b" in Simple.states()
    assert "state_c" in Simple.states()
    assert "unknown" not in Simple.states()
    # Instantiation
    simple_obj = Simple()
    # Class properties through instance
    assert simple_obj.get_default_initial_state() == "state_a"
    assert "event1" in simple_obj.events()
    assert "event2" in simple_obj.events()
    assert "event3" not in simple_obj.events()


def test_initial_state():
    # Invalid initial state
    with pytest.raises(DefinitionError):
        class Wrong(Automaton):
            __default_initial_state__ = "unknown"
            event1 = Event("state_a", "state_b")
            event2 = Event("state_b", "state_c")
    # Initial state not defined
    class NoInit(Automaton):
        event1 = Event("state_a", "state_b")
        event2 = Event("state_b", "state_c")

    assert NoInit.get_default_initial_state() is None
    with pytest.raises(DefinitionError):
        noinit_obj = NoInit()
    with pytest.raises(DefinitionError):
        noinit_obj = NoInit(initial_state="unknown")
    for state in "state_a", "state_b", "state_c":
        noinit_obj = NoInit(initial_state=state)
        assert noinit_obj.get_default_initial_state() is None
        assert noinit_obj.state == state


def test_unconnected_naive():
    # The graph representing the FSM must be connected.
    with pytest.raises(DefinitionError):
        class Unconnected(Automaton):
            cluster1 = Event("state_a", "state_b")
            cluster2 = Event("state_c", "state_d")


def test_empty():
    class Empty(Automaton):
        pass


def test_unconnected():
    # The graph representing the FSM must be connected.
    with pytest.raises(DefinitionError):
        class Unconnected(Automaton):
            cluster1_1 = Event("state_a", "state_b")
            cluster1_2 = Event("state_b", "state_c")
            cluster1_3 = Event("state_c", "state_d")
            #
            cluster2_1 = Event("state_e", "state_f")
            cluster2_2 = Event("state_f", "state_g")
            cluster2_3 = Event("state_g", "state_h")
            #
            cluster3_1 = Event("state_1", "state_2")
            cluster3_2 = Event("state_2", "state_3")
            cluster3_3 = Event("state_3", "state_4")
            cluster3_4 = Event("state_4", "state_5")
            cluster3_5 = Event("state_5", "state_6")
            cluster3_6 = Event("state_6", "state_7")


def test_connected_clusters():
    # Connect the clusters:
    class Unconnected(Automaton):
        cluster1_1 = Event("state_a", "state_b")
        cluster1_2 = Event("state_b", "state_c")
        cluster1_3 = Event("state_c", "state_d")
        #
        cluster2_1 = Event("state_e", "state_f")
        cluster2_2 = Event("state_f", "state_g")
        cluster2_3 = Event("state_g", "state_h")
        #
        cluster3_1 = Event("state_1", "state_2")
        cluster3_2 = Event("state_2", "state_3")
        cluster3_3 = Event("state_3", "state_4")
        cluster3_4 = Event("state_4", "state_5")
        cluster3_5 = Event("state_5", "state_6")
        cluster3_6 = Event("state_6", "state_7")
        #
        conn_1_2 = Event("state_d", "state_e")
        conn_2_3 = Event("state_h", "state_1")


def test_multiple_arcs():
    # It's ok to have multiple directed arcs between two states,
    # it seems like an elegant (but somehow not efficient) way
    # to support multiple events per transition.
    class Multiple(Automaton):
        event1 = Event("state_a", "state_b")
        event2 = Event("state_a", "state_b")
        event3 = Event("state_a", "state_b")

    assert "event1" in Multiple.events()
    assert "event2" in Multiple.events()
    assert "event3" in Multiple.events()


def test_auto_arc():
    class Auto(Automaton):
        loop = Event("state_a", "state_a")

    assert "loop" in Auto.events()
    auto_obj = Auto(initial_state="state_a")
    assert auto_obj.state == "state_a"
    auto_obj.event("loop")
    assert auto_obj.state == "state_a"


def test_transition(traffic_light):
    crossroads = traffic_light()
    # Initial state
    assert crossroads.state == "red"
    # Transitions
    crossroads.event("go")
    assert crossroads.state == "green"
    crossroads.event("slowdown")
    assert crossroads.state == "yellow"
    crossroads.event("stop")
    assert crossroads.state == "red"
    crossroads.event("go")
    assert crossroads.state == "green"
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.event("stop")
    assert crossroads.state == "green"
    with pytest.raises(InvalidTransitionError):
        crossroads.event("unknown")
    assert crossroads.state == "green"


def test_event_binding(traffic_light):
    assert traffic_light.go.name == "go"
    assert traffic_light.slowdown.name == "slowdown"
    assert traffic_light.stop.name == "stop"


def test_event_descriptor(traffic_light):
    crossroads = traffic_light()
    with pytest.raises(AttributeError):
        crossroads.go = None


def test_event_methods(traffic_light):
    crossroads = traffic_light()
    # Initial state
    assert crossroads.state == "red"
    # Transitions
    crossroads.go()
    assert crossroads.state == "green"
    crossroads.slowdown()
    assert crossroads.state == "yellow"
    crossroads.stop()
    assert crossroads.state == "red"
    crossroads.go()
    assert crossroads.state == "green"
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == "green"


def test_invalid_default_accepting_states():
    with pytest.raises(DefinitionError):
        class Wrong(Automaton):
            __default_accepting_states__ = ("event1", "unknown")
            event1 = Event("state_a", "state_b")


def test_default_accepting_states(traffic_light):
    crossroads = traffic_light()
    # Initial state
    assert crossroads.state == "red"
    assert crossroads.is_accepted
    # Transitions
    crossroads.go()
    assert crossroads.state == "green"
    assert crossroads.is_accepted
    crossroads.slowdown()
    assert crossroads.state == "yellow"
    assert not crossroads.is_accepted
    crossroads.stop()
    assert crossroads.state == "red"
    assert crossroads.is_accepted
    crossroads.go()
    assert crossroads.state == "green"
    assert crossroads.is_accepted
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == "green"
    assert crossroads.is_accepted


def test_custom_accepting_states(traffic_light):
    crossroads = traffic_light(accepting_states=("yellow", ))
    # Initial state
    assert crossroads.state == "red"
    assert not crossroads.is_accepted
    # Transitions
    crossroads.go()
    assert crossroads.state == "green"
    assert not crossroads.is_accepted
    crossroads.slowdown()
    assert crossroads.state == "yellow"
    assert crossroads.is_accepted
    crossroads.stop()
    assert crossroads.state == "red"
    assert not crossroads.is_accepted
    crossroads.go()
    assert crossroads.state == "green"
    assert not crossroads.is_accepted
    # Invalid transitions
    with pytest.raises(InvalidTransitionError):
        crossroads.stop()
    assert crossroads.state == "green"
    assert not crossroads.is_accepted


def test_invalid_custom_accepting_states(traffic_light):
    with pytest.raises(DefinitionError):
        crossroads = traffic_light(accepting_states=("yellow", "unknown"))


def test_sink_state():
    sources = ("state_a", "state_b", "state_c", "state_d")

    class Sink(Automaton):
        event1 = Event(sources, "sink")

    for initial in sources:
        auto = Sink(initial_state=initial)
        assert auto.state == initial
        auto.event1()
        assert auto.state == "sink"
        with pytest.raises(InvalidTransitionError):
            auto.event1()


def test_sink_state_complex():
    class Sink(Automaton):
        event1 = Event("state_a", "state_b")
        event2 = Event(("state_a", "state_b", "state_c", "state_d"), "sink1")
        event3 = Event(("state_a", "state_b", "state_c", "state_d", "sink1"), "sink2")

    auto = Sink(initial_state="state_a")
    auto.event1()
    assert auto.state == "state_b"
    auto.event2()
    assert auto.state == "sink1"
    auto.event3()
    assert auto.state == "sink2"


def test_sink_state_loop():
    class Sink(Automaton):
        event1 = Event("state_a", "state_b")
        event2 = Event(("state_a", "state_b", "state_c", "state_d"), "sink1")
        event3 = Event(("state_a", "state_b", "state_c", "state_d", "sink1"), "sink2")
        event4 = Event("sink2", "state_a")

    auto = Sink(initial_state="state_a")
    auto.event1()
    assert auto.state == "state_b"
    auto.event2()
    assert auto.state == "sink1"
    auto.event3()
    assert auto.state == "sink2"
    auto.event4()
    assert auto.state == "state_a"
    auto.event1()
    assert auto.state == "state_b"
    auto.event2()
    assert auto.state == "sink1"
    auto.event3()
    assert auto.state == "sink2"
    auto.event4()
    assert auto.state == "state_a"
