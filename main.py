import numpy as np
import scipy.sparse.linalg as la
import matplotlib.pyplot as plt
from timeit import default_timer as timer
# Own packages
from wavecontrol import mesh
from wavecontrol.hct import assembly as hct_assembly
from wavecontrol.hct import master_functions as mf
from wavecontrol import wave_time_marching as wtm
from wavecontrol import plots

# Evaluation of master functions at gaussian points
master_eval = mf.HctMasterFunctions([True, True, True, True])

# Data for the mesh
T = 2
N = 20
K = int(2.2 * N)
del_x = 1 / N
del_t = T / K
# Creation of the mesh
rectagle_mesh = mesh.Mesh(N, K, T)

print("Uniform mesh dimension: [N,K]=[" + str(N) + "," + str(K) + "]")
print("T= ", T)
print("DelX= ", del_x)
print("DelT= ", del_t)

# Ellipticity parameter, related to the weight that we put in the functional
# that we want to solve

# Stiffness and Load Matrices assembly
A = hct_assembly.build_stiffness(rectagle_mesh, master_eval)
initial_pos_matrix, initial_vel_matrix = hct_assembly.build_initial_conditions(rectagle_mesh, master_eval)

# Interpolation of the L^2 initial data


def f(x): return np.sin(2 * np.pi * x)

# g = lambda x: np.sin(3*np.pi*x)


def g(x): return 0


P = hct_assembly.interpolation_P1(f, N)
Q = hct_assembly.interpolation_P1(g, N)

xx = np.linspace(0, 1, P.shape[0])
plt.plot(xx, P)
plt.show()
plt.close()

# Set the Load Vector from the Load Matrix and the interpolated initial data
F1 = -initial_pos_matrix.dot(P)
F2 = initial_vel_matrix.dot(Q)

# Homogeneous Dirichlet boundary conditions
F1[3 * rectagle_mesh.right_boundary_idx] = 0
F1[3 * rectagle_mesh.left_boundary_idx] = 0
F1[3 * rectagle_mesh.right_boundary_idx + 2] = 0
F1[3 * rectagle_mesh.left_boundary_idx + 2] = 0
F2[3 * rectagle_mesh.right_boundary_idx] = 0
F2[3 * rectagle_mesh.left_boundary_idx] = 0
F2[3 * rectagle_mesh.right_boundary_idx + 2] = 0
F2[3 * rectagle_mesh.left_boundary_idx + 2] = 0

# Linear Solver
start = timer()
U = la.spsolve(A, F1, use_umfpack=True)
end = timer()
print("Solved! (" + str(end - start) + "s.)")
print("MAX: ", np.amax(U))
print("MIN: ", np.amin(U))

# Store the vector solution in a (K+1)x(N+1)x3 array
u = wtm.to_grid(U, K, N)
# Store the gradient in x at the boundary x=1
gradient_at_boundary = u[:, N, 1]

# Sampling points
x = np.linspace(0, 1, N + 1)
t = np.linspace(0, T, K + 1)

# Plot control
plt.plot(t, gradient_at_boundary)
plt.show()
plt.close()

# Plot Initial data
plt.plot(x, u[0, :, 1:])
plt.show()
plt.close()

# Initial data for the a posteriori computation
y0 = f(x)
y1 = g(x)

L = 1
y = wtm.solve_explicit(y0, y1, gradient_at_boundary, None, L, T, N, K)
# Plot Final data
plt.plot(x, y[K, :])
plt.show()
plt.close()
# Plot space-time grid
plots.space_time(y, L, T, N, K)