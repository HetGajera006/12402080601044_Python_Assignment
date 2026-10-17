
import re
from collections import defaultdict, deque


def time_to_minutes(timestamp):
    hours, minutes = map(int, timestamp.split(":"))
    return hours * 60 + minutes


def detect_suspicious_users(X, T, logs):
    # Store failed login attempts for each user.
    failures = defaultdict(deque)
    suspicious = {}

    pattern = re.compile(
        r"^(\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)$"
    )

    for log in logs:
        match = pattern.fullmatch(log.strip())

        if not match:
            continue

        timestamp, user, ip, status = match.groups()
        current_time = time_to_minutes(timestamp)

        if status == "FAIL":
            failures[user].append((current_time, ip))

            # Remove failures outside the T-minute window.
            while (
                failures[user]
                and current_time - failures[user][0][0] > T
            ):
                failures[user].popleft()

        elif status == "SUCCESS":
            # Remove expired failed attempts.
            while (
                failures[user]
                and current_time - failures[user][0][0] > T
            ):
                failures[user].popleft()

            # Check whether enough failures came from another IP.
            count = sum(
                1 for _, failed_ip in failures[user]
                if failed_ip != ip
            )

            if count >= X and user not in suspicious:
                suspicious[user] = timestamp

    return suspicious


def main():
    try:
        X, T = map(int, input("Enter X and T: ").split())
        n = int(input("Enter number of logs: "))

        if X < 1 or T < 1 or n < 1:
            print("Error: X, T and n must be positive.")
            return

        logs = []

        for _ in range(n):
            logs.append(input().strip())

        result = detect_suspicious_users(X, T, logs)

        for user in sorted(result):
            print(user, result[user])

    except ValueError:
        print("Error: Invalid input format.")


if __name__ == "__main__":
    main()
