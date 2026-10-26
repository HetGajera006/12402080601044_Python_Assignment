import re
import sys
from collections import deque

LOG_RE = re.compile(r"^(\d{1,2}):(\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)\s*$")


def main():
    stream = sys.stdin
    try:
        x, t = map(int, stream.readline().split())
        n = int(stream.readline())
    except ValueError:
        print("Error: invalid header")
        sys.exit(1)
    if not (1 <= x <= 100 and 1 <= t <= 1440 and n >= 1):
        print("Error: constraints violated")
        sys.exit(1)

    fails = {}
    armed = {}
    flagged = {}

    for _ in range(n):
        line = stream.readline()
        if not line:
            break
        m = LOG_RE.match(line)
        if not m:
            continue
        hh, mm, user, ip, status = m.groups()
        minute = int(hh) * 60 + int(mm)
        if status == "FAIL":
            dq = fails.setdefault(user, deque())
            dq.append((minute, ip))
            while minute - dq[0][0] > t:
                dq.popleft()
            if len(dq) >= x:
                armed[user] = ip
        else:
            if user in flagged or user not in armed:
                continue
            if ip != armed[user]:
                flagged[user] = f"{int(hh):02d}:{mm}"
            else:
                del armed[user]

    for user in sorted(flagged):
        print(user, flagged[user])


if __name__ == "__main__":
    main()
