import numpy as np
import pytest
import scipy as sp
import scipy.sparse

from glm_benchmarks.matrix.sandwich.sandwich import dense_sandwich, sparse_sandwich


@pytest.mark.parametrize("dtype", [np.float64, np.float32])
def test_fast_sandwich_sparse(dtype):
    A = simulate_matrix(dtype=dtype).tocsc()

    d = np.ones(A.shape[0], dtype=dtype)
    true = A.T.dot(A).toarray()
    AT = A.T.tocsc()

    out = sparse_sandwich(A, AT, d)
    np.testing.assert_allclose(true, out, atol=np.sqrt(np.finfo(dtype).eps))


def test_fast_sandwich_dense():
    for i in range(5):
        A = simulate_matrix()
        d = np.random.rand(A.shape[0])

        check(A, d, np.arange(A.shape[1], dtype=np.int32))

        cols = np.random.choice(np.arange(A.shape[1]), size=10, replace=False).astype(
            np.int32
        )
        check(A, d, cols)


def check(A, d, cols):
    Asub = A[:, cols]
    true = Asub.T.dot(Asub).toarray()
    out = dense_sandwich(np.asfortranarray(A.toarray()), d, cols)
    np.testing.assert_allclose(true, out, atol=np.sqrt(np.finfo(np.float64).eps))


def simulate_matrix(nonzero_frac=0.05, shape=(100, 50), seed=0, dtype=np.float64):

    np.random.seed(seed)
    nnz = int(np.prod(shape) * nonzero_frac)
    row_index = np.random.randint(shape[0], size=nnz)
    col_index = np.random.randint(shape[1], size=nnz)
    A = sp.sparse.csr_matrix(
        (np.random.randn(nnz).astype(dtype), (row_index, col_index)), shape
    )
    return A
