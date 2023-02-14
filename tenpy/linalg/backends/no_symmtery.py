from __future__ import annotations
from abc import ABC, abstractmethod
from math import prod

from .abstract_backend import AbstractBackend, AbstractBlockBackend, Data, Block, Dtype
from ..symmetries import ProductSpace, VectorSpace, no_symmetry, Symmetry
from ..tensors import Tensor


# TODO eventually remove AbstractBlockBackend inheritance, it is not needed,
#  jakob only keeps it around to make his IDE happy


class AbstractNoSymmetryBackend(AbstractBackend, AbstractBlockBackend, ABC):
    """
    Backend with no symmetries.
    Tensor.data is a single block of the AbstractBlockBackend, e.g. a numpy.ndarray for NumpyBlockBackend
    """

    def infer_dtype(self, a: Tensor) -> Dtype:
        return self.block_dtype(a.data)

    def to_dtype(self, a: Tensor, dtype: Dtype) -> Tensor:
        return self.block_to_dtype(a.data, self.parse_dtype(dtype))

    def is_real(self, a: Tensor) -> bool:
        return self.block_is_real(a.data)

    def tdot(self, a: Tensor, b: Tensor, axs_a: list[int], axs_b: list[int]) -> Data:
        return self.block_tdot(a.data, b.data, axs_a, axs_b)

    def item(self, a: Tensor) -> float | complex:
        return self.block_item(a.data)

    def to_dense_block(self, a: Tensor) -> Block:
        return a.data

    def reduce_symmetry(self, a: Tensor, new_symm: Symmetry) -> Data:
        if new_symm == no_symmetry:
            return a.data
        else:
            raise ValueError(f'Can not decrease {no_symmetry} to {new_symm}.')

    def increase_symmetry(self, a: Tensor, new_symm: Symmetry, atol=1e-8, rtol=1e-5) -> Data:
        if new_symm == no_symmetry:
            return a.data
        else:
            raise ValueError(f'{self} can not represent {new_symm}.')

    def copy_data(self, a: Tensor) -> Data:
        return self.block_copy(a.data)

    def _data_repr_lines(self, data: Data, indent: str, max_width: int, max_lines: int):
        return [f'{indent}* Data:'] + self._block_repr_lines(data, indent=indent + '  ', max_width=max_width,
                                                            max_lines=max_lines - 1)

    @abstractmethod
    def svd(self, a: Tensor, axs1: list[int], axs2: list[int], new_leg: VectorSpace | None
            ) -> tuple[Data, Data, Data, VectorSpace]:
        # reshaping, slicing etc is so specific to the BlockBackend that I dont bother unifying anything here.
        # that might change though...
        ...

    def outer(self, a: Tensor, b: Tensor) -> Data:
        return self.block_outer(a.data, b.data)

    def inner(self, a: Tensor, b: Tensor, axs2: list[int] | None) -> complex:
        return self.block_inner(a.data, b.data, axs2)

    def transpose(self, a: Tensor, permutation: list[int]) -> Data:
        return self.block_transpose(a.data, permutation)

    def trace(self, a: Tensor, idcs1: list[int], idcs2: list[int]) -> Data:
        return self.block_trace(a.data, idcs1, idcs2)

    def conj(self, a: Tensor) -> Data:
        return self.block_conj(a.data)

    def combine_legs(self, a: Tensor, idcs: list[int], new_leg: ProductSpace) -> Data:
        return self.block_combine_legs(a.data, idcs)

    def split_leg(self, a: Tensor, leg_idx: int) -> Data:
        return self.block_split_leg(a, leg_idx, dims=[s.dim for s in a.legs[leg_idx]])

    def allclose(self, a: Tensor, b: Tensor, rtol: float, atol: float) -> bool:
        return self.block_allclose(a.data, b.data, rtol=rtol, atol=atol)

    def squeeze_legs(self, a: Tensor, idcs: list[int]) -> Data:
        return self.block_squeeze_legs(a, idcs)

    def norm(self, a: Tensor) -> float:
        return self.block_norm(a.data)

    def exp(self, a: Tensor, idcs1: list[int], idcs2: list[int]) -> Data:
        matrix, aux = self.block_matrixify(a.data, idcs1, idcs2)
        return self.block_dematrixify(self.matrix_exp(matrix), aux)

    def log(self, a: Tensor, idcs1: list[int], idcs2: list[int]) -> Data:
        matrix, aux = self.block_matrixify(a.data, idcs1, idcs2)
        return self.block_dematrixify(self.matrix_log(matrix), aux)

    def random_gaussian(self, legs: list[VectorSpace], dtype: Dtype, sigma: float) -> Data:
        return self.block_random_gaussian([l.dim for l in legs], dtype=dtype, sigma=sigma)

    def add(self, a: Tensor, b: Tensor) -> Data:
        return self.block_add(a.data, b.data)

    def mul(self, a: float | complex, b: Tensor) -> Data:
        return self.block_mul(a, b.data)

