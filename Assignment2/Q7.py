import json
import math
import sys

UNKNOWN = "<unknown>"


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def parse_records(lines):
    for line in lines:
        try:
            rec = json.loads(line)
        except ValueError:
            yield UNKNOWN, None
            continue
        if not isinstance(rec, dict):
            yield UNKNOWN, None
            continue
        device = rec.get("device_id")
        if isinstance(device, bool) or not isinstance(device, (str, int)) or device == "":
            yield UNKNOWN, None
            continue
        yield str(device), rec


def validate_and_transform(parsed):
    for device, rec in parsed:
        if rec is None:
            yield device, None
            continue
        temp, hum = rec.get("temperature_c"), rec.get("humidity")
        if not is_number(temp) or not is_number(hum) or not (0 <= hum <= 100):
            yield device, None
            continue
        yield device, (float(temp), float(hum))


def aggregate(records):
    stats = {}
    for device, value in records:
        s = stats.get(device)
        if s is None:
            s = stats[device] = [0, None, None, 0.0, 0]
        if value is None:
            s[4] += 1
            continue
        temp = value[0]
        s[0] += 1
        s[1] = temp if s[1] is None or temp < s[1] else s[1]
        s[2] = temp if s[2] is None or temp > s[2] else s[2]
        s[3] += temp
    return stats


def main():
    path = input("Enter path of JSONL file: ").strip()
    try:
        stats = aggregate(validate_and_transform(parse_records(read_lines(path))))
    except OSError as e:
        print("Error:", e)
        sys.exit(1)
    for device in sorted(stats):
        count, lo, hi, total, bad = stats[device]
        if count:
            print(f"{device} count={count} min={lo:g} max={hi:g} avg={total / count:.2f} corrupted={bad}")
        else:
            print(f"{device} count=0 min=NA max=NA avg=NA corrupted={bad}")


if __name__ == "__main__":
    main()
