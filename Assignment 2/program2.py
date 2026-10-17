
import re
from html.parser import HTMLParser
from pathlib import Path


class ProductParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # Start a product block.
        if "product" in attrs.get("class", "").lower().split():
            self.current = {}
            self.field = None

        if self.current is not None:
            classes = attrs.get("class", "").lower()

            if "name" in classes:
                self.field = "name"
            elif "price" in classes:
                self.field = "price"
            elif "rating" in classes:
                self.field = "rating"

    def handle_data(self, data):
        if self.current is not None and self.field:
            self.current[self.field] = (
                self.current.get(self.field, "") + data.strip()
            )

    def handle_endtag(self, tag):
        if self.current is not None:
            if all(k in self.current for k in ("name", "price", "rating")):
                self.products.append(self.current)
                self.current = None
                self.field = None


def normalize_price(price_text):
    # Remove currency symbols and commas.
    value = re.sub(r"[^\d.]", "", price_text)
    return float(value)


def extract_products(file_path):
    parser = ProductParser()

    with open(file_path, "r", encoding="utf-8") as file:
        parser.feed(file.read())

    return parser.products


def main():
    try:
        p, k = map(int, input("Enter number of files and K: ").split())

        if p < 1 or k < 1:
            print("Error: p and K must be positive.")
            return

        products = {}

        for _ in range(p):
            file_path = input("Enter HTML file path: ").strip()

            if not Path(file_path).is_file():
                print("Error: File not found:", file_path)
                return

            for item in extract_products(file_path):
                try:
                    name = item["name"].strip()
                    price = normalize_price(item["price"])
                    rating = float(item["rating"])

                    if not name or price < 0 or not 0 <= rating <= 5:
                        continue

                    # Keep the best-rated version of each product.
                    key = name.casefold()
                    product = {
                        "name": name,
                        "price": price,
                        "rating": rating
                    }

                    if key not in products:
                        products[key] = product
                    else:
                        old = products[key]
                        if (-rating, price, name) < (
                            -old["rating"], old["price"], old["name"]
                        ):
                            products[key] = product

                except (ValueError, KeyError):
                    continue

        ranked = sorted(
            products.values(),
            key=lambda x: (-x["rating"], x["price"], x["name"])
        )

        for item in ranked[:k]:
            price = int(item["price"]) if item["price"].is_integer() else item["price"]
            print(item["name"], price, item["rating"])

    except ValueError:
        print("Error: Enter valid integer values for p and K.")
    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    main()
