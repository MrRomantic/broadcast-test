#!/usr/bin/env python3

def prds(xs):
    acc = 1
    zs = []
    for x in xs:
        acc *= x
        zs.append(acc)
    return zs

def prd(xs):
    acc = 1
    for x in xs:
        acc *= x
    return acc


def strides(shape):
    acc = 1
    st = list(shape)
    for j in range(len(shape) - 1, -1, -1):
        acc *= shape[j]
        st[j] = acc
    return st


def stride2(shape):
    return prds(shape[::-1])[::-1] #[1:] + [1]


def simplify_shapes(xs, ys):
    x0 = y0 = 1
    prev_same = False
    for x1, y1 in zip(xs, ys):
        cur_same = x1 == y1
        if not cur_same:
            if x1 != 1 and y1 != 1:
                raise Exception(f"NOT SAME! {x1} != {y1} on pos _")
        if prev_same == cur_same:
            x0 *= x1
            y0 *= y1
        else:
            yield x0, y0
            x0 = x1
            y0 = y1
        prev_same = cur_same
    yield x0, y0


def pr(x):
    shape, ar = x
    #strides = prds(shape[::-1])[::-1][1:] + [1]
    st = strides(shape)
    pr_(ar, shape, st, 0, 0)
    print()


def pr_(ar, shape, st, i, j):
    if i == len(shape) - 1:
        for k in range(shape[i]):
            print(ar[j + k], end=" ")
        print()
    else:
        for k in range(shape[i]):
            pr_(ar, shape, st, i + 1, st[i + 1] * k + j)
    # TODO print nl?


def extend_shapes(xsh, ysh):
    if len(xsh) < len(ysh):
        xsh = [1] * (len(ysh) - len(xsh)) + xsh
    elif len(ysh) < len(xsh):
        ysh = [1] * (len(xsh) - len(ysh)) + ysh
    return xsh, ysh


def merge_shapes(xsh, ysh):
    zsh = []
    for x, y in zip(xsh, ysh):
        zsh.append(max(x, y))
    return zsh


def bin_apply(x, y, kernel):
    xsh, xbuf = x
    ysh, ybuf = y

    # prepare shapes
    xsh, ysh = extend_shapes(xsh, ysh)
    xsh, ysh = zip(*simplify_shapes(xsh, ysh))
    zsh = merge_shapes(xsh, ysh)

    # prepare strides
    xst = strides(xsh)[1:]
    yst = strides(ysh)[1:]
    zst = strides(zsh)[1:]

    # apply and return
    z = arr_fill(zsh, 0)
    bin_apply_(kernel, xbuf, ybuf, z[1], xsh, ysh, xst, yst, zst, 0, 0, 0, 0)
    return z


def bin_apply_(kernel, x, y, z, xsh, ysh, xst, yst, zst, xo, yo, zo, i):
    if i == len(xsh) - 1:
        kernel(x, y, z, xsh[i], ysh[i], xo, yo, zo)
    else:
        if xsh[i] == ysh[i]:
            for j in range(xsh[i]):
                bin_apply_(kernel, x, y, z, xsh, ysh, xst, yst, zst, xst[i] * j + xo, yst[i] * j + yo, zst[i] * j + zo, i + 1)
        elif xsh[i] == 1:
            for j in range(ysh[i]):
                bin_apply_(kernel, x, y, z, xsh, ysh, xst, yst, zst, xo, yst[i] * j + yo, zst[i] * j + zo, i + 1)
        elif ysh[i] == 1:
            for j in range(xsh[i]):
                bin_apply_(kernel, x, y, z, xsh, ysh, xst, yst, zst, xst[i] * j + xo, yo, zst[i] * j + zo, i + 1)
        else:
            assert False


def add_kernel(x, y, z, xshl, yshl, xo, yo, zo):
    if xshl == yshl:
        for j in range(xshl):
            z[zo + j] = x[xo + j] + y[yo + j]
    elif xshl == 1:
        for j in range(yshl):
            z[zo + j] = x[xo] + y[yo + j]
    elif yshl == 1:
        for j in range(xshl):
            z[zo + j] = x[xo + j] + y[yo]
    else:
        assert False


def arr_fill(shape, fill):
    return shape, [fill] * prd(shape)


def arr_reshape(x, new_sh):
    sh, x = x
    assert prd(sh) == prd(new_sh)
    return new_sh, x


def iota(n):
    return [n], list(range(n))


if __name__ == "__main__":
    #x = iota(10)
    #y = add(x, arr_fill([10,1], 10))
    x = [1,2,3], [0,1,2,3,4,5]
    y = [1,3], [10,20,30]
    z = bin_apply(x, y, add_kernel)
    pr(x)
    pr(y)
    pr(z)
