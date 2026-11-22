[English](Step-06-Order-Kanban-Board) · **Dansk** · [Bahasa Malaysia](Step-06-Order-Kanban-Board-ms)

# Trin 6: Kanban-tavle for ordrer

Butiksejeren følger hver betalt ordre på en Kanban-tavle, og hver kunde ser status på sine egne ordrer.

![Trin 6](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-06.png)

## Statusforløb

En ordre går gennem fem kolonner: **Needs confirmation**, **Confirmed**, **Being packed**, **Shipped** og **Delivered**. En betalt ordre starter sidst i den første kolonne. Ejeren trækker et kort til en anden kolonne, eller inden for en kolonne for at ændre dets plads, og butikken gemmer den nye status og position. Positionerne omnummereres i kilde- og målkolonnen i én transaktion, så rækkefølgen af kortene er den samme efter en genindlæsning.

## Tavlen

Tavlesiden er kun for admin: en besøgende, der ikke er logget ind, sendes til loginsiden, og en kunde får 403. Hvert kort viser ordrenummer, kundens e-mail, varerne og totalen. Siden bruger almindelig JavaScript og browserens egen træk-og-slip uden bibliotek. Et flyt vises med det samme og sendes derefter til butikken med CSRF-tokenet; afviser butikken det, springer kortet tilbage, og en besked vises. En select på hvert kort laver det samme flyt uden træk, til tastatur og telefon. Ved 400 pixels bredde ruller kolonnerne sidelæns.

## Genbrugt fra dag 89

Layoutet og træk-og-slip-ideen kommer fra dag 89-opgaven med todo-listen: lister blev til statuskolonner og kort blev til ordrer. Koden er skrevet om til denne butiks mørke tema og eget API.

## Kundens ordrehistorik

Siden Ordrer viser den indloggede kundes egne ordrer, nyeste først, med varer, total og et statusmærke.

## Test

En browsertest i en Docker-container trækker en ordre til Confirmed, genindlæser siden og tjekker, at den blev, og at en kunde ikke kan åbne tavlen.

## Det lærte jeg

- At gemme positionen og ikke kun status er det, der får et træk til at overleve en genindlæsning.
- At lave flyttet i én transaktion holder kolonnerne konsistente.
- En kontrol, der gør det samme uden træk, gør tavlen brugbar på telefon og med tastatur.
