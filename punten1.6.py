"""
Atletiek punten v1.6
- v1.0: Competitie (MANNEN) + Meerkamp (M/V)
- v1.1: Competitie (VROUWEN) incl. piecewise hoog
- v1.3: U14/U16 (J/M gelijk) incl. piecewise hoog & ver
- v1.5: U14/U16 samengevoegd tot één categorie + 2 regels voor 60m horden
- v1.6: NIEUW: U8/U9/U10/U12 – COMPETITIE (J/M gelijk)
        • Lopen:               P = int(A / tijd - B)
        • Werpen/Springen:     P = int(A * sqrt(afstand_m) - B)
        • Piecewise U8–U12:
            - Verspringen:  d > 4.41 → int(A*sqrt(d) - B)  (A=887.99, B=1264.5)
                             d ≤ 4.41 → int((d - 1.91)*200 + 100.5)
            - Hoogspringen: h > 1.35 → int(A*sqrt(h) - B)  (A=1977.53, B=1698.5)
                             h ≤ 1.35 → int((h - 0.67)*733.33333 + 100.7)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Literal, Union
import math

# ---------- Types ----------
Gender = Literal["men", "women"]
UnitKind = Literal["time", "distance_m", "distance_cm"]
FormulaKind = Literal["track", "field"]

@dataclass(frozen=True)
class EventCoeff:
    A: float
    B: float
    C: float
    unit: UnitKind
    formula: FormulaKind

# ===========================
# Meerkamp tabellen (ongewijzigd)
# ===========================
MEN_DECATHLON: Dict[str, EventCoeff] = {
    "60m": EventCoeff(58.01500, 11.5, 1.810, "time", "track"),
    "100m": EventCoeff(25.43470, 18.0, 1.810, "time", "track"),
    "200m": EventCoeff(5.84250, 38.0, 1.810, "time", "track"),
    "400m": EventCoeff(1.53775, 82.0, 1.810, "time", "track"),
    "1000m": EventCoeff(0.08713, 305.5, 1.850, "time", "track"),
    "1500m": EventCoeff(0.03768, 480.0, 1.850, "time", "track"),
    "60m_h": EventCoeff(20.51730, 15.5, 1.920, "time", "track"),
    "110m_h": EventCoeff(5.74352, 28.5, 1.920, "time", "track"),
    "hoog": EventCoeff(0.8465, 75.0, 1.42, "distance_cm", "field"),
    "polsstok": EventCoeff(0.2797, 100.0, 1.35, "distance_cm", "field"),
    "ver": EventCoeff(0.14354, 220.0, 1.40, "distance_cm", "field"),
    "kogel": EventCoeff(51.39, 1.5, 1.05, "distance_m", "field"),
    "discus": EventCoeff(12.91, 4.0, 1.10, "distance_m", "field"),
    "kogelslingeren": EventCoeff(13.0449, 7.0, 1.05, "distance_m", "field"),
    "speer": EventCoeff(10.14, 7.0, 1.08, "distance_m", "field"),
    "gewichtwerpen": EventCoeff(47.8338, 1.5, 1.05, "distance_m", "field"),
}
MEN_ORDER = list(MEN_DECATHLON.keys())

WOMEN_HEPTATHLON: Dict[str, EventCoeff] = {
    "60m": EventCoeff(46.08490, 13.0, 1.810, "time", "track"),
    "100m": EventCoeff(17.85700, 21.0, 1.810, "time", "track"),
    "200m": EventCoeff(4.99087, 42.5, 1.810, "time", "track"),
    "400m": EventCoeff(1.34285, 91.7, 1.810, "time", "track"),
    "800m": EventCoeff(0.11193, 254.0, 1.880, "time", "track"),
    "1000m": EventCoeff(0.07068, 337.0, 1.880, "time", "track"),
    "1500m": EventCoeff(0.02883, 535.0, 1.880, "time", "track"),
    "60m_h": EventCoeff(20.04790, 17.0, 1.835, "time", "track"),
    "100m_h": EventCoeff(9.23076, 26.7, 1.835, "time", "track"),
    "hoog": EventCoeff(1.84523, 75.0, 1.348, "distance_cm", "field"),
    "polsstok": EventCoeff(0.44125, 100.0, 1.35, "distance_cm", "field"),
    "ver": EventCoeff(0.188807, 210.0, 1.41, "distance_cm", "field"),
    "kogel": EventCoeff(56.0211, 1.5, 1.05, "distance_m", "field"),
    "discus": EventCoeff(12.3311, 3.0, 1.10, "distance_m", "field"),
    "kogelslingeren": EventCoeff(17.5458, 6.0, 1.05, "distance_m", "field"),
    "speer": EventCoeff(15.9803, 3.8, 1.04, "distance_m", "field"),
    "gewichtwerpen": EventCoeff(52.1403, 1.5, 1.05, "distance_m", "field"),
}
WOMEN_ORDER = list(WOMEN_HEPTATHLON.keys())

# ===========================
# COMPETITIE (mannen) v1.0
# ===========================
COMP_MEN_RUN: Dict[str, Tuple[float, float]] = {
    "35m": (12020.6, 1813.60), "40m": (13826.6, 1860.50), "50m": (16844.4, 1927.10),
    "60m": (19942.4, 1983.80), "100m": (29550.0, 1881.50), "150m": (38003.1, 1486.00),
    "200m": (52611.4, 1547.10), "300m": (81710.5, 1473.60), "400m": (111960.0, 1433.50),
    "600m": (181894.7, 1341.00), "800m": (248544.0, 1323.20), "1000m": (317523.3, 1285.00),
    "1500m": (489971.4, 1224.70), "3000m": (1077300.0, 1234.90), "5000m": (1786833.9, 1145.00),
    "3000m_steeple": (1048695.7, 1008.90), "2000m_steeple": (673418.4, 1001.10),
    "50m_h": (16606.5, 1504.50), "60m_h": (22564.2, 1795.00), "110m_h": (23955.3, 747.90),
    "400m_h": (96830.9, 912.80), "4x100m": (118175.1, 1880.65),
    "4x200m": (210287.2, 1545.10), "4x400m": (446880.0, 1429.25), "zwedse_est": (247800.0, 1126.00),
}
COMP_MEN_FIELD: Dict[str, Tuple[float, float]] = {
    "hoog": (2440.0, 2593.5), "polsstok": (1040.0, 1272.5), "ver": (1094.4, 2075.3),
    "hss": (762.9, 2074.5), "kogel": (462.5, 1001.8), "discus": (249.8, 893.5),
    "kogelslingeren": (197.3, 591.8), "speer": (190.2, 711.3), "gewichtwerpen": (333.5, 539.0),
}
COMP_MEN_ORDER = [
    "35m","40m","50m","60m","50m_h","60m_h","100m","150m","200m","300m","400m",
    "4x100m","4x200m","4x400m","zwedse_est","600m","800m","1000m","1500m","3000m","5000m",
    "110m_h","400m_h","2000m_steeple","3000m_steeple",
    "hoog","polsstok","ver","hss","kogel","discus","kogelslingeren","speer","gewichtwerpen",
]

# ===========================
# COMPETITIE (vrouwen) v1.1
# ===========================
COMP_WOMEN_RUN: Dict[str, Tuple[float, float]] = {
    "35m": (11844.40, 1684.00), "40m": (13289.00, 1592.50), "50m": (16234.10, 1623.70),
    "60m": (19268.70, 1631.80), "100m": (30672.00, 1682.50), "150m": (40288.40, 1330.00),
    "200m": (54720.00, 1342.00), "300m": (90616.40, 1307.00), "400m": (111720.00, 1084.50),
    "600m": (175609.80, 964.10), "800m": (247200.00, 975.50), "1000m": (335842.30, 1034.40),
    "1500m": (557448.00, 1181.50), "3000m": (1197450.00, 1176.00),
    "3000m_steeple": (1161602.60, 926.20), "2000m_steeple": (822635.40, 1118.60),
    "50m_h": (15999.80, 1211.00), "60m_h": (18477.90, 1161.00), "100m_h": (24672.00, 895.50),
    "400m_h": (112752.00, 925.70), "4x100m": (122328.00, 1677.75),
    "4x200m": (218613.30, 1340.60), "4x400m": (446803.85, 1084.35), "zwedse_est": (261981.50, 865.00),
}
COMP_WOMEN_FIELD: Dict[str, Tuple[float, float]] = {
    "polsstok": (1225.8, 1500.2), "ver": (1076.3, 1729.4), "hss": (750.3, 1730.6),
    "kogel": (429.5, 768.3), "discus": (224.8, 686.5), "kogelslingeren": (183.5, 415.7),
    "speer": (197.5, 482.5), "gewichtwerpen": (309.4, 440.0),
}
COMP_WOMEN_HOOG_THRESH = 1.40
COMP_WOMEN_HOOG_LEQ = (3039.8, 2981.5)
COMP_WOMEN_HOOG_GT  = (2635.6, 2501.5)
COMP_WOMEN_ORDER = [
    "35m","40m","50m","60m","50m_h","60m_h","100m","100m_h","150m","200m","300m","400m","400m_h",
    "4x100m","4x200m","4x400m","zwedse_est","600m","800m","1000m","1500m","3000m","2000m_steeple","3000m_steeple",
    "hoog","polsstok","ver","hss","kogel","discus","kogelslingeren","speer","gewichtwerpen",
]

# ===========================
# U14/U16 – één categorie (zoals v1.5)
# ===========================
U1416_RUN: Dict[str, Tuple[float, float]] = {
    "30m": (8532.0, 1035.00), "35m": (9710.0, 1073.00), "40m": (10834.0, 1096.00),
    "50m": (13090.0, 1141.50), "60m": (15365.0, 1158.00), "80m": (19933.0, 1193.00),
    "100m": (24450.0, 1212.00), "150m": (36380.0, 1200.00), "300m": (78286.0, 1204.00),
    "600m": (160470.5, 911.35), "800m": (216604.8, 884.50), "1000m": (276912.0, 838.50),
    "1500m": (425682.0, 788.50),
    "60m_h_76c": (14050.0, 795.50), "60m_h_84c": (13820.0, 714.50),
    "4x40m": (41050.0, 1053.00), "4x60m": (59225.0, 1130.00),
    "4x80m": (77325.0, 1168.00), "4x100m": (95150.0, 1189.50),
}
U1416_FIELD: Dict[str, Tuple[float, float]] = {
    "polsstok": (795.66, 686.5), "kogel": (303.73, 437.5),
    "discus": (166.79, 438.5), "speer": (170.39, 437.5),
}
U1416_VER_THRESH = 4.41
U1416_HOOG_THRESH = 1.35
U1416_VER_GT = (887.99, 1364.5)
U1416_HOOG_GT = (1977.53, 1798.5)
U1416_ORDER = [
    "30m","35m","40m","50m","60m","80m","100m","150m","300m",
    "600m","800m","1000m","1500m",
    "60m_h_76c","60m_h_84c","4x40m","4x60m","4x80m","4x100m",
    "hoog","polsstok","ver","kogel","discus","speer",
]

# ===========================
# U8/U9/U10/U12 – NIEUW (v1.6, J/M gelijk)
# ===========================
# Lopen / estafettes
U8U12_RUN: Dict[str, Tuple[float, float]] = {
    "30m": (8532.0, 935.00),
    "35m": (9710.0, 973.00),
    "40m": (10834.0, 996.00),
    "50m": (13090.0, 1041.50),
    "60m": (15365.0, 1058.00),
    "600m": (160470.5, 811.35),
    "1000m": (276912.0, 738.50),
    "4x40m": (41050.0, 953.00),
    "4x60m": (59225.0, 1030.00),
}
# Springen/Werpen (incl. piecewise voor hoog & ver)
U8U12_FIELD: Dict[str, Tuple[float, float]] = {
    "kogel": (303.73, 337.5),
    "bal": (126.00, 245.5),  # Balwerpen
}
U8U12_VER_THRESH = 4.41
U8U12_HOOG_THRESH = 1.35
U8U12_VER_GT = (887.99, 1264.5)     # d > 4.41
U8U12_HOOG_GT = (1977.53, 1698.5)   # h > 1.35

U8U12_ORDER = [
    # lopen / estafettes
    "30m","35m","40m","50m","60m","600m","1000m","4x40m","4x60m",
    # springen / werpen
    "hoog","ver","kogel","bal",
]

# ===========================
# Helpers
# ===========================
def parse_time(value: Union[str, float, int]) -> float:
    """Parse 'm:ss.xx' of seconden → float seconden."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            m, sec = parts
            return float(m) * 60.0 + float(sec)
        if len(parts) == 3:
            h, m, sec = parts
            return float(h) * 3600.0 + float(m) * 60.0 + float(sec)
    return float(s)

def to_unit(value: Union[str, float, int], unit: UnitKind) -> float:
    if unit == "time":
        return parse_time(value)
    v = float(value)
    if unit == "distance_cm":
        return v * 100.0
    return v

# ---------- Meerkamp ----------
def score_event_meerkamp(event_key: str, perf: Union[str, float, int], gender: Gender) -> int:
    coeffs = MEN_DECATHLON if gender == "men" else WOMEN_HEPTATHLON
    e = coeffs[event_key]
    x = to_unit(perf, e.unit)
    value = e.A * pow(e.B - x, e.C) if e.formula == "track" else e.A * pow(x - e.B, e.C)
    return max(0, int(value))

# ---------- Competitie (mannen) ----------
def score_event_comp_men(event_key: str, perf: Union[str, float, int]) -> int:
    if event_key in COMP_MEN_RUN:
        A, B = COMP_MEN_RUN[event_key]
        t = parse_time(perf)
        return max(0, int((A / t) - B))
    if event_key in COMP_MEN_FIELD:
        A, B = COMP_MEN_FIELD[event_key]
        d = float(perf)
        return max(0, int((A * math.sqrt(d)) - B))
    return 0

# ---------- Competitie (vrouwen) ----------
def score_event_comp_women(event_key: str, perf: Union[str, float, int]) -> int:
    if event_key in COMP_WOMEN_RUN:
        A, B = COMP_WOMEN_RUN[event_key]
        t = parse_time(perf)
        return max(0, int((A / t) - B))
    if event_key == "hoog":
        d = float(perf)
        if d <= COMP_WOMEN_HOOG_THRESH:
            A, B = COMP_WOMEN_HOOG_LEQ
        else:
            A, B = COMP_WOMEN_HOOG_GT
        return max(0, int((A * math.sqrt(d)) - B))
    if event_key in COMP_WOMEN_FIELD:
        A, B = COMP_WOMEN_FIELD[event_key]
        d = float(perf)
        return max(0, int((A * math.sqrt(d)) - B))
    return 0

# ---------- U14/U16 ----------
def score_event_u1416(event_key: str, perf: Union[str, float, int]) -> int:
    if event_key in U1416_RUN:
        A, B = U1416_RUN[event_key]
        t = parse_time(perf)
        return max(0, int((A / t) - B))
    if event_key == "ver":
        d = float(perf)
        if d > U1416_VER_THRESH:
            A, B = U1416_VER_GT
            return max(0, int((A * math.sqrt(d)) - B))
        else:
            return max(0, int(((d - 1.91) * 200.0) + 0.5))
    if event_key == "hoog":
        h = float(perf)
        if h > U1416_HOOG_THRESH:
            A, B = U1416_HOOG_GT
            return max(0, int((A * math.sqrt(h)) - B))
        else:
            return max(0, int(((h - 0.67) * 733.33333) + 0.7))
    if event_key in U1416_FIELD:
        A, B = U1416_FIELD[event_key]
        d = float(perf)
        return max(0, int((A * math.sqrt(d)) - B))
    return 0

# ---------- U8/U9/U10/U12 ----------
def score_event_u8u12(event_key: str, perf: Union[str, float, int]) -> int:
    # Lopen / estafettes
    if event_key in U8U12_RUN:
        A, B = U8U12_RUN[event_key]
        t = parse_time(perf)
        return max(0, int((A / t) - B))
    # Piecewise verspringen
    if event_key == "ver":
        d = float(perf)
        if d > U8U12_VER_THRESH:
            A, B = U8U12_VER_GT
            return max(0, int((A * math.sqrt(d)) - B))
        else:
            return max(0, int(((d - 1.91) * 200.0) + 100.5))
    # Piecewise hoogspringen
    if event_key == "hoog":
        h = float(perf)
        if h > U8U12_HOOG_THRESH:
            A, B = U8U12_HOOG_GT
            return max(0, int((A * math.sqrt(h)) - B))
        else:
            return max(0, int(((h - 0.67) * 733.33333) + 100.7))
    # Overige werp/spring
    if event_key in U8U12_FIELD:
        A, B = U8U12_FIELD[event_key]
        d = float(perf)
        return max(0, int((A * math.sqrt(d)) - B))
    return 0

def total_score(perfs: Dict[str, Union[str, float, int]], category: str) -> Tuple[int, Dict[str, int]]:
    details: Dict[str, int] = {}
    if category == "Sen Man Meerkamp":
        for k in MEN_ORDER:
            if k in perfs:
                details[k] = score_event_meerkamp(k, perfs[k], "men")
    elif category == "Sen Vrouw Meerkamp":
        for k in WOMEN_ORDER:
            if k in perfs:
                details[k] = score_event_meerkamp(k, perfs[k], "women")
    elif category == "MANNEN Masters, Sen, U20, U18- COMPETITIE":
        for k in COMP_MEN_ORDER:
            if k in perfs:
                details[k] = score_event_comp_men(k, perfs[k])
    elif category == "VROUWEN Masters, Sen, U20, U18- COMPETITIE":
        for k in COMP_WOMEN_ORDER:
            if k in perfs:
                details[k] = score_event_comp_women(k, perfs[k])
    elif category == "U14/U16 - COMPETITIE":
        for k in U1416_ORDER:
            if k in perfs:
                details[k] = score_event_u1416(k, perfs[k])
    elif category == "U8/U9/U10/U12 - COMPETITIE":
        for k in U8U12_ORDER:
            if k in perfs:
                details[k] = score_event_u8u12(k, perfs[k])
    return sum(details.values()), details

# ===========================
# UI (Streamlit) — 2 kolommen: Onderdeel & Prestatie
# ===========================
try:
    import streamlit as st
    import pandas as pd
except Exception:
    st = None

_NL_NAMES = {
    # algemene
    "60m": "60 meter", "100m": "100 meter", "200m": "200 meter", "400m": "400 meter",
    "800m": "800 meter", "1000m": "1000 meter", "1500m": "1500 meter",
    "60m_h": "60 meter horden", "100m_h": "100 meter horden", "110m_h": "110 meter horden",
    "hoog": "Hoogspringen", "ver": "Verspringen", "polsstok": "Polsstokhoogspringen",
    "kogel": "Kogelstoten", "discus": "Discuswerpen", "kogelslingeren": "Kogelslingeren",
    "speer": "Speerwerpen", "gewichtwerpen": "Gewichtwerpen",
    "35m": "35 meter", "40m": "40 meter", "50m": "50 meter", "300m": "300 meter",
    "4x100m": "4 × 100 meter", "4x200m": "4 × 200 meter", "4x400m": "4 × 400 meter",
    "zwedse_est": "Zweedse estafette", "hss": "Hink-stapspringen",
    "2000m_steeple": "2000 meter steeplechase", "3000m_steeple": "3000 meter steeplechase",
    # U14/U16 & U8–U12 labels
    "30m": "30 meter", "80m": "80 meter", "4x40m": "4 × 40 meter", "4x60m": "4 × 60 meter",
    "4x80m": "4 × 80 meter",
    "60m_h_76c": "60 m horden (76,2 cm)",
    "60m_h_84c": "60 m horden (84 cm)",
    "bal": "Balwerpen",
}

if st is not None:
    st.set_page_config(page_title="Meerkamp & Competitie punten – v1.6", page_icon="🏃", layout="centered")
    st.title("🏃 Puntenberekening: Meerkamp & Competitie")

    categories = [
        "Sen Man Meerkamp",
        "Sen Vrouw Meerkamp",
        "MANNEN Masters, Sen, U20, U18- COMPETITIE",
        "VROUWEN Masters, Sen, U20, U18- COMPETITIE",
        "U14/U16 - COMPETITIE",
        "U8/U9/U10/U12 - COMPETITIE",
    ]
    cat = st.selectbox("Categorie", categories, index=5)

    if cat == "Sen Man Meerkamp":
        order_keys = MEN_ORDER
    elif cat == "Sen Vrouw Meerkamp":
        order_keys = WOMEN_ORDER
    elif cat == "MANNEN Masters, Sen, U20, U18- COMPETITIE":
        order_keys = COMP_MEN_ORDER
    elif cat == "VROUWEN Masters, Sen, U20, U18- COMPETITIE":
        order_keys = COMP_WOMEN_ORDER
    elif cat == "U14/U16 - COMPETITIE":
        order_keys = U1416_ORDER
    else:
        order_keys = U8U12_ORDER

    display_names = [_NL_NAMES.get(k, k) for k in order_keys]
    df = pd.DataFrame({"Onderdeel": display_names, "Prestatie": [""] * len(order_keys)})

    st.caption("Tijden in seconden (of m:ss.xx). Afstanden in meters; bij competitie springen/werpen wordt √afstand gebruikt.")
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Onderdeel": st.column_config.TextColumn(disabled=True, width="large"),
            "Prestatie": st.column_config.TextColumn(width="medium"),
        },
    )

    punten, totaal = [], 0
    for idx, row in edited.iterrows():
        key = order_keys[idx]
        perf = str(row["Prestatie"]).strip()
        if not perf:
            pts = 0
        else:
            try:
                if cat == "Sen Man Meerkamp":
                    pts = score_event_meerkamp(key, perf, "men")
                elif cat == "Sen Vrouw Meerkamp":
                    pts = score_event_meerkamp(key, perf, "women")
                elif cat == "MANNEN Masters, Sen, U20, U18- COMPETITIE":
                    pts = score_event_comp_men(key, perf)
                elif cat == "VROUWEN Masters, Sen, U20, U18- COMPETITIE":
                    pts = score_event_comp_women(key, perf)
                elif cat == "U14/U16 - COMPETITIE":
                    pts = score_event_u1416(key, perf)
                else:
                    pts = score_event_u8u12(key, perf)
            except Exception:
                pts = 0
        punten.append(pts)
        totaal += pts

    out_df = edited.copy()
    out_df["Punten"] = punten
    st.dataframe(out_df, hide_index=True, use_container_width=True)

    st.markdown("<hr style='margin-top:6px;margin-bottom:6px'>", unsafe_allow_html=True)
    st.metric("Totaal aantal punten", int(totaal))
