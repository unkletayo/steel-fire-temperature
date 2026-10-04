"""Sanity checks. Run with: python test_steel_fire.py"""

import numpy as np

from steel_fire import (
    iso834_gas_temp,
    steel_specific_heat,
    steel_temperature,
    time_to_reach,
)


def test_iso834_known_values():
    # Hand check: 20 + 345*log10(8*30+1) = 841.9 C at 30 min
    assert abs(iso834_gas_temp(30.0) - 842.0) < 1.0
    assert abs(iso834_gas_temp(60.0) - 945.0) < 1.0


def test_specific_heat_at_20c():
    # EN 1993-1-2 gives about 439.8 J/kgK at 20 C
    assert abs(steel_specific_heat(20.0) - 439.8) < 1.0


def test_steel_never_hotter_than_gas():
    times, gas, steel = steel_temperature(300.0)
    assert np.all(steel <= gas + 1e-6)


def test_slender_sections_heat_faster():
    t_heavy = time_to_reach(*steel_temperature(50.0)[::2])
    t_slender = time_to_reach(*steel_temperature(300.0)[::2])
    assert t_slender < t_heavy


def test_smaller_time_step_gives_same_answer():
    _, _, coarse = steel_temperature(200.0, dt=5.0)
    _, _, fine = steel_temperature(200.0, dt=1.0)
    assert abs(coarse[-1] - fine[-1]) < 5.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("pass", name)
