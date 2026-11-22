[English](Step-01-Project-Foundation) · **Dansk** · [Bahasa Malaysia](Step-01-Project-Foundation-ms)

# Trin 1: Projektets fundament

Det første trin bygger ikke noget, kunden kan bruge endnu. Det opsætter værktøjerne og strukturen, som alle senere trin bygger på, og serverer én side.

![Trin 1](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-01.png)

## Opsætning

- **Python 3.14 eller nyere.** `pyproject.toml` har en `dev`-gruppe: pytest, pytest-cov, ruff og mypy. Flask, den eneste direkte afhængighed ved kørsel, kom til i trin 2 (ADR-0002).
- **Et lokalt virtuelt miljø.** `python -m venv .venv`, aktivér det, kør derefter `python -m pip install --upgrade pip` og `python -m pip install -e ".[dev]"`. Miljøet holder projektets pakker adskilt fra systemets Python.
- **Kør butikken** med `python -m online_shop` og åbn http://127.0.0.1:8000/.

## Struktur

Koden i `src/online_shop/` har fire lag: `domain`, `application`, `infrastructure` og `presentation`. Afhængighederne peger indad, så forretningsreglerne aldrig importerer webserveren. Præsentationslaget følger MVC: en controller besvarer en forespørgsel, og en view bygger HTML.

## Konstanter

Hver værdi, som mere end ét sted bruger, står én gang i `src/online_shop/constants.py`: appens titel, vært, port, indholdstyper, statuskoder og fejlbeskeder. At ændre porten er at rette én linje.

## Kontrol

- `pytest` kører enheds- og integrationstest og fejler under 90 procent dækning.
- `python scripts/run_opengrep.py` scanner koden og må ikke finde noget af alvorlighed error før et push.
- Skærmbilledet tages af en headless browser i en Docker-container, aldrig på skrivebordet.

## Det lærte jeg

- Den første side blev serveret med `http.server` og en lille router; trin 2 erstattede dem med Flask, da det håndskrevne lag begyndte at vokse.
- Konstanter i ét modul og lag i hver sin mappe fra dag ét koster lidt og sparer omarbejde senere.
- En test, der starter den rigtige server på en ledig port, fanger fejl, som enhedstest overser.
