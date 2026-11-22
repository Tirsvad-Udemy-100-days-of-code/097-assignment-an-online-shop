[English](Step-03-Registration-and-Login) · **Dansk** · [Bahasa Malaysia](Step-03-Registration-and-Login-ms)

# Trin 3: Registrering og login

Besøgende kan nu registrere sig, logge ind og logge ud, og butikken har en admin-rolle.

![Trin 3](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-03.png)

## Hashing af adgangskoder

En adgangskode gemmes aldrig. Butikken gemmer en saltet `scrypt`-hash lavet med `hashlib.scrypt` på formen `scrypt$n$r$p$salt$key`. Omkostningsparametrene ligger i selve hashen, så de kan hæves senere uden at gamle konti går i stykker. Kontrol af en adgangskode sammenligner hashes med `hmac.compare_digest`, som tager samme tid, uanset om de er ens. Er e-mailen ukendt, hasher butikken alligevel mod en dummy-hash, og begge fejl viser én besked, så en angriber ikke kan se, hvad der var forkert.

## Sessioner

Flasks signerede sessionscookie holder brugeren logget ind. Den er `HttpOnly`, så scripts ikke kan læse den, `SameSite=Lax`, og den udløber efter syv dage. Nøglen kommer fra `SHOP_SECRET_KEY`. Login rydder den gamle session først, så et session-id sat før login aldrig genbruges (session fixation).

## CSRF

Hver formular har et skjult `csrf_token`. En forespørgsel, der ændrer tilstand (POST, PUT, PATCH, DELETE), uden det rette token afvises med 403. Logout er også en POST af samme grund. Efter login følger butikken kun en `next`-adresse, der er en lokal sti, så et link ikke kan sende en bruger til et andet websted.

## Admin

Admin-kontoen oprettes ved start fra `SHOP_ADMIN_EMAIL` og `SHOP_ADMIN_PASSWORD`; der er ingen standardadgangskode i koden. `/admin` sender besøgende, der ikke er logget ind, til loginsiden, svarer 403 til kunder og viser siden til admin.

## Det lærte jeg

- Hash med en langsom, saltet funktion og sammenlign i konstant tid.
- Den samme fejl ved enhver mislykket login giver en angriber mindre at arbejde med.
- En sikkerhedsregel som én vagt, som alle forespørgsler passerer, er lettere at teste end et tjek på hver side.
