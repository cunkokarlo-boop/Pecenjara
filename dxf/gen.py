"""Generira DXF datoteke za lasersko rezanje dijelova plinskog ražnja (izvedba s 4 IR plamenika).
Sve mjere u mm. Ishodište (0,0) je donji lijevi kut svakog dijela.
Slojevi: REZ (konture za rezanje), SAVIJANJE (linije savijanja, NE rezati)."""
import json, math, os, sys
import ezdxf

P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "postavke.json"), encoding="utf-8"))

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CUT, BEND = "REZ", "SAVIJANJE"
parts = []   # (datoteka, naziv, materijal, kom, napomena, dužina reza mm, broj probijanja)


def new_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.layers.add(CUT, color=1)
    doc.layers.add(BEND, color=5, linetype="DASHED")
    return doc


class Part:
    def __init__(self, fname, name, mat, qty, note=""):
        self.doc = new_doc(); self.msp = self.doc.modelspace()
        self.fname, self.name, self.mat, self.qty, self.note = fname, name, mat, qty, note
        self.cut_len = 0.0; self.pierces = 0

    def poly(self, pts):
        self.msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": CUT})
        self.cut_len += sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))
        self.pierces += 1

    def rect(self, x, y, w, h):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])

    def rect_c(self, cx, cy, w, h):
        self.rect(cx - w / 2, cy - h / 2, w, h)

    def circle(self, cx, cy, d):
        self.msp.add_circle((cx, cy), d / 2, dxfattribs={"layer": CUT})
        self.cut_len += math.pi * d; self.pierces += 1

    def obround(self, x1, x2, cy, h):
        """Vodoravni duguljasti utor od x1 do x2 (krajnje točke), visine h, zaobljeni krajevi."""
        r = h / 2; a, b = x1 + r, x2 - r
        # bulge = 1 → polukrug
        pts = [(a, cy - r, 0, 0, 0), (b, cy - r, 0, 0, 1), (b, cy + r, 0, 0, 0), (a, cy + r, 0, 0, 1)]
        self.msp.add_lwpolyline(pts, format="xyseb", close=True, dxfattribs={"layer": CUT})
        self.cut_len += 2 * (b - a) + math.pi * h; self.pierces += 1

    def outline_bulge(self, pts):
        """Zatvorena kontura s lukovima, točke (x, y, bulge)."""
        self.msp.add_lwpolyline([(x, y, 0, 0, bg) for x, y, bg in pts], format="xyseb", close=True, dxfattribs={"layer": CUT})
        L = 0
        n = len(pts)
        for i in range(n):
            x1, y1, bg = pts[i]; x2, y2, _ = pts[(i + 1) % n]
            c = math.dist((x1, y1), (x2, y2))
            if bg == 0: L += c
            else:
                th = 4 * math.atan(abs(bg)); r = c / (2 * math.sin(th / 2)); L += r * th
        self.cut_len += L; self.pierces += 1

    def bend(self, x1, y1, x2, y2):
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": BEND})

    def save(self):
        self.doc.saveas(os.path.join(OUT, self.fname))
        parts.append((self.fname, self.name, self.mat, self.qty, self.note, self.cut_len, self.pierces))


# Osi plamenika (od lijevog ruba kućišta 1100 mm) i visina osi ražnja od dna kućišta
BURNER_X = P["plamenik_osi_x"]
AXIS_Y = P["os_raznja_y"]

# 01 Stražnji zid, vanjski 1100 × 700, 2 mm
p = Part("01_strazni_zid_vanjski_1100x700_2mm.dxf", "Stražnji zid, vanjski", "crni lim 2 mm", 1,
         "Rupe za plamenike PROVJERITI prema stvarnom plameniku prije rezanja.")
p.rect(0, 0, 1100, 700)
for cx in BURNER_X:
    for dx in (-P["plamenik_rupe_m6_dx"], P["plamenik_rupe_m6_dx"]):
        for dy in (-P["plamenik_rupe_m6_dy"], P["plamenik_rupe_m6_dy"]):
            p.circle(cx + dx, AXIS_Y + dy, P["rupa_m6"])      # M6 za kućište plamenika
    p.circle(cx + P["cijev_pomak"][0], AXIS_Y + P["cijev_pomak"][1], P["rupa_cijev"])                    # prolaz bakrene cijevi Ø8 (s holenderom)
    p.circle(cx + P["termoelement_pomak"][0], AXIS_Y + P["termoelement_pomak"][1], P["rupa_termoelement"])                # prolaz termoelementa
p.save()

# 02 Stražnji zid, unutarnji 1060 × 660, 2 mm, 4 izreza 176 × 131
p = Part("02_strazni_zid_unutarnji_1060x660_2mm.dxf", "Stražnji zid, unutarnji (4 izreza za plamenike)", "crni lim 2 mm", 1,
         "Izrezi 176 × 131 = 175 × 130 + zazor. Provjeriti prema plameniku.")
p.rect(0, 0, 1060, 660)
for cx in BURNER_X:
    p.rect_c(cx + P["izrez_pomak"][0], AXIS_Y + P["izrez_pomak"][1], *P["izrez_plamenika"])
p.save()

# 03 Bočna stranica 500 × 700, 2 mm, 2 kom (drugi okrenuti = zrcalno)
p = Part("03_bocna_stranica_500x700_2mm.dxf", "Bočna stranica s utorom za ražanj", "crni lim 2 mm", 2,
         "Isti dio 2 kom; desni se montira okrenut (zrcalno). Lijevi rub (x=0) je uz stražnji zid.")
p.rect(0, 0, 500, 700)
p.obround(P["utor_stranice"][0], P["utor_stranice"][1], AXIS_Y, P["utor_stranice"][2])                     # utor za ražanj, kvadrat 16 (dijagonala 22,6) slobodno prolazi
p.save()

# 04 Vanjski nosač ražnja 210 × 80, 3 mm, 2 kom, 3 U-utora
p = Part("04_nosac_raznja_210x80_3mm.dxf", "Vanjski nosač ražnja s 3 utora", "crni lim 3 mm", 2,
         "U-utori širine 24 mm s dnom R12 (kvadrat 16 se okreće, dijagonala 22,6). Montaža izvana na bočnu stranicu: lijevi rub nosača 230 mm od stražnjeg ruba stranice, gornji rub nosača 360 mm od dna stranice (os ražnja na 350). Zavariti ili privijčiti.")
W, H, R = 210, 80, P["utor_nosaca_sirina"] / 2
D = P["utor_nosaca_dubina"]
pts = [(0, 0, 0), (W, 0, 0), (W, H, 0)]
for sx in sorted(P["utori_nosaca_x"], reverse=True):                          # utori s desna na lijevo (gornji rub)
    pts += [(sx + R, H, 0), (sx + R, H - D + R, -1), (sx - R, H - D + R, 0), (sx - R, H, 0)]
pts += [(0, H, 0)]
p.outline_bulge(pts)
p.circle(25, 20, 6.5); p.circle(185, 20, 6.5)
p.save()

# 05 Krov 1150 × 660, 2 mm, 1 savijanje 90° (prednji rub 100 mm)
p = Part("05_krov_1150x660_2mm.dxf", "Krov s prednjim rubom", "crni lim 2 mm", 1, "Savijanje 90° na 100 mm od prednjeg ruba (y=100).")
p.rect(0, 0, 1150, 660)
p.bend(0, 100, 1150, 100)
p.save()

# 06 Upravljačka letva 500 × 180, 2 mm, 2 savijanja
p = Part("06_upravljacka_letva_500x180_2mm.dxf", "Upravljačka letva (4 ventila + piezo)", "crni lim 2 mm", 1,
         "Savijanja 90° na y=30 i y=150. Rupe Ø12 za osovine ventila i Ø17 za piezo PROVJERITI prema kupljenim dijelovima.")
p.rect(0, 0, 500, 180)
for x in P["ventili_x"]:
    p.circle(x, P["letva_rupe_y"], P["ventil_rupa"])
p.circle(P["piezo_x"], P["letva_rupe_y"], P["piezo_rupa"])
for x in (30, 250, 470):
    p.circle(x, 15, 6.5); p.circle(x, 165, 6.5)
p.bend(0, 30, 500, 30); p.bend(0, 150, 500, 150)
p.save()

# 07 Nosač (kutnik) 80 × 60, 2 mm, 8 kom
p = Part("07_nosac_kutnik_80x60_2mm.dxf", "Nosač / kutnik za montažu", "crni lim 2 mm", 8, "Savijanje 90° na y=30.")
p.rect(0, 0, 80, 60)
for x in (20, 60):
    p.circle(x, 15, 6.5); p.circle(x, 45, 6.5)
p.bend(0, 30, 80, 30)
p.save()

# 08 Nosač motora 150 × 150, 3 mm
p = Part("08_nosac_motora_150x150_3mm.dxf", "Nosač motora (utor za krak protiv okretanja)", "crni lim 3 mm", 1,
         "Utor 20 × 80 za krak motora. Provjeriti prema motoru.")
p.rect(0, 0, 150, 150)
p.obround(*P["motor_utor"])
for x in P["motor_rupe_xy"]:
    for y in P["motor_rupe_xy"]:
        p.circle(x, y, P["motor_rupa"])
p.save()

# 09 Glava vilice 70 × 50, 8 mm, 2 kom
p = Part("09_glava_vilice_70x50_8mm.dxf", "Glava vilice", "crni lim ili inox 8 mm", 2,
         "Kvadratna rupa 16,5 za ražanj 16. Rupe Ø8,2 za šiljke. Rupu M8 za vijak za stezanje izbušiti i narezati sa strane.")
p.rect(0, 0, 70, 50)
p.rect_c(35, 25, 16.5, 16.5)
p.circle(13, 25, 8.2); p.circle(57, 25, 8.2)
p.save()

# 10 Tava za mast, razvijena 1130 × 530, inox 1 mm
p = Part("10_tava_razvijena_1130x530_inox1mm.dxf", "Tava za mast (razvijena)", "inox 1 mm", 1,
         "Dno 1050 × 450, stranice 40. Savijanja 90° na 4 linije. Kutove zavariti (TIG) ili zakovati i zabrtviti.")
F = 40; Wt, Ht = 1050 + 2 * F, 450 + 2 * F
p.poly([(F, 0), (Wt - F, 0), (Wt - F, F), (Wt, F), (Wt, Ht - F), (Wt - F, Ht - F), (Wt - F, Ht),
        (F, Ht), (F, Ht - F), (0, Ht - F), (0, F), (F, F)])
p.bend(F, F, Wt - F, F); p.bend(F, Ht - F, Wt - F, Ht - F)
p.bend(F, F, F, Ht - F); p.bend(Wt - F, F, Wt - F, Ht - F)
p.save()

# popis
tot_len = sum(x[5] * x[3] for x in parts) / 1000
tot_p = sum(x[6] * x[3] for x in parts)
with open(os.path.join(OUT, "00_POPIS_DIJELOVA.txt"), "w", encoding="utf-8") as f:
    f.write("PLINSKI RAŽANJ ZA ODOJKA – dijelovi za lasersko rezanje\n")
    f.write("Mjere u mm. Sloj REZ = rezati, sloj SAVIJANJE = linija savijanja (ne rezati).\n\n")
    for fn, name, mat, q, note, L, pc in parts:
        f.write(f"{fn}\n  {name} | {mat} | {q} kom | rez {L/1000:.2f} m/kom, {pc} probijanja/kom\n")
        if note: f.write(f"  Napomena: {note}\n")
        f.write("\n")
    f.write(f"UKUPNO: ~{tot_len:.1f} m reza, ~{tot_p} probijanja (sve količine)\n\n")
    f.write("Tolerancije: opće ±0,2 mm. Bez skošenja rubova. Ukloniti srh.\n")
    f.write("Savijanja (krov, letva, kutnici, tava) rade se na abkantu nakon rezanja.\n")
print(f"{len(parts)} dijelova, ~{tot_len:.1f} m reza, {tot_p} probijanja")
