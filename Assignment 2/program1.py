
import re


def extract_emails(file_path):
    pattern = re.compile(
        r'[A-Za-z0-9._+-]+@'
        r'[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*'
        r'\.(?:com|edu|org)\b',
        re.IGNORECASE
    )

    domains = {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                emails = pattern.findall(line)

                for email in emails:
                    email = email.lower()
                    domain = email.split("@")[1]

                    if domain not in domains:
                        domains[domain] = set()

                    domains[domain].add(email)

    except FileNotFoundError:
        print("Error: File not found.")
        return
    except OSError as error:
        print("Error:", error)
        return

    for domain in sorted(domains):
        emails = domains[domain]
        print(domain, len(emails), min(emails))


file_path = input("Enter text file path: ")
extract_emails(file_path)
