[English](Step-04-Shopping-Basket) · **Dansk** · [Bahasa Malaysia](Step-04-Shopping-Basket-ms)

# Trin 4: Indkøbskurv

En kunde, der er logget ind, kan nu samle produkter i en kurv, ændre antal, fjerne linjer og se totalen.

![Trin 4](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-04.png)

## Modellen

En `Basket` har `BasketLine`-værdier: et produkt-id og et antal. Kurven kopierer ikke prisen. Prisen læses fra produktet, når kurven vises, så en prisændring ses med det samme. Totalen er summen af pris gange antal i cent, beregnet i domænet med `Money`-værdien fra trin 2, så den er nøjagtig. Et antal har en grænse; sættes det til 0, fjernes linjen, og lægges samme produkt i kurven to gange, øges antallet på én linje i stedet for at lave to.

## Lagring

Kurven tilhører den bruger, der er logget ind, og gemmes i SQLite i to tabeller: én kurv pr. bruger og én række pr. produkt i den, unik pr. bruger og produkt. Den bevares efter logout og login. En besøgende, der ikke er logget ind, sendes til loginsiden, når vedkommende forsøger at lægge noget i kurven.

## Sider

Katalogkortene og produktsiden har hver en "læg i kurv"-formular med CSRF-tokenet fra trin 3. Kurvsiden viser linjerne med antalsfelter, knapper til opdatering og fjernelse og totalen. Headeren viser antallet af varer ved siden af kurvikonet.

## Det lærte jeg

- Gem kun det, der ikke kan udledes: et produkt-id og et antal. Prisen kommer fra produktet.
- At regne i hele cent ét sted holder totaler nøjagtige.
- Genbrug af CSRF-vagten og login-omdirigeringen betød, at kurven ikke krævede ny sikkerhedskode.
