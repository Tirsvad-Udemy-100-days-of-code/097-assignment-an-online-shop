[English](Step-05-Stripe-Checkout) · **Dansk** · [Bahasa Malaysia](Step-05-Stripe-Checkout-ms)

# Trin 5: Stripe checkout

Kunden betaler gennem Stripe Checkout i testtilstand, og kun en betalt session opretter en ordre.

![Trin 5](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-05.png)

## Forløbet

1. Kurvsiden har en **Checkout**-knap. Den sender til butikken, som opretter en Checkout Session hos Stripe med én varelinje pr. kurvlinje og sender browseren til Stripes betalingsside.
2. Efter betalingen sender Stripe kunden tilbage til en succesadresse med session-id'et.
3. Butikken stoler ikke på adressen. Den spørger Stripe om sessionen og opretter kun en ordre, når Stripe siger, at den er betalt, og sessionen tilhører den bruger, der er logget ind. At åbne samme adresse to gange giver én ordre, fordi session-id'et er unikt.
4. Annullerer kunden, bevares kurven, og der oprettes ingen ordre.

En ny ordre har status "Needs confirmation". Kurven tømmes først, når ordren er gemt.

## En port og en falsk

Butikken taler med en `PaymentGateway`-port. Stripe-adapteren kalder REST-API'et med `urllib` og formkoder de indlejrede felter. Test bruger en falsk gateway og, til adapteren, en lille lokal server, der spiller Stripe, så ingen test rører netværket.

## Testtilstand og nøgler

Testnøglerne læses fra en lokal `stripe.env`-fil, som git ignorerer. Butikken afviser enhver nøgle, der ikke er en testnøgle. Nøgler udskrives, logges eller skrives aldrig i en fejlbesked, og uden filen læser butikken miljøvariablerne `PUBLISHABLE_KEY` og `SECRET_KEY`, eller starter, hvis ingen af delene findes, stadig med skjult Checkout-knap. I testtilstand betaler du med kortet `4242 4242 4242 4242`, en vilkårlig fremtidig dato og en vilkårlig CVC.

## Det lærte jeg

- Opret aldrig en ordre ud fra returadressen alene; spørg udbyderen, hvad der skete.
- Et unikt session-id gør succesiden sikker at genindlæse.
- En hemmelighed kræver tre regler: holdt ude af git, holdt ude af output og kontrolleret for den rette tilstand før brug.
