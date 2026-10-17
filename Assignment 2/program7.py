
import json


def read_records(file_path):
    """Read JSON records one line at a time."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)

                device = record["device_id"]
                temperature = float(record["temperature_c"])
                humidity = float(record["humidity"])

                if not isinstance(device, str) or not device.strip():
                    raise ValueError("Invalid device ID")

                if not (-273.15 <= temperature <= 1000):
                    raise ValueError("Invalid temperature")

                if not (0 <= humidity <= 100):
                    raise ValueError("Invalid humidity")

                yield {
                    "device_id": device,
                    "temperature_c": temperature,
                    "humidity": humidity
                }

            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                # Skip corrupted or invalid records.
                continue


def transform_records(records):
    """Convert temperature from Celsius to Fahrenheit."""
    for record in records:
        yield {
            "device_id": record["device_id"],
            "temperature_c": record["temperature_c"],
            "temperature_f": (
                record["temperature_c"] * 9 / 5 + 32
            ),
            "humidity": record["humidity"]
        }


def calculate_statistics(file_path):
    statistics = {}
    corrupted_count = 0

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)

                device = record["device_id"]
                temperature = float(record["temperature_c"])
                humidity = float(record["humidity"])

                if not isinstance(device, str) or not device.strip():
                    raise ValueError("Invalid device ID")

                if not (-273.15 <= temperature <= 1000):
                    raise ValueError("Invalid temperature")

                if not (0 <= humidity <= 100):
                    raise ValueError("Invalid humidity")

                if device not in statistics:
                    statistics[device] = {
                        "count": 0,
                        "min": temperature,
                        "max": temperature,
                        "sum": 0.0
                    }

                stats = statistics[device]
                stats["count"] += 1
                stats["sum"] += temperature
                stats["min"] = min(stats["min"], temperature)
                stats["max"] = max(stats["max"], temperature)

            except (
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError
            ):
                corrupted_count += 1

    for device in sorted(statistics):
        stats = statistics[device]
        average = stats["sum"] / stats["count"]

        print(
            f"{device} count={stats['count']} "
            f"min={stats['min']:g} "
            f"max={stats['max']:g} "
            f"avg={average:.2f} "
            f"corrupted={corrupted_count}"
        )


def main():
    file_path = input("Enter JSONL file path: ").strip()

    try:
        calculate_statistics(file_path)
    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    main()
