import numpy as np
from scipy.integrate import quad
from matplotlib.pyplot import figure, show

import general as ge
import coefficients as cf
import boundaries as bo



class merger_wave(object):
    """ Class for merging gravitational waves """
    
    def __init__(self, m1, m2):
        """ Initialization """
        
        self.m1, self.m2 = m1.kg, m2.kg                     # Masses in kg
        self.M = self.tot_m()                               # Total mass
        
        self.d1, self.d2 = m1.dist, m2.dist             # Masses in meters
        self.t1, self.t2 = m1.time, m2.time             # Masses in seconds
        
        self.etaV = self.eta()                          # eta
    
    
    def tot_m(self):
        return self.m1 + self.m2
    
    def eta(self):
        return self.m1 * self.m2 / np.power(self.M, 2)
    
    def omegaQNM(self):
        """ Determine parameter omega_QNM """
        return 1 - 0.63 * np.power(1 - cf.sfin(self.etaV), 0.3)
    
    def f_hat(self, t):
        """ Determine the function f^hat """
        
            # Coefficients
        etaV = self.etaV                                # eta
        kappa = cf.kappa(etaV)                          # Coefficient kappa
        b = cf.b(etaV)                                  # Coefficient b
        cCoef = cf.cCoef(etaV)                          # Coefficient c
        
            # Computing f^hat
        part1 = cCoef * np.power(1 + 1/kappa, 1 + kappa) / 2
        part2 = 1 + np.exp(-2 * t / b) / kappa
        
        return part1 * (1 - np.power(part2, -kappa))
    
    def omega(self, t):
        """ Find omega(t) """
        return self.omegaQNM() * (1 - self.f_hat(t))
    
    def phi_gIRS(self, tStart, tFin):
        """ Find the phase by integrating the function omega(t) """
        return quad(self.omega, tStart, tFin)[0]
    
    def A(self, t):
        """ Amplitude as function of time """
        
        A0 = 1 / (self.t1 + self.t2)                    # Amplitude
        alpha = cf.alpha(self.etaV)                     # alpha coefficient
        omegaT = self.omega(t)                          # omega(t)
        
        func = self.f_hat(t)                            # function f^hat
        difFunc = ge.diff_func(func, t)                  # df^hat/dt
        
        denomP = np.power(func, 2) - np.power(func, 4)      # Part of denom.
        part1 = np.abs(difFunc) / (1 + alpha * denomP[1:])  # Part of equation
        
        return A0 * np.sqrt(part1) / omegaT[1:]
    
    def hMerger(self, t):
        """ Waveform strain """
        
        t = t / (self.t1 + self.t2)
        tS, tF = t[0], t[-1]                            # Start & end times
        aT = self.A(t)                                  # Amplitude
        
        phiVals = []
        for ind in range(len(t)):
            phigIRS = self.phi_gIRS(t[0], t[ind])       # Phase
            phiVals.append(phigIRS)
        
        phiRes = np.asarray(phiVals[:-1])
        
            # e^(-ix) = cos(x) - i sin(x)
        realMerg = aT * np.cos(phiRes)                  # Real part
        imgMerg = -aT * np.sin(phiRes)                  # Imaginary part
        
        return t, realMerg, imgMerg


def main():

    M1 = bo.geom_units(20)
    M2 = bo.geom_units(20)
    
    timeRange = np.linspace(-0.05, 0.05, 1000)          # Units M_sun
    
    mergeWave = merger_wave(M1, M2)                     # Initializing wave
    unitLessTime, hP, hC = mergeWave.hMerger(timeRange) # Waves
    
    ampVals = mergeWave.A(unitLessTime)                 # Amplitude
    

if __name__ == "__main__":
    main()
