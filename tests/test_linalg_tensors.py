"""A collection of tests for tenpy.linalg.tensors."""
# Copyright 2023-2023 TeNPy Developers, GNU GPLv3
from multiprocessing.sharedctypes import Value
import numpy as np
from tenpy.linalg.tensors import *
from tenpy.linalg.backends import NoSymmetryNumpyBackend
from tenpy.linalg.symmetries import VectorSpace
import pytest



def test_Tensor_methods():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random((2, 3, 10))
    data2 = np.random.random((2, 3, 10))
    
    legs = [VectorSpace.non_symmetric(d) for d in data.shape]
    
    print('checking __init__ with labels=None')
    tens1 = Tensor(data, backend, legs, labels=None)
    tens1.check_sanity()

    print('checking __init__, partially labelled')
    tens2 = Tensor(data2, backend, legs, labels=[None, 'a', 'b'])
    tens2.check_sanity()

    print('checking __init__, fully labelled')
    tens3 = Tensor(data, backend, legs, labels=['foo', 'a', 'b'])
    tens3.check_sanity()

    print('check size')
    assert tens3.size == np.prod(data.shape)

    # TODO reintroduce when implemented
    # print('check num_parameters')
    # assert tens3.num_parameters == prod(data.shape)

    print('check is_fully_labelled')
    assert not tens1.is_fully_labelled
    assert not tens2.is_fully_labelled
    assert tens3.is_fully_labelled

    print('check has_label')
    assert tens3.has_label('a')
    assert tens3.has_label('a', 'foo')
    assert not tens3.has_label('bar')
    assert not tens3.has_label('a', 'bar')

    print('check labels_are')
    assert tens3.labels_are('foo', 'a', 'b')
    assert tens3.labels_are('a', 'foo', 'b')
    assert not tens3.labels_are('a', 'foo', 'b', 'bar')

    
    tens3.set_labels(['i', 'j', 'k'])
    assert tens3.labels_are('i', 'j', 'k')

    print('check get_leg_idx')
    assert tens3.get_leg_idx(0) == 0
    assert tens3.get_leg_idx(-1) == 2
    with pytest.raises(KeyError):
        tens3.get_leg_idx(10)
    assert tens3.get_leg_idx('i') == 0
    assert tens3.get_leg_idx('j') == 1
    with pytest.raises(KeyError):
        tens3.get_leg_idx('bar')
    with pytest.raises(TypeError):
        tens3.get_leg_idx(None)

    print('check get_leg_idcs')
    assert tens3.get_leg_idcs('i') == [0]
    assert tens3.get_leg_idcs(['i', 'k', 1]) == [0, 2, 1]

    print('check item')
    tens4 = Tensor(np.ones((1,)), backend, legs=[VectorSpace.non_symmetric(1)])
    assert np.allclose(tens4.item(), 1)
    
    print('check str and repr')
    str(tens1)
    str(tens3)
    repr(tens1)
    repr(tens3)

    print('check addition + multiplication')
    neg_t3 = -tens3
    assert np.allclose(neg_t3.data, -data)
    a = 42
    b = 17
    res = a * tens1 - b * tens2
    assert np.allclose(res.data, a * data - b * data2)
    res = tens1 / a + tens2 / b
    assert np.allclose(res.data, data / a + data2 / b)
    # TODO check strict label behavior!

    with pytest.raises(TypeError):
        tens1 == tens2

    print('check converisions, float, complex, array')
    assert isinstance(float(tens4), float)
    assert np.allclose(float(tens4), 1)
    assert isinstance(complex(tens4 + 2.j * tens4), complex)
    assert np.allclose(complex(tens4 + 2.j * tens4), 1 + 2.j)
    # TODO check that float of a complex tensor raises a warning
    t1_np = np.asarray(tens1)
    assert np.allclose(t1_np, data)



def test_Tensor_classmethods():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random((2, 3, 10))
    
    print('checking from_numpy')
    tens = Tensor.from_numpy(data, backend=backend)
    assert np.allclose(data, tens.data)

    print('checking from_dense_block')
    tens = Tensor.from_dense_block(data, backend=backend)
    assert np.allclose(data, tens.data)

    print('checking zero')
    tens = Tensor.zero(backend, [2, 3, 4])
    assert np.allclose(tens.data, np.zeros([2, 3, 4]))

    print('checking eye')
    tens = Tensor.eye(backend, 5)
    assert np.allclose(tens.data, np.eye(5))
    tens = Tensor.eye(backend, [VectorSpace.non_symmetric(10), 4])
    assert np.allclose(tens.data, np.eye(40).reshape((10, 4, 10, 4)))


def test_tdot():
    backend = NoSymmetryNumpyBackend()
    a = VectorSpace.non_symmetric(7)
    b = VectorSpace.non_symmetric(13)
    c = VectorSpace.non_symmetric(22)
    d = VectorSpace.non_symmetric(11)
    data1 = np.random.random((a.dim, b.dim, c.dim))
    data2 = np.random.random((b.dim, c.dim, d.dim))
    data3 = np.random.random((a.dim, b.dim))
    data4 = np.random.random((c.dim, b.dim))
    data5 = np.random.random((c.dim, a.dim, b.dim))
    t1 = Tensor.from_numpy(data1, backend, legs=[a, b, c])
    t2 = Tensor.from_numpy(data2, backend, legs=[b.dual, c.dual, d.dual])
    t3 = Tensor.from_numpy(data3, backend, legs=[a.dual, b.dual])
    t4 = Tensor.from_numpy(data4, backend, legs=[c.dual, b.dual])
    t5 = Tensor.from_numpy(data5, backend, legs=[c.dual, a.dual, b.dual])
    t1_labelled = Tensor.from_numpy(data1, backend, legs=[a, b, c], labels=['a', 'b', 'c'])
    t2_labelled = Tensor.from_numpy(data2, backend, legs=[b.dual, c.dual, d.dual], labels=['b*', 'c*', 'd*'])
    t3_labelled = Tensor.from_numpy(data3, backend, legs=[a.dual, b.dual], labels=['a*', 'b*'])
    t4_labelled = Tensor.from_numpy(data4, backend, legs=[c.dual, b.dual], labels=['c*', 'b*'])
    t5_labelled = Tensor.from_numpy(data5, backend, legs=[c.dual, a.dual, b.dual], labels=['c*', 'a*', 'b*'])

    print('contract one leg')
    expect = np.tensordot(data1, data2, (1, 0))
    res1 = tdot(t1, t2, 1, 0).data
    res2 = tdot(t1_labelled, t2_labelled, 1, 0).data
    res3 = tdot(t1_labelled, t2_labelled, 'b', 'b*').data
    assert np.allclose(res1, expect)
    assert np.allclose(res2, expect)
    assert np.allclose(res3, expect)
    
    print('contract two legs')
    expect = np.tensordot(data1, data2, ([1, 2], [0, 1]))
    res1 = tdot(t1, t2, [1, 2], [0, 1]).data
    res2 = tdot(t1_labelled, t2_labelled, [1, 2], [0, 1]).data
    res3 = tdot(t1_labelled, t2_labelled, ['b', 'c'], ['b*', 'c*']).data
    assert np.allclose(res1, expect)
    assert np.allclose(res2, expect)
    assert np.allclose(res3, expect)

    print('contract all legs of first tensor')
    expect = np.tensordot(data3, data1, ([0, 1], [0, 1]))
    res1 = tdot(t3, t1, [0, 1], [0, 1]).data
    res2 = tdot(t3_labelled, t1_labelled, [0, 1], [0, 1]).data
    res3 = tdot(t3_labelled, t1_labelled, ['a*', 'b*'], ['a', 'b']).data
    assert np.allclose(res1, expect)
    assert np.allclose(res2, expect)
    assert np.allclose(res3, expect)

    print('contract all legs of second tensor')
    expect = np.tensordot(data1, data4, ([1, 2], [1, 0]))
    res1 = tdot(t1, t4, [1, 2], [1, 0]).data
    res2 = tdot(t1_labelled, t4_labelled, [1, 2], [1, 0]).data
    res3 = tdot(t1_labelled, t4_labelled, ['b', 'c'], ['b*', 'c*']).data
    assert np.allclose(res1, expect)
    assert np.allclose(res2, expect)
    assert np.allclose(res3, expect)

    print('scalar result')
    expect = np.tensordot(data1, data5, ([0, 1, 2], [1, 2, 0]))
    res1 = tdot(t1, t5, [0, 1, 2], [1, 2, 0]).data
    res2 = tdot(t1_labelled, t5_labelled, [0, 1, 2], [1, 2, 0]).data
    res3 = tdot(t1_labelled, t5_labelled, ['a', 'b', 'c'], ['a*', 'b*', 'c*']).data
    assert np.allclose(res1, expect)
    assert np.allclose(res2, expect)
    assert np.allclose(res3, expect)


def test_outer():
    backend = NoSymmetryNumpyBackend()
    data1 = np.random.random([3, 5])
    data2 = np.random.random([4, 8])
    t1 = Tensor.from_numpy(data1, backend, labels=['a', 'f'])
    t2 = Tensor.from_numpy(data2, backend, labels=['g', 'b'])
    expect = data1[:, :, None, None] * data2[None, None, :, :]
    res = outer(t1, t2)
    assert np.allclose(expect, res.data)
    assert res.labels_are('a', 'f', 'g', 'b')


def test_inner():
    backend = NoSymmetryNumpyBackend()
    data1 = np.random.random([3, 5]) + 1.j * np.random.random([3, 5])
    data2 = np.random.random([3, 5]) + 1.j * np.random.random([3, 5])
    data3 = np.random.random([5, 3]) + 1.j * np.random.random([5, 3])
    t1 = Tensor.from_numpy(data1, backend)
    t2 = Tensor.from_numpy(data2, backend, labels=['a', 'b'])
    t3 = Tensor.from_numpy(data3, backend, labels=['b', 'a'])
    expect1 = np.tensordot(np.conj(data1), data2, ([0, 1], [0, 1]))
    res1 = inner(t1, t2)
    assert np.allclose(expect1, res1)
    expect2 = np.tensordot(np.conj(data2), data3, ([0, 1], [1, 0]))
    res2 = inner(t2, t3)
    assert np.allclose(expect2, res2)


def test_transpose():
    backend = NoSymmetryNumpyBackend()
    shape = [3, 5, 7, 10]
    data = np.random.random(shape) + 1.j * np.random.random(shape)
    t = Tensor.from_numpy(data, backend, labels=['a', 'b', 'c', 'd'])
    res = transpose(t, [2, 0, 3, 1])
    assert res.labels == ['c', 'a', 'd', 'b']
    assert np.allclose(res.data, np.transpose(data, [2, 0, 3, 1]))
    

def test_trace():
    backend = NoSymmetryNumpyBackend()

    print('single legpair - default legs* args')
    data = np.random.random([7, 7, 7]) + 1.j * np.random.random([7, 7, 7])
    legs = [VectorSpace.non_symmetric(7), VectorSpace.non_symmetric(7), VectorSpace.non_symmetric(7).dual]
    tens = Tensor.from_numpy(data, backend, legs, labels=['a', 'b', 'b*'])
    expect = np.trace(data, axis1=-2, axis2=-1)
    res = trace(tens)
    assert res.labels_are('a')
    assert np.allclose(expect, res.data)

    print('single legpair - via idx or label')
    expect = np.trace(data, axis1=0, axis2=2)
    res_idx = trace(tens, 0, 2)
    res_label = trace(tens, 'a', 'b*')
    assert res_idx.labels_are('b')
    assert np.allclose(res_idx.data, expect)
    assert res_label.labels_are('b')
    assert np.allclose(res_label.data, expect)

    print('two legpairs')
    data = np.random.random([11, 13, 11, 7, 13]) + 1.j * np.random.random([11, 13, 11, 7, 13])
    expect = np.trace(np.trace(data, axis1=1, axis2=4), axis1=0, axis2=1)
    a = VectorSpace.non_symmetric(11)
    b = VectorSpace.non_symmetric(13)
    c = VectorSpace.non_symmetric(7)
    tens = Tensor.from_numpy(data, backend, [a, b.dual, a.dual, c, b], labels=['a', 'b*', 'a*', 'c', 'b'])
    res_idx = trace(tens, [0, 1], [2, 4])
    res_label = trace(tens, ['a', 'b*'], ['a*', 'b'])
    assert res_idx.labels_are('c')
    assert np.allclose(res_idx.data, expect)
    assert res_label.labels_are('c')
    assert np.allclose(res_label.data, expect)

    print('scalar result')
    data = np.random.random([11, 13, 11, 13]) + 1.j * np.random.random([11, 13, 11, 13])
    expect = np.trace(np.trace(data, axis1=1, axis2=3), axis1=0, axis2=1)
    a = VectorSpace.non_symmetric(11)
    b = VectorSpace.non_symmetric(13)
    tens = Tensor.from_numpy(data, backend, [a, b.dual, a.dual, b], labels=['a', 'b*', 'a*', 'b'])
    res_idx = trace(tens, [0, 1], [2, 3])
    res_label = trace(tens, ['a', 'b*'], ['a*', 'b'])
    assert isinstance(res_idx, complex)
    assert np.allclose(res_idx, expect)
    assert isinstance(res_label, complex)
    assert np.allclose(res_label, expect)
    

def test_conj():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random([2, 4, 5]) + 1.j * np.random.random([2, 4, 5])
    tens = Tensor.from_numpy(data, backend, labels=['a', 'b', None])
    res = conj(tens)
    assert np.allclose(res.data, np.conj(data))
    assert res.labels == ['a*', 'b*', None]
    assert [l1.is_dual_of(l2) for l1, l2 in zip(res.legs, tens.legs)]
    

def test_combine_split():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random([2, 4, 7, 5]) + 1.j * np.random.random([2, 4, 7, 5])
    tens = Tensor.from_numpy(data, backend, labels=['a', 'b', 'c', 'd'])

    print('check by idx')
    res = combine_legs(tens, [1, 2])
    assert np.allclose(res.data, np.reshape(data, [2, 28, 5]))
    assert res.labels == ['a', '(b.c)', 'd']
    split = split_leg(res, 1)
    assert np.allclose(split.data, data)
    assert split.labels == ['a', 'b', 'c', 'd']

    print('check by label')
    res = combine_legs(tens, ['b', 'd'])
    expect = np.reshape(np.transpose(data, [0, 1, 3, 2]), [2, 20, 7])
    assert np.allclose(res.data, expect)
    assert res.labels == ['a', '(b.d)', 'c']
    split = split_leg(res, '(b.d)')
    assert np.allclose(split.data, np.transpose(data, [0, 1, 3, 2]))
    assert split.labels == ['a', 'b', 'd', 'c']

    print('check splitting a non-combined leg raises')
    with pytest.raises(ValueError):
        split_leg(res, 0)
    with pytest.raises(ValueError):
        split_leg(res, 'a')
    

def test_is_scalar():
    backend = NoSymmetryNumpyBackend()
    assert is_scalar(1) 
    assert is_scalar(0.) 
    assert is_scalar(1. + 2.j) 
    scalar_tens = Tensor.from_numpy([[1.]], backend)
    assert is_scalar(scalar_tens)
    non_scalar_tens = Tensor.from_numpy([[1., 2.], [3., 4.]], backend)
    assert not is_scalar(non_scalar_tens)
    

def test_allclose():
    backend = NoSymmetryNumpyBackend()
    pass  # FIXME 
    

def test_squeeze_legs():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random([2, 1, 7, 1, 1]) + 1.j * np.random.random([2, 1, 7, 1, 1])
    tens = Tensor.from_numpy(data, backend, labels=['a', 'b', 'c', 'd', 'e'])

    print('squeezing all legs (default arg)')
    res = squeeze_legs(tens)
    assert np.allclose(res.data, data[:, 0, :, 0, 0])
    assert res.labels == ['a', 'c']

    print('squeeze specific leg by idx')
    res = squeeze_legs(tens, 1)
    assert np.allclose(res.data, data[:, 0, :, :, :])
    assert res.labels == ['a', 'c', 'd', 'e']

    print('squeeze legs by labels')
    res = squeeze_legs(tens, ['b', 'e'])
    assert np.allclose(res.data, data[:, 0, :, :, 0])
    assert res.labels == ['a', 'c', 'd']
    

def test_norm():
    backend = NoSymmetryNumpyBackend()
    data = np.random.random([2, 3, 7]) + 1.j * np.random.random([2, 3, 7])
    tens = Tensor.from_numpy(data, backend)
    res = norm(tens)
    expect = np.linalg.norm(data)
    assert np.allclose(res, expect)
