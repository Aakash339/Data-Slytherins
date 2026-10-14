def shortest_path(grid, T):
    n = len(grid)

    sr = sc = er = ec = -1

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 'S':
                sr, sc = r, c
            elif grid[r][c] == 'E':
                er, ec = r, c

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    queue = [(sr, sc, 0, 0)]
    front = 0

    visited = set()
    visited.add((sr, sc, 0))

    while front < len(queue):
        r, c, keys, dist = queue[front]
        front += 1

        if (r, c) == (er, ec):
            return dist

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < n and 0 <= nc < n):
                continue

            cell = grid[nr][nc]

            if cell == '#':
                continue

            new_keys = keys

            # Collect key
            if 'a' <= cell <= 'f':
                new_keys |= 1 << (ord(cell) - ord('a'))

            # Check door
            if 'A' <= cell <= 'F':
                required = 1 << (ord(cell) - ord('A'))

                if (new_keys & required) == 0:
                    continue

            state = (nr, nc, new_keys)

            if state not in visited:
                visited.add(state)
                queue.append((nr, nc, new_keys, dist + 1))

    return -1


T = int(input())
N = int(input())

grid = [input().strip() for _ in range(N)]

print(shortest_path(grid, T))