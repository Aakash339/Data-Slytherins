# run this in terminal to install matplotlib (python -m pip install matplotlib)
import random
import math
import time
import matplotlib.pyplot as plt

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def brute_force(points):
    best=float("inf")
    pair=None
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            d=distance(points[i], points[j])
            if d<best:
                best=d
                pair=(points[i], points[j])
    return best, pair

def divide_conquer(points):
    if len(points) <= 3:
        return brute_force(points)
    points = sorted(points, key=lambda p: (p[0], p[1]))
    mid = len(points) // 2
    left = points[:mid]
    right = points[mid:]
    split_x = right[0][0]
    d1, p1 = divide_conquer(left)
    d2, p2 = divide_conquer(right)
    if d1<=d2:
        best, pair = d1, p1
    else:
        best, pair = d2, p2
    strip = [p for p in points if abs(p[0] - split_x) < best]
    strip.sort(key=lambda p: p[1])
    for i in range(len(strip)):
        for j in range(i + 1, len(strip)):
            if strip[j][1] - strip[i][1] >= best:
                break
            d=distance(strip[i], strip[j])
            if d<best:
                best=d
                pair=(strip[i], strip[j])
    return best, pair
n = int(input("Enter number of points: "))

if n<2:
    print("Please enter at least 2 points.")
else:
    points=[
        (random.randint(0, 100), random.randint(0, 100))
        for _ in range(n)
    ]
    print("\nGenerated Points:", points)
    start=time.perf_counter()
    b_dist, b_pair = brute_force(points)
    b_time=(time.perf_counter()-start)*1000

    start=time.perf_counter()
    d_dist, d_pair = divide_conquer(points)
    d_time=(time.perf_counter() - start)*1000
    print(f"\nBrute-Force: {b_dist:.6f}, {b_pair[0]}, {b_pair[1]}")
    print(f"Divide-and-Conquer: {d_dist:.6f}, {d_pair[0]}, {d_pair[1]}")
    print(f"Execution Time: Brute-Force = {b_time:.3f} ms, "
          f"Divide-and-Conquer = {d_time:.3f} ms")
    if math.isclose(b_dist, d_dist):
        print("Both algorithms agree.")
    else:
        print("Results do not match.")

    # Analyzing the performance
    print("\nPerformance Analysis")
    print(f"{'N':<10}{'Brute Force (ms)':<22}"
          f"{'Divide & Conquer (ms)'}")

    for size in [10, 50, 100, 250, 500]:
        test_points=[
            (random.randint(0, 10000), random.randint(0, 10000))
            for _ in range(size)
        ]
        start=time.perf_counter()
        brute_force(test_points)
        bt=(time.perf_counter()-start)*1000

        start=time.perf_counter()
        divide_conquer(test_points)
        dt=(time.perf_counter()-start)*1000
        print(f"{size:<10}{bt:<22.3f}{dt:.3f}")

    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.scatter(x, y, color="blue", label="All Points")

    p1, p2 = d_pair

    plt.scatter(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color="red",
        label="Closest Pair",
        zorder=3
    )
    plt.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color="red"
    )
    plt.title(f"Closest Pair Distance={d_dist:.2f}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.show()