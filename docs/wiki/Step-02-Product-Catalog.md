**English** · [Dansk](Step-02-Product-Catalog-da) · [Bahasa Malaysia](Step-02-Product-Catalog-ms)

# Step 2: Product catalog and storage

The shop now stores products in SQLite and shows them: a grid on the home page and a detail page for each product.

![Step 2](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-02.png)

## Layering

The `domain` layer holds the `Product` entity, the `Money` value and the `ProductRepository` port. The `application` layer holds the use cases that list products and fetch one, and returns DTOs. The `infrastructure` layer holds the SQLite adapter. The `presentation` layer renders the pages. Imports point inward: domain and application never import infrastructure or presentation, so the rules can be tested without a database or a server.

## SQLite

The repository uses `sqlite3` from the standard library. The schema is created on start and the sample products are seeded, so the data is in a file and survives a restart. Queries use placeholders, never string formatting.

## Money in cents

A price is a whole number of minor units (cents), held in a `Money` value that rejects negative amounts. Floating point numbers cannot represent most decimal prices exactly, so adding them drifts. Integers add exactly, and the page formats cents as a price only when it draws it.

## What I learned

- A port in the domain lets the use cases run against a fake repository in unit tests.
- DTOs keep entities out of the views.
- Escaping every database value before it reaches HTML is a rule for the view helper, not for each page.
