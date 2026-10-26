import os
import re
import sys

EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9+._-])"
    r"([A-Za-z0-9+._-]+)@"
    r"((?:[A-Za-z0-9-]+\.)+(?:com|edu|org))"
    r"(?![A-Za-z0-9-])(?!\.[A-Za-z0-9-])",
    re.IGNORECASE,
)


def extract_stats(path):
    users = {}
    smallest = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for m in EMAIL_RE.finditer(line):
                user = m.group(1)
                domain = m.group(2).lower()
                email = user + "@" + domain
                users.setdefault(domain, set()).add(user)
                if domain not in smallest or email < smallest[domain]:
                    smallest[domain] = email
    return users, smallest


def main():
    path = input("Enter path of text file: ").strip()
    if not path or not os.path.isfile(path):
        print("Error: file not found.")
        sys.exit(1)
    try:
        users, smallest = extract_stats(path)
    except OSError as e:
        print("Error reading file:", e)
        sys.exit(1)
    for domain in sorted(users):
        print(domain, len(users[domain]), smallest[domain])


if __name__ == "__main__":
    main()
