[English](Step-07-Reflection) · **Dansk** · [Bahasa Malaysia](Step-07-Reflection-ms)

# Trin 7: Refleksion

## Hvordan jeg greb projektet an

Jeg planlagde først. Business case, interessenter, projektplan og syv milepæle blev skrevet og gennemgået, før der var kode, og hver milepæl gik gennem én pull request med sin egen reviewpost. Koden ligger i fire lag (domæne, applikation, infrastruktur, præsentation), så butikkens regler ikke afhænger af Flask, SQLite eller Stripe, og de fleste af de 340 tests kører uden en browser. Jeg valgte en Kanban-tavle til ordrerne, fordi en ordre går gennem få tydelige trin: skal bekræftes, bekræftet, pakkes, afsendt og leveret. En tavle viser hele køen på et blik, så ejeren kan se, hvad der skal ske næste gang, og flytte en ordre videre med et træk.

## Hvad der var let

Domæneregler (penge i cent, kurven, ordrestatus) og SQLite-lagrene. Da portene først fandtes, gjorde falske implementeringer dem hurtige at teste.

## Hvad der var svært

Ordretavlen med træk og slip, der gemmer placeringer i databasen, og Stripe checkout, som skal testes uden rigtige nøgler eller rigtige betalinger. CI fangede også det, mine lokale kontroller missede: en falsk `sk_live_`-nøgle i en test udløste hemmelighedsscanningen, og SQL bygget med f-strenge udløste kodescanningen. Hver forespørgsel er en almindelig tekst med `?`-pladsholdere. Brugerinput rejser kun som en bundet værdi, aldrig inde i selve SQL-teksten. Scanningerne holder også øje med det.

## Hvordan jeg kan blive bedre til næste projekt

Køre de samme scanninger som CI før hver push, se på et rigtigt skærmbillede, så snart en side findes, og holde planen og koden i takt undervejs.

## Min største læring

En beslutning, der ændres midt i et projekt, her skiftet fra standardbiblioteket til Flask, er billigst, når den først skrives ned i en ADR og planen og først derefter kodes. En fejl som `site.update`, der viste en dict-metode i en skabelon, findes ved at se på et rigtigt skærmbillede, ikke med enhedstests.

## Hvad jeg ville gøre anderledes

Vælge framework før den første milepæl og skrive SQL som almindelig tekst med pladsholdere fra det første lager.
