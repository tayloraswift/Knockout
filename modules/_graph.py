def generate_key(FLOW, subcell, c, top, py, P):
    ky = [top - py]
    for S in FLOW:
        S.cast(subcell, c, ky[-1] + py, P)
        ky.append(S.y - py + 4)
    return ky, list(zip(ky, ky[1:]))
