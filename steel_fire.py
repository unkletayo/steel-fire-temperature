"""Temperature of unprotected steel in a standard fire (ISO 834).

Simplified method from Eurocode 3, EN 1993-1-2, section 4.2.5.1:
the steel section is treated as one lump at a single uniform temperature.
Each small time step, the gas heats the steel by convection and radiation,
and the steel's heat capacity decides how fast it warms up.

Teaching exercise, not for design. Simplifications are listed in the README.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Constants (EN 1993-1-2) -------------------------------------------------
STEEL_DENSITY = 7850.0          # kg/m^3
CONVECTION_COEFF = 25.0         # W/m^2K, standard fire
EMISSIVITY = 0.7                # resultant emissivity (surface 0.7 x flame 1.0)
STEFAN_BOLTZMANN = 5.67e-8      # W/m^2K^4
KELVIN = 273.0
CRITICAL_TEMP = 550.0           # deg C, commonly used critical temperature


def iso834_gas_temp(t_min):
    """Gas temperature (deg C) after t_min minutes of standard fire."""
    return 20.0 + 345.0 * np.log10(8.0 * t_min + 1.0)


def steel_specific_heat(theta):
    """Specific heat of carbon steel (J/kgK) at theta deg C.

    The bump near 735 deg C is a real phase change in the steel,
    and it slows heating there.
    """
    if theta < 600.0:
        return 425.0 + 0.773 * theta - 1.69e-3 * theta**2 + 2.22e-6 * theta**3
    if theta < 735.0:
        return 666.0 + 13002.0 / (738.0 - theta)
    if theta < 900.0:
        return 545.0 + 17820.0 / (theta - 731.0)
    return 650.0


def steel_temperature(section_factor, duration_min=60.0, dt=2.0):
    """Steel temperature history under ISO 834.

    section_factor: Am/V in 1/m. Heated surface area per unit volume.
                    Thin or slender sections are high; heavy sections low.
    duration_min:   how long to simulate, in minutes.
    dt:             time step in seconds. EN 1993-1-2 says keep it <= 5 s.

    Returns (times in minutes, gas temps, steel temps), all numpy arrays.
    """
    n_steps = int(duration_min * 60.0 / dt)
    times = np.arange(n_steps + 1) * dt / 60.0
    gas = iso834_gas_temp(times)
    steel = np.empty(n_steps + 1)
    steel[0] = 20.0

    for i in range(n_steps):
        theta_a = steel[i]
        theta_g = gas[i]

        convection = CONVECTION_COEFF * (theta_g - theta_a)
        radiation = EMISSIVITY * STEFAN_BOLTZMANN * (
            (theta_g + KELVIN) ** 4 - (theta_a + KELVIN) ** 4
        )
        net_heat_flux = convection + radiation          # W/m^2

        c_a = steel_specific_heat(theta_a)
        d_theta = section_factor / (c_a * STEEL_DENSITY) * net_heat_flux * dt
        steel[i + 1] = theta_a + d_theta

    return times, gas, steel


def time_to_reach(times, steel, target=CRITICAL_TEMP):
    """First time (minutes) the steel reaches target deg C, or None."""
    above = np.nonzero(steel >= target)[0]
    if above.size == 0:
        return None
    return times[above[0]]


def main():
    section_factors = [50, 100, 200, 300]  # 1/m, heavy to slender

    fig, ax = plt.subplots(figsize=(8, 5))
    times, gas, _ = steel_temperature(section_factors[0])
    ax.plot(times, gas, "k--", label="ISO 834 gas")

    print(f"Time for unprotected steel to reach {CRITICAL_TEMP:.0f} C:")
    for sf in section_factors:
        times, _, steel = steel_temperature(sf)
        t_crit = time_to_reach(times, steel)
        label = f"Am/V = {sf} 1/m"
        if t_crit is None:
            print(f"  Am/V = {sf:>3}: not reached in {times[-1]:.0f} min")
        else:
            print(f"  Am/V = {sf:>3}: {t_crit:5.1f} min")
        ax.plot(times, steel, label=label)

    ax.axhline(CRITICAL_TEMP, color="red", lw=0.8, ls=":")
    ax.text(1, CRITICAL_TEMP + 12, f"{CRITICAL_TEMP:.0f} C", color="red")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Temperature (deg C)")
    ax.set_title("Unprotected steel in a standard fire")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("steel_temperature.png", dpi=150)
    print("Saved steel_temperature.png")


if __name__ == "__main__":
    main()
