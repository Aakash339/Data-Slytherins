
import random
import csv
import time


# 1. Generate a random conflict graph
def generate_graph(n, density):
    graph = {i: set() for i in range(1, n + 1)}

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if random.random() < density:
                graph[i].add(j)
                graph[j].add(i)

    return graph


# 2. Greedy Welsh-Powell algorithm
def welsh_powell(graph, R):
    courses = sorted(
        graph,
        key=lambda course: len(graph[course]),
        reverse=True
    )

    timetable = []

    for course in courses:
        placed = False

        for slot in timetable:
            if len(slot) < R and all(
                other not in graph[course] for other in slot
            ):
                slot.append(course)
                placed = True
                break

        if not placed:
            timetable.append([course])

    return timetable


# 3. Exact backtracking algorithm using DSatur ordering
def exact_scheduling(graph, R, greedy_timetable):
    n = len(graph)

    best = [slot[:] for slot in greedy_timetable]
    upper_bound = len(best)

    # Valid lower bounds
    lower_bound = max(
        max((len(graph[v]) + 1 for v in graph), default=0),
        (n + R - 1) // R
    )

    for k in range(lower_bound, upper_bound):
        colors = {}
        slot_counts = [0] * k

        def select_course():
            unassigned = [
                v for v in graph if v not in colors
            ]

            return max(
                unassigned,
                key=lambda v: (
                    len({
                        colors[u]
                        for u in graph[v]
                        if u in colors
                    }),
                    len(graph[v])
                )
            )

        def backtrack():
            if len(colors) == n:
                return True

            course = select_course()

            forbidden = {
                colors[neighbor]
                for neighbor in graph[course]
                if neighbor in colors
            }

            for color in range(k):
                if color in forbidden:
                    continue

                if slot_counts[color] >= R:
                    continue

                colors[course] = color
                slot_counts[color] += 1

                if backtrack():
                    return True

                del colors[course]
                slot_counts[color] -= 1

            return False

        if backtrack():
            result = [[] for _ in range(k)]

            for course, color in colors.items():
                result[color].append(course)

            return result, True

    # No solution with fewer slots exists
    return best, True


# 4. Display the timetable
def display_timetable(name, timetable, proven):
    print("\n" + name)
    print("-" * 40)
    print("Minimum slots found:", len(timetable))
    print("Proven optimal:", "Yes" if proven else "No")

    for i, slot in enumerate(timetable, start=1):
        print(f"Slot {i}: {', '.join(map(str, sorted(slot)))}")


# 5. Export timetable to CSV
def export_csv(timetable, R, filename):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            f"Hall {i}" for i in range(1, R + 1)
        ])

        for slot in timetable:
            row = sorted(slot) + [""] * (R - len(slot))
            writer.writerow(row)

    print("\nCSV file saved as:", filename)


# 6. Main program
def main():
    print("EXAM TIMETABLE SCHEDULING")
    print("1. Enter conflict graph")
    print("2. Generate random conflict graph")

    choice = int(input("Enter choice (1 or 2): "))

    if choice == 1:
        n, m, R = map(
            int, input("Enter N M R: ").split()
        )

        graph = {i: set() for i in range(1, n + 1)}

        print("Enter conflicting course pairs:")

        for _ in range(m):
            u, v = map(int, input().split())

            if u == v or not (
                1 <= u <= n and 1 <= v <= n
            ):
                raise ValueError("Invalid course pair")

            graph[u].add(v)
            graph[v].add(u)

    elif choice == 2:
        n, R = map(
            int, input("Enter N R: ").split()
        )

        density = float(
            input("Enter edge density (0 to 1): ")
        )

        if not 0 <= density <= 1:
            raise ValueError("Density must be between 0 and 1")

        graph = generate_graph(n, density)

        print("\nGenerated conflict edges:")

        for u in graph:
            for v in sorted(graph[u]):
                if u < v:
                    print(u, v)

    else:
        print("Invalid choice")
        return

    if n < 1 or R < 1:
        print("N and R must be positive.")
        return

    # Run greedy algorithm
    start = time.perf_counter()
    greedy = welsh_powell(graph, R)
    greedy_time = time.perf_counter() - start

    # Run exact algorithm
    start = time.perf_counter()
    exact, optimal = exact_scheduling(graph, R, greedy)
    exact_time = time.perf_counter() - start

    # Display results
    display_timetable(
        "GREEDY WELSH-POWELL",
        greedy,
        False
    )

    display_timetable(
        "EXACT BACKTRACKING",
        exact,
        optimal
    )

    print("\nALGORITHM COMPARISON")
    print("-" * 40)
    print("Greedy slots:", len(greedy))
    print(f"Greedy time: {greedy_time:.6f} seconds")
    print("Exact slots:", len(exact))
    print(f"Exact time: {exact_time:.6f} seconds")
    print("Exact result proven optimal:", optimal)

    export_csv(exact, R, "exam_timetable.csv")


if __name__ == "__main__":
    main()
