#!/usr/bin/python2
# Copyright 2019-2021 TeNPy Developers, GNU GPLv3
import numpy as np
import pytest
from tenpy.models.spins import SpinChain
from tenpy.algorithms import tdvp
from tenpy.algorithms import tebd
from tenpy.networks.mps import MPS


@pytest.mark.slow
def test_tdvp():
    """compare overlap from TDVP with TEBD """
    L = 8
    chi = 20
    delta_t = 0.01
    parameters = {
        'L': L,
        'S': 0.5,
        'conserve': 'Sz',
        'Jz': 1.0,
        'Jy': 1.0,
        'Jx': 1.0,
        'bc_MPS': 'finite',
    }

    M = SpinChain(parameters)
    # prepare system in product state
    product_state = ["up", "down"] * (L // 2)
    psi = MPS.from_product_state(M.lat.mps_sites(), product_state, bc=M.lat.bc_MPS)

    N_steps = 2
    tebd_params = {
        'order': 2,
        'dt': delta_t,
        'N_steps': N_steps,
        'trunc_params': {
            'chi_max': chi,
            'svd_min': 1.e-10,
            'trunc_cut': None
        }
    }

    tdvp_params = {
        'start_time': 0,
        'dt': delta_t,
        'N_steps': N_steps,
        'trunc_params': {
            'chi_max': chi,
            'svd_min': 1.e-10,
            'trunc_cut': None
        }
    }

    # start by comparing TEBD and 2-site TDVP (increasing bond dimension)
    psi_tdvp = psi.copy()
    tebd_engine = tebd.TEBDEngine(psi, M, tebd_params)
    tdvp2_engine = tdvp.TwoSiteTDVPEngine(psi_tdvp, M, tdvp_params)
    for _ in range(10):
        tebd_engine.run()
        tdvp2_engine.run()
        ov = psi.overlap(psi_tdvp)
        assert np.abs(1 - np.abs(ov)) < 1e-10

    # now compare TEBD and 1-site TDVP (constant bond dimension)
    tdvp_params['start_time'] = tdvp2_engine.evolved_time
    tdvp1_engine = tdvp.SingleSiteTDVPEngine(psi_tdvp, M, tdvp_params)
    for _ in range(10):
        tebd_engine.run()
        tdvp1_engine.run()
        ov = psi.overlap(psi_tdvp)
        assert np.abs(1 - np.abs(ov)) < 1e-10
