# Pečenjara – plinski ražanj za odojka (Komadar)

Kućni plinski ražanj za odojka do ~25 kg: kutija 1100 × 500 × 700 mm, dvostruki stražnji zid,
4 keramička IR gyros plamenika (~3,2 kW, propan-butan 30 mbar), ražanj inox kvadrat 16 mm.

## Struktura
- `web/index.html` + `web/models.js` – stranica (Narudžba · 3D · Nacrt). Objavljena:
  https://claude.ai/artifact/4TDAndEmrF6mWfYAq93WEU (slug 1bf440d4-f3f6-4c56-b537-a3d92eac98b1)
- `dxf/postavke.json` – SVE izmjenjive mjere za DXF. Mijenjaj ovdje, ne u kodu.
- `dxf/gen.py` – generira 10 DXF dijelova + `00_POPIS_DIJELOVA.txt`.
- `dxf/preview.py` – slika pregleda svih dijelova.
- `dxf/izlaz/` – zadnji generirani DXF-ovi za laser.
- `tests/` – testovi geometrije (pytest).

## Naredbe
```
pip install ezdxf matplotlib pytest
python dxf/gen.py dxf/izlaz
python dxf/preview.py dxf/izlaz dxf/izlaz/00_PREGLED.png
python -m pytest -q tests
```
Automatika: GitHub Action `.github/workflows/dxf.yml` nakon svake izmjene `postavke.json`/`gen.py`/testova
pokrene testove, regenerira `dxf/izlaz/` i sama ga commita (ruka: Actions → Run workflow).
Komentari: tema https://github.com/cunkokarlo-boop/Pecenjara/issues/1 – `obavijest.yml` nakon svakog pusha na main
upiše popis promjena kao komentar (Karlo i prijatelj komentiraju ispod).
3D lokalno: `cd web && python -m http.server` (importmap s jsdelivr, three@0.160.0).

## Zaključano
- Slojevi DXF-a: `REZ` (rezati) i `SAVIJANJE` (ne rezati); jedinice mm ($INSUNITS=4).
- Utori za ražanj ≥ dijagonala kvadrata + 1 mm (test).
- Mjere plamenika, ventila i motora su PRETPOSTAVKA dok se ne izmjere kupljeni dijelovi.

Odluke: `ODLUKE.md`. Stanje: `STANJE.md`.
