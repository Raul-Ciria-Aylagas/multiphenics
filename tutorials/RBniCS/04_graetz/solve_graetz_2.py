# Copyright (C) 2015-2017 by the RBniCS authors
# Copyright (C) 2016-2017 by the block_ext authors
#
# This file is part of the RBniCS interface to block_ext.
#
# RBniCS and block_ext are free software: you can redistribute them and/or modify
# them under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS and block_ext are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS and block_ext. If not, see <http://www.gnu.org/licenses/>.
#

from dolfin import *
from block_ext import *
from RBniCS import *

#~~~~~~~~~~~~~~~~~~~~~~~~~     EXAMPLE 4: GRAETZ CLASS     ~~~~~~~~~~~~~~~~~~~~~~~~~#
@SCM()
@ShapeParametrization(
    ("x[0]", "x[1]"), # subdomain 1
    ("mu[0]*(x[0] - 1) + 1", "x[1]"), # subdomain 2
)
class Graetz(EllipticCoerciveProblem):
    
    ###########################     CONSTRUCTORS     ########################### 
    ## @defgroup Constructors Methods related to the construction of the reduced order model object
    #  @{
    
    ## Default initialization of members
    def __init__(self, block_V, **kwargs):
        # Call the standard initialization
        EllipticCoerciveProblem.__init__(self, block_V, **kwargs)
        # ... and also store FEniCS data structures for assembly
        assert "subdomains" in kwargs
        assert "boundaries" in kwargs
        self.subdomains, self.boundaries = kwargs["subdomains"], kwargs["boundaries"]
        block_u = BlockTrialFunction(block_V)
        block_v = BlockTestFunction(block_V)
        (self.u, ) = block_split(block_u)
        (self.v, ) = block_split(block_v)
        self.dx = Measure("dx")(subdomain_data=subdomains)
        self.ds = Measure("ds")(subdomain_data=boundaries)
        # Store the velocity expression
        self.vel = Expression("x[1]*(1-x[1])", element=self.V.sub(0).ufl_element())
                
    #  @}
    ########################### end - CONSTRUCTORS - end ########################### 
        
    ###########################     PROBLEM SPECIFIC     ########################### 
    ## @defgroup ProblemSpecific Problem specific methods
    #  @{
    
    ## Return theta multiplicative terms of the affine expansion of the problem.
    def compute_theta(self, term):
        mu1 = self.mu[0]
        mu2 = self.mu[1]
        mu3 = self.mu[2]
        mu4 = self.mu[3]
        if term == "a":
            theta_a0 = mu2
            theta_a1 = mu2/mu1
            theta_a2 = mu1*mu2
            theta_a3 = 1.0
            return (theta_a0, theta_a1, theta_a2, theta_a3)
        elif term == "f":
            theta_f0 = 1.0
            return (theta_f0,)
        elif term == "dirichlet_bc":
            theta_bc0 = mu3
            theta_bc1 = mu4
            return (theta_bc0, theta_bc1)
        elif term == "s":
            theta_s0 = 1.0
            return (theta_s0,)
        else:
            raise ValueError("Invalid term for compute_theta().")
                    
    ## Return forms resulting from the discretization of the affine expansion of the problem operators.
    def assemble_operator(self, term):
        v = self.v
        dx = self.dx
        if term == "a":
            u = self.u
            vel = self.vel
            a0 = [[inner(grad(u),grad(v))*dx(1)]]
            a1 = [[u.dx(0)*v.dx(0)*dx(2)]]
            a2 = [[u.dx(1)*v.dx(1)*dx(2)]]
            a3 = [[vel*u.dx(0)*v*dx(1) + vel*u.dx(0)*v*dx(2)]]
            return (a0, a1, a2, a3)
        elif term == "f":
            f0 = [Constant(0.0)*v*dx]
            return (f0,)
        elif term == "s":
            ds = self.ds
            s0 = [v*ds(4)]
            return (s0,)
        elif term == "dirichlet_bc":
            bc0 = BlockDirichletBC([[DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 1),
                                     DirichletBC(self.V.sub(0), Constant(1.0), self.boundaries, 2),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 3),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 5),
                                     DirichletBC(self.V.sub(0), Constant(1.0), self.boundaries, 6),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 7),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 8)]])
            bc1 = BlockDirichletBC([[DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 1),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 2),
                                     DirichletBC(self.V.sub(0), Constant(1.0), self.boundaries, 3),
                                     DirichletBC(self.V.sub(0), Constant(1.0), self.boundaries, 5),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 6),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 7),
                                     DirichletBC(self.V.sub(0), Constant(0.0), self.boundaries, 8)]])
            return (bc0, bc1)
        elif term == "inner_product":
            u = self.u
            x0 = [[inner(grad(u),grad(v))*dx]]
            return (x0,)
        else:
            raise ValueError("Invalid term for assemble_operator().")
        
    #  @}
    ########################### end - PROBLEM SPECIFIC - end ########################### 
    
#~~~~~~~~~~~~~~~~~~~~~~~~~     EXAMPLE 4: MAIN PROGRAM     ~~~~~~~~~~~~~~~~~~~~~~~~~# 

# 1. Read the mesh for this problem
mesh = Mesh("data/graetz.xml")
subdomains = MeshFunction("size_t", mesh, "data/graetz_physical_region.xml")
boundaries = MeshFunction("size_t", mesh, "data/graetz_facet_region.xml")

# 2. Create Finite Element space (Lagrange P1)
V = FunctionSpace(mesh, "Lagrange", 1)
block_V = BlockFunctionSpace([V])

# 3. Allocate an object of the Graetz class
graetz_problem = Graetz(block_V, subdomains=subdomains, boundaries=boundaries)
mu_range = [(0.01, 10.0), (0.01, 10.0), (0.5, 1.5), (0.5, 1.5)]
graetz_problem.set_mu_range(mu_range)

# 4. Prepare reduction with a reduced basis method
reduced_basis_method = ReducedBasis(graetz_problem)
reduced_basis_method.set_Nmax(20, dual=20, SCM=15)

# 5. Perform the offline phase
first_mu = (1.0, 1.0, 1.0, 1.0)
graetz_problem.set_mu(first_mu)
reduced_basis_method.initialize_training_set(500, dual=500, SCM=110)
reduced_graetz_problem = reduced_basis_method.offline()

# 6. Perform an online solve
online_mu = (10.0, 0.01, 1.0, 1.0)
reduced_graetz_problem.set_mu(online_mu)
reduced_graetz_problem.solve()
reduced_graetz_problem.export_solution("Graetz", "online_solution")

# 7. Perform an error analysis
reduced_basis_method.initialize_testing_set(100, dual=100, SCM=100)
reduced_basis_method.error_analysis()

# 8. Perform a speedup analysis
reduced_basis_method.speedup_analysis()

# 9. Define a new class corresponding to the exact version of Graetz,
#    for which SCM is replaced by ExactCoercivityConstant
ExactGraetz = ExactProblem(Graetz)

# 10. Allocate an object of the ExactGraetz class
exact_graetz_problem = ExactGraetz(V, subdomains=subdomains, boundaries=boundaries)
exact_graetz_problem.set_mu_range(mu_range)

# 11. Perform an error analysis with respect to the exact problem
reduced_basis_method.error_analysis(with_respect_to=exact_graetz_problem)

# 12. Perform a speedup analysis with respect to the exact problem
reduced_basis_method.speedup_analysis(with_respect_to=exact_graetz_problem)
