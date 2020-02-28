
def ambient_turbulence_wake_erosion_rate(turbulence):
    
    # Equate 19 (from p440)
    # An Experimental analysis of wind turbine wakes, P.E.J. Vermeulen, Wind Energy Systems August 26-29, 1980.

    if turbulence < 0.02:
        return 5.0 * turbulence
    else:
        return 2.5 * turbulence + 0.05
