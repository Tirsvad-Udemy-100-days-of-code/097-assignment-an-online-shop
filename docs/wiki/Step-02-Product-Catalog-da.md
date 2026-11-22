[English](Step-02-Product-Catalog) · **Dansk** · [Bahasa Malaysia](Step-02-Product-Catalog-ms)

# Trin 2: Produktkatalog og lagring

Butikken gemmer nu produkter i SQLite og viser dem: et gitter på forsiden og en detaljeside for hvert produkt.

![Trin 2](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-02.png)

## Lagdeling

Laget `domain` har entiteten `Product`, værdien `Money` og porten `ProductRepository`. Laget `application` har use cases, der viser produkter og henter ét, og returnerer DTO'er. Laget `infrastructure` har SQLite-adapteren. Laget `presentation` tegner siderne. Importerne peger indad: domain og application importerer aldrig infrastructure eller presentation, så reglerne kan testes uden database og server.

## SQLite

Repositoriet bruger `sqlite3` fra standardbiblioteket. Skemaet oprettes ved start, og eksempelprodukterne indlæses, så data ligger i en fil og overlever en genstart. Forespørgsler bruger pladsholdere, aldrig strengformatering.

## Penge i cent

En pris er et helt antal mindste enheder (cent) i en `Money`-værdi, der afviser negative beløb. Kommatal kan ikke gengive de fleste decimalpriser præcist, så summer driver. Heltal lægges nøjagtigt sammen, og siden formaterer først cent som pris, når den tegner den.

## Det lærte jeg

- En port i domænet lader use cases køre mod et falsk repository i enhedstest.
- DTO'er holder entiteter ude af viewene.
- At escape alle databaseværdier, før de når HTML, er en regel for view-hjælperen og ikke for hver side.
