def split_every(n: int, string: str):
    start, end = 0, n
    piece = string[start:end]
    while piece:
        yield piece
        start, end = start + n, end + n
        piece = string[start:end]
