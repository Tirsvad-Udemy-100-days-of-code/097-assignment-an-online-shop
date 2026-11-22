**English** · [Dansk](Step-04-Shopping-Basket-da) · [Bahasa Malaysia](Step-04-Shopping-Basket-ms)

# Step 4: Shopping basket

A signed-in shopper can now collect products in a basket, change the quantities, remove lines and see the total.

![Step 4](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-04.png)

## The model

A `Basket` holds `BasketLine` values: a product id and a quantity. The basket does not copy the price. The price is read from the product when the basket is shown, so a price change shows up at once. The total is the sum of price times quantity in cents, computed in the domain with the `Money` value from step 2, so it is exact. A quantity has a limit; setting it to 0 removes the line, and adding the same product twice increases the quantity of one line instead of making two.

## Storage

The basket belongs to the signed-in user and is stored in SQLite, in two tables: one basket per user and one row per product in it, unique per user and product. It is kept after logout and login. A visitor who is not signed in is sent to the login page when they try to add something.

## Pages

The catalog cards and the product page each have an "add to basket" form with the CSRF token from step 3. The basket page lists the lines with quantity inputs, update and remove buttons and the total. The header shows the number of items next to the cart icon.

## What I learned

- Store only what cannot be derived: a product id and a quantity. The price comes from the product.
- Doing the arithmetic in integer cents in one place keeps totals exact.
- Reusing the CSRF guard and the login redirect meant the basket needed no new security code.
