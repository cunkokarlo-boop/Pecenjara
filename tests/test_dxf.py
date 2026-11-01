"""Testovi geometrije DXF dijelova pečenjare. Pokretanje: python -m pytest -q"""
import json, math, os, subprocess, sys, tempfile
import ezdxf
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "dxf", "postavke.json"), encoding="utf-8"))


@pytest.fixture(scope="module")
def out():
    d = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(ROOT, "dxf", "gen.py"), d], check=True)
    return d


def ents(out, name):
    f = [x for x in os.listdir(out) if x.startswith(name)][0]
    return ezdxf.readfile(os.path.join(out, f)).modelspace()


def test_svi_dijelovi_postoje(out):
    assert len([f for f in os.listdir(out) if f.endswith(".dxf")]) == 10


def test_jedinice_mm_i_slojevi(out):
    for f in os.listdir(out):
        if f.endswith(".dxf"):
            doc = ezdxf.readfile(os.path.join(out, f))
            assert doc.header["$INSUNITS"] == 4
            assert {e.dxf.layer for e in doc.modelspace()} <= {"REZ", "SAVIJANJE"}


def test_utor_nosaca_propusta_kvadrat_koji_se_okrece():
    # kvadrat 16 ima dijagonalu 22,6 mm; uz 1 mm zazora utor mora biti širi
    diag = P["raznj_kvadrat"] * math.sqrt(2)
    assert P["utor_nosaca_sirina"] >= diag + 1
    assert P["utor_stranice"][2] >= diag + 1


def test_izrezi_unutarnjeg_zida_poravnati_s_plamenicima(out):
    # unutarnji zid je 20 mm uvučen lijevo i dolje u odnosu na vanjski
    msp = ents(out, "02_")
    centers = sorted(
        round(sum(p[0] for p in e.get_points("xy")) / 4) for e in msp.query("LWPOLYLINE")
        if abs(max(p[0] for p in e.get_points("xy")) - min(p[0] for p in e.get_points("xy")) - P["izrez_plamenika"][0]) < 0.01)
    assert centers == [x - 20 for x in P["plamenik_osi_x"]]


def test_razmak_raznja_od_keramike_23_28_33_cm():
    # nosač počinje na z=-20 (od stražnjeg ruba kućišta 250 mm iza osi); keramika na z=-195
    dist = [x - 20 - (-195) for x in P["utori_nosaca_x"]]
    assert dist == [230, 280, 330]


def test_utor_stranice_pokriva_sve_polozaje_raznja():
    x1, x2, h = P["utor_stranice"]
    for x in P["utori_nosaca_x"]:
        z_panel = x - 20 + 250  # z osi ražnja u koordinatama bočne stranice
        assert x1 + h / 2 <= z_panel <= x2 - h / 2
