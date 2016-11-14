"""A collection of tests for tenpy.tools submodules"""

import numpy as np
import numpy.testing as npt
import nose.tools as nst
import itertools as it
import tenpy.tools as tools
import warnings


def test_inverse_permutation(N=10):
    x = np.random.random(N)
    p = np.arange(N)
    np.random.shuffle(p)
    xnew = x[p]
    pinv = tools.misc.inverse_permutation(p)
    npt.assert_equal(x, xnew[pinv])


def test_argsort():
    x = [1., -1., 1.5, -1.5, 2.j, -2.j]
    npt.assert_equal(tools.misc.argsort(x, 'LM'), [4, 5, 2, 3, 0, 1])
    npt.assert_equal(tools.misc.argsort(x, 'SM'), [0, 1, 2, 3, 4, 5])
    npt.assert_equal(tools.misc.argsort(x, 'LR'), [2, 0, 4, 5, 1, 3])


def test_speigs():
    x = np.array([1., -1.2, 1.5, -1.8, 2.j, -2.2j])
    tol_NULP = len(x)**3
    x_LM = x[tools.misc.argsort(x, 'm>')]
    x_SM = x[tools.misc.argsort(x, 'SM')]
    A = np.diag(x)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')  # disable warngings temporarily
        for k in range(4, 9):
            print k
            W, V = tools.math.speigs(A, k, which='LM')
            W = W[tools.misc.argsort(W, 'LM')]
            print W, x_LM[:k]
            npt.assert_array_almost_equal_nulp(W, x_LM[:k], tol_NULP)
            W, V = tools.math.speigs(A, k, which='SM')
            W = W[tools.misc.argsort(W, 'SM')]
            print W, x_SM[:k]
            npt.assert_array_almost_equal_nulp(W, x_SM[:k], tol_NULP)


def test_perm_sign():
    res = [tools.math.perm_sign(u) for u in it.permutations(range(4))]
    check = [1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1]
    npt.assert_equal(res, check)


if __name__ == "__main__":
    test_inverse_permutation()
