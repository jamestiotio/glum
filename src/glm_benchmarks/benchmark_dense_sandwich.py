import time

import numpy as np
import pandas as pd

from glm_benchmarks.sandwich.sandwich import dense_sandwich


def numpy_mklC(X, d):
    sqrtD = np.sqrt(d)[:, np.newaxis]
    x_d = X[0] * sqrtD
    return x_d.T @ x_d


def numpy_mklF(X, d):
    sqrtD = np.sqrt(d)[:, np.newaxis]
    x_d = X[1] * sqrtD
    return x_d.T @ x_d


def bench(f, iter):
    ts = []
    for i in range(iter):
        start = time.time()
        out = f()
        ts.append(time.time() - start)
    return ts, out


def _dense_sandwich(X, d):
    return dense_sandwich(X[0], d, 400, 10, 500000000, 64)


def mn_run(m, n, iter, dtype):
    precision = dtype().itemsize * 8
    X = [np.random.rand(n, m).astype(dtype=dtype)]
    d = np.random.rand(n).astype(dtype=dtype)

    X.append(np.asfortranarray(X[0]))

    out = dict()
    out["name"] = []
    out["runtime"] = []
    to_run = [
        "numpy_mklC",
        "numpy_mklF",
        "_dense_sandwich",
    ]
    for name in to_run:
        ts, result = bench(lambda: globals()[name](X, d), iter)
        if name == "numpy_mklC":
            true = result
        elif "numpy_mklC" in to_run:
            err = np.abs((true - result) / true)
            np.testing.assert_almost_equal(err, 0, 4 if precision == 32 else 7)
        runtime = np.min(ts)
        out["name"].append(name)
        out["runtime"].append(runtime)
        print(name, runtime)
    out_df = pd.DataFrame(out)
    out_df["m"] = m
    out_df["n"] = n
    out_df["precision"] = precision
    return out_df


def main():
    iter = 10
    Rs = []
    for m, n in [
        # (20, 1000000),
        # (50, 500000),
        # (150, 200000),
        # (300, 100000),
        # (2048, 2048),
        (1500, 1500),
        (500, 500),
    ]:
        for dt in [np.float64]:
            Rs.append(mn_run(m, n, iter, dt))
    df = pd.concat(Rs)
    df.set_index(["m", "n", "name", "precision"], inplace=True)
    df.sort_index(inplace=True)
    print(df)


def main2():
    n = 1000
    m = 1000
    dtype = np.float64
    X = np.asfortranarray(np.random.rand(n, m).astype(dtype=dtype))
    d = np.random.rand(n).astype(dtype=dtype)
    t1d = []
    pls = []
    krs = []
    kstps = []
    results = []
    # for thresh1d in [16, 32, 64, 128]:
    #     for parlevel in [5, 7, 10, 13]:
    #         for kratio in [1, 10, 20, 80]:
    for thresh1d in [300, 400]:
        for parlevel in [10]:
            for kratio in [1000]:
                for kstep in [32, 64, 128]:
                    t1d.append(thresh1d)
                    pls.append(parlevel)
                    krs.append(kratio)
                    kstps.append(kstep)
                    # results.append(np.min(bench(lambda: X.T @ X, 20)[0]))
                    results.append(
                        np.min(
                            bench(
                                lambda: dense_sandwich(
                                    X, d, thresh1d, parlevel, kratio, kstep
                                ),
                                20,
                            )[0]
                        )
                    )
                    print(results[-1])
    df = pd.DataFrame(
        dict(thresh1d=t1d, parlevel=pls, kratio=krs, ksteps=kstps, results=results)
    )
    df.set_index(["thresh1d", "parlevel", "kratio", "ksteps"], inplace=True)
    df.sort_index(inplace=True)
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(df)


#  841650213      L1-dcache-load-misses     #   12.01% of all L1-dcache hits    (71.87%)
# 7006517280      L1-dcache-loads                                               (71.53%)
# 1016757397      L1-dcache-stores                                              (69.82%)


if __name__ == "__main__":
    main()
