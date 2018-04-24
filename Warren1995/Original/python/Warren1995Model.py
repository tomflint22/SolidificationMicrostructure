
# coding: utf-8

# In[3]:
import numpy as np
import matplotlib
import os
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ipywidgets import interact, fixed


# In[4]:

def __p(phi):
    return phi*phi*phi*(10-15*phi+6*phi*phi)

def __g(phi):
    return (phi*phi*(1-phi)*(1-phi))

def __gprime(phi):
    return (4*phi*phi*phi - 6*phi*phi +2*phi)

_p = np.vectorize(__p)
_g = np.vectorize(__g) 
_gprime = np.vectorize(__gprime)

def gradx(phi, dx):
    phim = np.roll(phi, -1, 0)
    phip = np.roll(phi, 1, 0)
    return (phip-phim)/(2*dx)

def grady(phi, dx):
    phim = np.roll(phi, -1, 1)
    phip = np.roll(phi, 1, 1)
    return (phip-phim)/(2*dx)

def gradxx(phi, dx):
    phim = np.roll(phi, -1, 0)
    phip = np.roll(phi, 1, 0)
    return (phip+phim-2*phi)/(dx*dx)

def gradyy(phi, dx):
    phim = np.roll(phi, -1, 1)
    phip = np.roll(phi, 1, 1)
    return (phip+phim-2*phi)/(dx*dx)


# In[5]:

#material parameters
T_mA = 1728 #melting point of nickel
T_mB = 1358 #melting point of copper
L_A = 2350. #latent heat of nickel, J/cm^3
L_B = 1728. #latent heat of copper, J/cm^3
s_A = 3.7e-5 #surface energy of nickel, J/cm^2
s_B = 2.9e-5 #surface energy of copper, J/cm^2
D_L = 1e-5 #diffusion in liquid, cm^2/s
D_S = 1e-9 #diffusion in solid, cm^2/s
B_A = 0.33 #linear kinetic coefficient of nickel, cm/K/s
B_B = 0.39 #linear kinetic coefficient of copper, cm/K/s
v_m = 7.42 #molar volume, cm^3/mol
R = 8.314 #gas constant, J/mol*K
y_e = 0.06 #anisotropy


# In[1]:

np.set_printoptions(threshold=np.inf)
T = 1574
res = 300
dx = 4.6e-6 #spacial division, cm
dt = dx*dx/5./D_L
print(dt)
d = dx/0.94 #interfacial thickness
ebar = np.sqrt(6*np.sqrt(2)*s_A*d/T_mA) #baseline energy

W_A = 3*s_A/(np.sqrt(2)*T_mA*d)
W_B = 3*s_B/(np.sqrt(2)*T_mB*d)
M_A = T_mA*T_mA*B_A/(6*np.sqrt(2)*L_A*d)
M_B = T_mB*T_mB*B_B/(6*np.sqrt(2)*L_B*d)
ebar = np.sqrt(6*np.sqrt(2)*s_A*d/T_mA)

c = np.zeros((res,res))
phi = np.zeros((res, res))
c += 0.40831
phi += 1
diamondParam = 15
for i in range(diamondParam):
    phi[(int)(res/2-i):(int)(res/2+i), ((int)(res/2-(diamondParam-i))):(int)(res/2+(diamondParam-i))] = 0

if not os.path.isdir('data'):
    os.makedirs('data')
	
# In[52]:

for i in range(401):
    print(i)
    g = _g(phi)
    p = _p(phi)
    gprime = _gprime(phi)
    H_A = W_A*gprime + 30*L_A*(1/T-1/T_mA)*g
    H_B = W_B*gprime + 30*L_B*(1/T-1/T_mB)*g
    phixx = gradxx(phi, dx)
    phiyy = gradyy(phi, dx)
    lphi = phixx+phiyy
    phix = gradx(phi, dx)
    phiy = grady(phi, dx)
    phixy = grady(phix, dx)
    
    #change in c
    D_C = D_S+p*(D_L-D_S)
    temp = D_C*v_m*c*(1-c)*(H_B-H_A)/R
    deltac = D_C*(gradxx(c, dx)+gradyy(c, dx))+(gradx(D_C, dx)*gradx(c, dx)+grady(D_C, dx)*grady(c, dx))+temp*(lphi)+(gradx(temp, dx)*phix+grady(temp, dx)*phiy)
    
    #change in phi
    theta = np.arctan2(phiy, phix)
    eta = 1+y_e*np.cos(4*theta)
    etap = -4*y_e*np.sin(4*theta)
    etapp = -16*(eta-1)
    c2 = np.cos(2*theta)
    s2 = np.sin(2*theta)
    M_phi = (1-c)*M_A + c*M_B
    deltaphi = M_phi*((ebar*ebar*eta*eta*lphi-(1-c)*H_A-c*H_B)+ebar*ebar*eta*etap*(s2*(phiyy-phixx)+2*c2*phixy)+0.5*ebar*ebar*(etap*etap+eta*etapp)*(-2*s2*phixy+lphi+c2*(phiyy-phixx)))
    randArray = 2*np.random.rand(res, res)-1
    alpha = 0.3
    deltaphi += M_phi*alpha*randArray*(16*g)*((1-c)*H_A+c*H_B)
    
    #apply changes
    ctemp = c.copy()
    c += deltac*dt
    phi += deltaphi*dt
    
    if(i%50 == 0):
        plt.imshow(phi)
        plt.savefig('data/phi'+str(i)+'.png')
        plt.imshow(c)
        plt.savefig('data/c'+str(i)+'.png')
        f = open('data/rawData_'+str(i)+'.txt','w')
        f.write(np.array_str(c))
        f.write('\n')
        f.write(np.array_str(phi))
        f.close()


# In[2]:

plt.imshow(phi)


# In[ ]:


