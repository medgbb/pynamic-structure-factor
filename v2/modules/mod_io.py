import numpy as np
import os
import h5py
from mod_utils import print_stdout

class traj_file:

    """
    have to open traj_file on each rank seperately. python complained when i tried to pass open file
    with mpi communicator. 
    """

    # -----------------------------------------------------------------------------------------

    def __init__(self,invars):
        """
        open the hdf5 file
        """
        self.handle = h5py.File(invars.traj_file,'r')

    # -----------------------------------------------------------------------------------------

    def parse_trajectory(self,invars,sqw):

        if sqw.rank == 0:
            message = 'now reading positions'
            print_stdout(message,msg_type='NOTE')

        inds = [sqw.block_index*sqw.block_steps,(sqw.block_index+1)*sqw.block_steps]

        if invars.parse_lammps:
            sqw.box_lengths[0] = np.mean(self.handle['particles']['all']['box']['edges']['value']
                        [inds[0]:inds[1],0],axis=0)
            sqw.box_lengths[1] = np.mean(self.handle['particles']['all']['box']['edges']['value']
                        [inds[0]:inds[1],1],axis=0)
            sqw.box_lengths[2] = np.mean(self.handle['particles']['all']['box']['edges']['value']
                        [inds[0]:inds[1],2],axis=0)
            sqw.pos[:,:,:] = self.handle['particles']['all']['position']['value'][inds[0]:inds[1],:,:]
            sqw.atom_ids[:,:] = self.handle['particles']['all']['species']['value'][inds[0]:inds[1],:] 
        else:
            sqw.box_lengths[0] = np.mean(invars.traj_handle['box_bounds'][inds[0]:inds[1],1]-
                    invars.traj_handle['box_bounds'][inds[0]:inds[1],0])
            sqw.box_lengths[1] = np.mean(invars.traj_handle['box_bounds'][inds[0]:inds[1],3]-
                    invars.traj_handle['box_bounds'][inds[0]:inds[1],2])
            sqw.box_lengths[2] = np.mean(invars.traj_handle['box_bounds'][inds[0]:inds[1],5]-
                    invars.traj_handle['box_bounds'][inds[0]:inds[1],4])
            self.pos[:,:,:] = invars.traj_handle['pos_data'][inds[0]:inds[1],:,:]   # get the positins
            self.atom_ids[0,:] = invars.traj_handle['atom_types'][:]                # get the atom TYPES

        # optionally unimpose minimum image convention
        if invars.unwrap_pos:

            if sqw.rank == 0:
                message = 'unwrapping positions'
                print_stdout(message,msg_type='NOTE')

            self._unwrap_positions(invars,sqw)

    # -----------------------------------------------------------------------------------------

    def close(self):
        """
        close the hdf5 file
        """
        self.handle.close()

    # =======================================================================================
    # ------------------------------ private methods ----------------------------------------
    # =======================================================================================

    def _unwrap_positions(self,invars,sqw):
        """
        un-apply minimum image convention so that positions dont jump discontinuously
        by a full box length. this wont be memory effecient but should be fast... ish

        the issue is that, if the positions are written out 'wrapped' (e.g. lammps
        x y z instead of xu yu zu), then atoms that cross the box boundary are wrapped
        back to the other side of the box. in that case, atoms near the box boundary will
        occasionally jump discontinously by a full-box lenght. i did some checking and this
        screws up the debye waller factor at low Q (i.e. wave-length ~ the box). it was
        only a minor effect, but this takes care of it and isn't super expensive.

        the solution is to 'un-impose' the minimum image convention. i.e. treat every
        atom as the center of the cell at t=0 and at all other times t', if the atom has
        deviated by half a box length (i.e. outside the cell since the atom is at the
        center), shift it back. See e.g. Allen: "Computer Simulation of Liquids".
        """

        lx = sqw.box_lengths[0] 
        ly = sqw.box_lengths[1]
        lz = sqw.box_lengths[2]

        # build an array to be added to the positions to shift them 
        shift = sqw.pos-np.tile(sqw.pos[0,:,:].reshape((1,invars.num_atoms,3)),
                reps=[sqw.block_steps,1,1])

        # check whether to shift atoms in the x direction     
        dr = -lx*(shift[:,:,0] > lx/2).astype(int)
        dr = dr+lx*(shift[:,:,0] <= -lx/2).astype(int)
        shift[:,:,0] = np.copy(dr)

        # check whether to shift atoms in the y direction  
        dr = -ly*(shift[:,:,1] > ly/2).astype(int)
        dr = dr+ly*(shift[:,:,1] <= -ly/2).astype(int)
        shift[:,:,1] = np.copy(dr)

        # check whether to shift atoms in the z direction   
        dr = -lz*(shift[:,:,2] > lz/2).astype(int)
        dr = dr+lz*(shift[:,:,2] <= -lz/2).astype(int)
        shift[:,:,2] = np.copy(dr)

        # apply the shift    
        sqw.pos = sqw.pos+shift

# ============================================================================================
# --------------------------------------------------------------------------------------------
# ============================================================================================

def save_sqw(invars,Qpts,energy,sqw,f_name='sqw.hdf5'):
    """
    write the output to an hdf5 file. use the read_sqw method to read it 
    """
    fmt = '%6.10f'

    num_e = energy.shape[0]
    num_Q = Qpts.shape[0]

    f_name = os.path.join(invars.output_dir,f_name)
    with h5py.File(f_name,'w') as db:
        db_energy = db.create_dataset('energy_meV',[num_e])
        db_Qpts = db.create_dataset('Qpts_rlu',[num_Q,3])
        db_sqw = db.create_dataset('sqw',[num_e,num_Q])
        db_energy[:] = energy[:]
        db_Qpts[:,:] = Qpts[:,:]
        db_sqw[:,:] = sqw[:,:]

# --------------------------------------------------------------------------------------------

def read_sqw(f_name):

    """
    read the sqw data written with save_sqw
    """

    with h5py.File(f_name,'r') as db:
        energy = db['energy_meV'][:]
        Qpts = db['Qpts_rlu'][:,:]
        sqw = db['sqw'][:,:]

    return energy, Qpts, sqw




