import numpy as np
from mod_utils import print_stdout

class lattice:

    """
    lattice and reciprocal lattice vectors 
    """

    # -----------------------------------------------------------------------------------------

    def __init__(self,invars):
        """
        store lattice and reciprocal lattice vectors
        """
        self.lattice_vectors = invars.lattice_vectors
        self.r_lattice_vectors = np.zeros((3,3))

        message = (f'cell lengths from input: {self.lattice_vectors[0,0]} '
                   f'{self.lattice_vectors[1,1]} '
                   f'{self.lattice_vectors[2,2]} Angstrom')
        print_stdout(message,msg_type='NOTE')

        if not invars.recalculate_cell_lengths:
            message = 'using cell lengths from input\n'
            print_stdout(message,msg_type='NOTE')
        else:
            message = 'using cell lengths from hdf5 trajectory file'
            print_stdout(message,msg_type='NOTE')

        self._compute_reciprocal_lattice()

        message = (f'real space lattice (Angstrom):\n'
                f'  {self.lattice_vectors[0,0]:2.3f} {self.lattice_vectors[0,1]:2.3f}'
                f' {self.lattice_vectors[0,2]:2.3f}\n  {self.lattice_vectors[1,0]:2.3f}'
                f' {self.lattice_vectors[1,1]:2.3f} {self.lattice_vectors[1,2]:2.3f}\n'
                f'  {self.lattice_vectors[2,0]:2.3f} {self.lattice_vectors[2,1]:2.3f}'
                f' {self.lattice_vectors[2,2]:2.3f}\n')
        print_stdout(message,msg_type='NOTE')

        message = (f'reciprocal space lattice (1/Angstrom):\n'
                f'  {self.r_lattice_vectors[0,0]:2.3f} {self.r_lattice_vectors[0,1]:2.3f}'
                f' {self.r_lattice_vectors[0,2]:2.3f}\n  {self.r_lattice_vectors[1,0]:2.3f}'
                f' {self.r_lattice_vectors[1,1]:2.3f} {self.r_lattice_vectors[1,2]:2.3f}\n'
                f'  {self.r_lattice_vectors[2,0]:2.3f} {self.r_lattice_vectors[2,1]:2.3f}'
                f' {self.r_lattice_vectors[2,2]:2.3f}')
        print_stdout(message)

    # ------------------------------------------------------------------------------------------

    def recompute_lattice(self,invars):
        """
        recompute lattice vectors etc. from data read from traj file
        """
        self.lattice_vectors = invars.lattice_vectors
        self.r_lattice_vectors = np.zeros((3,3))
        self._compute_reciprocal_lattice()

    # =======================================================================================
    # ------------------------------ private methods ----------------------------------------
    # =======================================================================================

    def _compute_reciprocal_lattice(self):
        """
        compute reciprocal lattice vectors from real lattice
        """
        self.cell_vol = self.lattice_vectors[0,:].dot(np.cross(self.lattice_vectors[1,:],
            self.lattice_vectors[2,:]))
        self.r_lattice_vectors[0,:] = 2*np.pi*np.cross(self.lattice_vectors[1,:],
                self.lattice_vectors[2,:])/self.cell_vol
        self.r_lattice_vectors[1,:] = 2*np.pi*np.cross(self.lattice_vectors[2,:],
                self.lattice_vectors[0,:])/self.cell_vol
        self.r_lattice_vectors[2,:] = 2*np.pi*np.cross(self.lattice_vectors[0,:],
                self.lattice_vectors[1,:])/self.cell_vol













