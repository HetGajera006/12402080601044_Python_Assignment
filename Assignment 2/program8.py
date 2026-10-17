
MOD = 1000000007


def maximum_score_path(matrix, n, m):
    # Each state stores [maximum score, number of ways].
    dp = [[None] * m for _ in range(n)]

    if matrix[0][0] is None:
        return None

    dp[0][0] = (matrix[0][0], 1)

    for i in range(n):
        for j in range(m):
            if matrix[i][j] is None:
                continue

            if i == 0 and j == 0:
                continue

            best_score = None
            ways = 0

            # Possible previous cells: left, above, diagonal.
            previous_cells = []

            if j > 0:
                previous_cells.append(dp[i][j - 1])

            if i > 0:
                previous_cells.append(dp[i - 1][j])

            if i > 0 and j > 0:
                previous_cells.append(dp[i - 1][j - 1])

            for previous in previous_cells:
                if previous is None:
                    continue

                previous_score, previous_ways = previous
                candidate = previous_score + matrix[i][j]

                if best_score is None or candidate > best_score:
                    best_score = candidate
                    ways = previous_ways
                elif candidate == best_score:
                    ways = (ways + previous_ways) % MOD

            if best_score is not None:
                dp[i][j] = (best_score, ways)

    result = dp[n - 1][m - 1]

    if result is None:
        return None

    return result


def main():
    try:
        n, m = map(int, input("Enter rows and columns: ").split())

        if not (1 <= n <= 2000 and 1 <= m <= 2000):
            print("Error: Rows and columns must be between 1 and 2000.")
            return

        matrix = []

        for _ in range(n):
            row = input().split()

            if len(row) != m:
                print("Error: Incorrect number of values in a row.")
                return

            values = []

            for value in row:
                if value.upper() == "X":
                    values.append(None)
                else:
                    values.append(int(value))

            matrix.append(values)

        result = maximum_score_path(matrix, n, m)

        if result is None:
            print("IMPOSSIBLE")
        else:
            score, count = result
            print(score, count)

    except ValueError:
        print("Error: Enter valid integers or X for blocked cells.")


if __name__ == "__main__":
    main()
