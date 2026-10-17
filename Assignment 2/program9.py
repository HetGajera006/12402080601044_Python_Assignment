
class Product:
    def __init__(self, product_id, name, stock, purchase_price, selling_price):
        self.product_id = product_id
        self.name = name
        self.stock = stock
        self.purchase_price = purchase_price
        self.selling_price = selling_price

    def display(self):
        print(
            self.product_id,
            self.name,
            "stock=" + str(self.stock),
            "purchase=" + str(self.purchase_price),
            "selling=" + str(self.selling_price)
        )


class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.product_id in self.products:
            print("Product already exists.")
            return

        self.products[product.product_id] = product
        print("Product added successfully.")

    def delete_product(self, product_id):
        if product_id in self.products:
            del self.products[product_id]
            print("Product deleted successfully.")
        else:
            print("Product not found.")

    def update_stock(self, product_id, quantity):
        if product_id not in self.products:
            print("Product not found.")
            return

        new_stock = self.products[product_id].stock + quantity

        if new_stock < 0:
            print("Error: Stock cannot be negative.")
            return

        self.products[product_id].stock = new_stock
        print("Stock updated successfully.")

    def total_value(self):
        return sum(
            product.stock * product.purchase_price
            for product in self.products.values()
        )

    def __lt__(self, other):
        return self.total_value() < other.total_value()

    def __add__(self, other):
        merged = Inventory()

        # Copy products from the first inventory.
        for product in self.products.values():
            merged.products[product.product_id] = Product(
                product.product_id,
                product.name,
                product.stock,
                product.purchase_price,
                product.selling_price
            )

        # Merge products from the second inventory.
        for product in other.products.values():
            product_id = product.product_id

            if product_id in merged.products:
                existing = merged.products[product_id]

                if existing.name != product.name:
                    raise ValueError(
                        "Conflicting names for product ID: " + product_id
                    )

                existing.stock += product.stock
                existing.purchase_price = min(
                    existing.purchase_price,
                    product.purchase_price
                )
                existing.selling_price = max(
                    existing.selling_price,
                    product.selling_price
                )
            else:
                merged.products[product_id] = Product(
                    product.product_id,
                    product.name,
                    product.stock,
                    product.purchase_price,
                    product.selling_price
                )

        return merged

    def display_inventory(self):
        if not self.products:
            print("Inventory is empty.")
            return

        for product_id in sorted(self.products):
            self.products[product_id].display()

        print("Total purchase value:", self.total_value())


def main():
    inventory_a = Inventory()
    inventory_b = Inventory()

    # Sample products for inventory A.
    inventory_a.add_product(Product("P1", "Pen", 10, 5, 8))
    inventory_a.add_product(Product("P2", "Book", 5, 20, 30))

    # Sample products for inventory B.
    inventory_b.add_product(Product("P1", "Pen", 7, 4, 9))
    inventory_b.add_product(Product("P3", "Pencil", 20, 2, 4))

    while True:
        print("\n1. Display Inventory A")
        print("2. Display Inventory B")
        print("3. Add Product to A")
        print("4. Delete Product from A")
        print("5. Update Stock in A")
        print("6. Merge Inventories")
        print("7. Compare Inventories")
        print("8. Exit")

        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                inventory_a.display_inventory()

            elif choice == "2":
                inventory_b.display_inventory()

            elif choice == "3":
                product_id = input("Product ID: ").strip()
                name = input("Product name: ").strip()
                stock = int(input("Stock: "))
                purchase = float(input("Purchase price: "))
                selling = float(input("Selling price: "))

                if not product_id or not name:
                    print("ID and name are required.")
                elif stock < 0 or purchase < 0 or selling < 0:
                    print("Stock and prices cannot be negative.")
                else:
                    inventory_a.add_product(
                        Product(product_id, name, stock, purchase, selling)
                    )

            elif choice == "4":
                product_id = input("Product ID to delete: ").strip()
                inventory_a.delete_product(product_id)

            elif choice == "5":
                product_id = input("Product ID: ").strip()
                quantity = int(input("Stock change (+/-): "))
                inventory_a.update_stock(product_id, quantity)

            elif choice == "6":
                merged = inventory_a + inventory_b
                print("\nMerged Inventory:")
                merged.display_inventory()

            elif choice == "7":
                if inventory_a < inventory_b:
                    print("Inventory A has lower purchase value.")
                elif inventory_b < inventory_a:
                    print("Inventory B has lower purchase value.")
                else:
                    print("Both inventories have equal purchase value.")

            elif choice == "8":
                print("Program ended.")
                break

            else:
                print("Invalid choice.")

        except ValueError as error:
            print("Input error:", error)


if __name__ == "__main__":
    main()
