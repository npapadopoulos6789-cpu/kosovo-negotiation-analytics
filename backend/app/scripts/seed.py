"""
Seed script -- γεμίζει τη ΒΔ με τα δεδομένα της διπλωματικής.
Τρέχεται με: python -m app.scripts.seed

Όλες οι τιμές πεδίων (description, batna, red_lines, zopa/ripeness
reasoning, role_description, source) είναι στα αγγλικά, όπως το UI του
frontend -- μεταφρασμένες από το αρχικό ελληνικό κείμενο της διπλωματικής
χωρίς αλλαγή νοήματος/αριθμών/ημερομηνιών. Τα σχόλια αυτού του αρχείου
παραμένουν ελληνικά (dev-facing, όπως το CLAUDE.md).

ΠΗΓΕΣ:
- Economic (GDP growth, unemployment), Serbia: World Bank API, confidence=EXACT
- Military (% GDP δαπανών + απόλυτο USD), Serbia+Kosovo: World Bank API (πηγή SIPRI)
- FDI net inflows (% GDP), Serbia+Kosovo: World Bank API (BX.KLT.DINV.WD.GD.ZS),
  confidence=EXACT -- ΔΕΝ πρέπει να συγχέεται με το ξεχωριστό, ακόμα deferred
  `eu_fdi_share` (ποσοστό του ΣΥΝΟΛΙΚΟΥ FDI που είναι ευρωπαϊκό, από τη
  διπλωματική) -- διαφορετικό indicator_type/ερώτημα, βλ. FUTURE WORK παρακάτω
- Social (Freedom House score), Serbia+Kosovo: SEED_DATA_SPEC.md §2.4
  (Γράφημα 1.11 διπλωματικής), confidence=CHART_READ
- Kosovo unemployment (2005-2008): Γράφημα 1.5 διπλωματικής (ILO/WB, δεν
  καλύπτεται από το World Bank API για αυτή την περίοδο)
- Kosovo trade_share_eu (2018): Γράφημα 1.7 διπλωματικής (εισαγωγές)
- Serbia trade_share_eu (2023): Γράφημα 1.8 διπλωματικής

10 negotiation events (E1-E10) όπως περιγράφονται στο SEED_DATA_SPEC.md §3.
Per-event breakdown δρώντων/ρόλων: SEED_SOURCE.md.

Το Power Index ECONOMIC category συνδυάζει GDP_growth (ρυθμός μεταβολής,
πιάνει σοκ όπως το 1999), GDP_absolute_usd σε λογαριθμική κλίμακα (μέγεθος
οικονομίας), unemployment_rate, και FDI_net_inflows_pct_gdp (οικονομική
ελκυστικότητα/ρεύμα ξένου κεφαλαίου -- θετικό σήμα εδώ, ΟΧΙ "ανεξαρτησία":
η ερμηνεία εξάρτησης/ευπάθειας παραμένει ξεχωριστό ποιοτικό εύρημα στο
role_description, βλ. SEED_SOURCE.md). Το MILITARY category χρησιμοποιεί
military_expenditure_pct_gdp (ένταση προσπάθειας) + military_expenditure_usd
σε λογαριθμική κλίμακα (απόλυτη κλίμακα ικανότητας) και για τις δύο χώρες
(ίδιο indicator_type/πηγή)· το troop_presence_index (ξένη στρατιωτική
παρουσία NATO/KFOR) παραμένει context-only. Πλήρες σκεπτικό/πηγές:
SEED_SOURCE.md.

FUTURE WORK (δεν υλοποιείται τώρα, βλ. SEED_DATA_SPEC.md ενότητες 2.1-2.4
για τα πλήρη στοιχεία όταν χρειαστεί):
- Indicators: eu_fdi_share, eu_preaccession_funds, russian_gas_dependency,
  chinese_loans_cumulative, trade_volume_* ανά εμπορικό εταίρο (Serbia 2023),
  Kosovo GDP_per_capita/GDP_per_capita_USD, δημογραφικά (albanian/serb_
  population_share, serb_share_north_kosovo), has_own_currency,
  has_sovereign_bond_market, intl_aid_share_of_public_spending,
  international_recognitions -- ερευνήθηκαν IPA/trade-partner-volume ξανά
  2026-08-21, παραμένουν deferred (χωρίς αξιόπιστη ετήσια σειρά / χωρίς
  συμμετρικά Kosovo δεδομένα, βλ. SEED_SOURCE.md §3.1)
- Event-markers ως Indicators: ethnic_violence_event, unilateral_declaration,
  political_assassination, barricades_protests
- Military boolean markers του spec (nato_airstrike_days, infrastructure_
  damage, kfor_presence, us_military_base, russian_arms_supply,
  unsc_veto_protection) -- κρατάμε την τρέχουσα military_expenditure_pct_gdp
  / military_expenditure_usd / troop_presence_index προσέγγιση αμετάβλητη.
  SIPRI Arms Transfers (imports TIV) εξετάστηκε 2026-08-21 και απορρίφθηκε --
  Kosovo μόνο 3/10 KEY_YEARS, πολύ αραιό (βλ. SEED_SOURCE.md §3.7). IISS
  Military Balance απορρίφθηκε -- paywalled, μη επαληθεύσιμο. Global
  Firepower Index απορρίφθηκε -- αδιαφανής/υποκειμενική μεθοδολογία,
  τεκμηριωμένο σε πολλαπλές ανεξάρτητες πηγές (βλ. SEED_SOURCE.md §3.7)
"""
from app.core.database import SessionLocal
from app.services import country as country_service
from app.services import indicator as indicator_service
from app.services import negotiation_event as event_service
from app.schemas.country import CountryCreate
from app.schemas.indicator import IndicatorCreate
from app.schemas.negotiation_event import NegotiationEventCreate, ParticipantCreate


def seed_countries(db):
    # role_description=None για Serbia/Kosovo -- κύρια μέρη, ο ρόλος τους
    # περιγράφεται ήδη πλήρως από τα events (βλ. CLAUDE.md).
    countries_data = [
        ("Serbia", "STATE", "EAST", False, "SRB", None),
        ("Kosovo", "STATE", "WEST", None, "XKX", None),
        (
            "USA", "STATE", "WEST", True, "USA",
            "Strategic weight in the Western Balkans; promotes Kosovo's independence and "
            "integration into the Euro-Atlantic sphere. Tools: USAID (1.2bn, 2021-2025), "
            "MCC (300m Serbia / 500m Kosovo for energy decoupling from Russia/China), Camp "
            "Bondsteel, FMF/IMET. Goal: limiting Russian/Chinese influence. Leading role in "
            "lifting the tariffs in 2019-2020 (Trump/Grenell, economic diplomacy).",
        ),
        (
            "EU", "INTERNATIONAL_ORG", "EU", True, None,
            "The most important external actor in normalization. Leverage comes from the "
            "economic dependence of both sides (IPA III: 1.5bn Serbia / 600m Kosovo; 78% of "
            "Serbia's FDI is European; 60% of Serbia's trade with the EU in 2023). Uses "
            "Serbia's European perspective as a pressure tool; main mediator at Brussels and "
            "Ohrid. Sets implementation of the Brussels Agreement as a precondition for "
            "Kosovo's accession; internally divided (5 members -- Spain/Greece/Cyprus/"
            "Slovakia/Romania -- do not recognize Kosovo).",
        ),
        (
            "Russia", "STATE", "EAST", False, "RUS",
            "Serbia's strongest ally in preventing recognition of Kosovo. Leverage: threat "
            "of a UN veto, military supplier (MiG-29, Pantsir-S1), energy control (>80% of "
            "natural gas via Gazprom, controls NIS). Backs the Serbian element in North "
            "Mitrovica. Per the General Conclusions: exploits the dispute as leverage "
            "against the West, using hybrid-warfare practices, blocking resolutions that "
            "would legitimize the new status quo.",
        ),
        (
            "China", "STATE", "EAST", False, "CHN",
            "Serbia's second-largest economic partner after the EU. Does not recognize "
            "Kosovo (linked to its stance on Taiwan, interpretation of Remedial Secession). "
            "BRI, >10bn in loans 2010-2023, zero relations with Kosovo. Steady support for "
            "Serbia, a deterrent role against Kosovo's entry into international "
            "organizations.",
        ),
        (
            "NATO", "MILITARY_ALLIANCE", "WEST", None, None,
            "Present in Kosovo through KFOR since 1999; conflict deterrence, a factor of "
            "stability. The 1999 intervention (Allied Force) that overturned Serbia's "
            "military BATNA. Serbia views it as an occupying force, Kosovo as a security "
            "guarantee.",
        ),
        (
            "UN", "INTERNATIONAL_ORG", "NEUTRAL", None, None,
            "UNMIK since 1999; human rights oversight, monitoring of negotiations, "
            "coordinator of KFOR/OSCE. Resolution 1244. Commissioned the Ahtisaari plan.",
        ),
        (
            "Albania", "STATE", "WEST", True, "ALB",
            "Kosovo's strongest political ally; the first country to recognize its "
            "independence. Joint cabinet meetings, inter-state agreements, shared national/"
            "cultural/linguistic identity. Kosovo's GDP is partly dependent on Albanian "
            "economic activity. Serbia views it as a destabilizing factor.",
        ),
        (
            "India", "STATE", "NEUTRAL", False, "IND",
            "Among the countries that refused to recognize independence (2008), citing "
            "violation of national sovereignty and principles of international law.",
        ),
        (
            "OSCE", "INTERNATIONAL_ORG", "NEUTRAL", None, None,
            "Political stability through election monitoring, human rights protection, and "
            "institutional reforms. Oversight of Kosovo's 2013 municipal elections.",
        ),
        (
            "ICJ", "INTERNATIONAL_ORG", "NEUTRAL", None, None,
            "2010 advisory opinion (Serbia's request): the declaration of independence did "
            "not violate international law, but neither did it legitimize it.",
        ),
    ]

    created = {}
    for name, actor_type, bloc, recognized, code, role_description in countries_data:
        country = country_service.create_country(
            db,
            CountryCreate(
                name=name, actor_type=actor_type, geopolitical_bloc=bloc,
                recognized_kosovo=recognized, country_code=code,
                role_description=role_description,
            ),
        )
        created[name] = country.id
        print(f"  Country: {name} (id={country.id})")
    return created


def seed_indicators(db, country_ids: dict):
    serbia_id = country_ids["Serbia"]
    kosovo_id = country_ids["Kosovo"]

    # (country_id, category, indicator_type, year, value, unit, source, confidence)
    indicators = [
        # ============ SERBIA — ECONOMIC (World Bank API, πραγματικά, EXACT) ============
        # GDP_growth: μαζί με το GDP_absolute_usd παρακάτω, όχι αντί αυτού
        # -- μόνο ο ρυθμός μεταβολής πιάνει σοκ όπως το 1999, το απόλυτο
        # μέγεθος όχι.
        (serbia_id, "ECONOMIC", "GDP_growth", 1998, 5.34, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 1999, -10.33, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2000, 6.06, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2005, 5.90, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2007, 7.83, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2008, 5.16, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2013, 0.45, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2018, 4.65, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2020, -0.95, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2023, 3.75, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", "EXACT"),

        (serbia_id, "ECONOMIC", "unemployment_rate", 1998, 13.70, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 1999, 13.70, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2000, 12.60, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2005, 20.85, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2007, 18.06, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2008, 13.67, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2013, 22.15, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2018, 12.73, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2020, 9.01, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "unemployment_rate", 2023, 8.27, "%", "World Bank API (SL.UEM.TOTL.ZS)", "EXACT"),

        (serbia_id, "ECONOMIC", "trade_share_eu", 2023, 60.0, "%", "European Commission/IMF/Statistical Office of Serbia, Thesis Chart 1.8", None),

        # ============ SERBIA — FDI_net_inflows_pct_gdp ============
        # World Bank API (BX.KLT.DINV.WD.GD.ZS), raw JSON query 2026-08-21.
        # Θετικό οικονομικό σήμα (οικονομική ελκυστικότητα/ρεύμα κεφαλαίου),
        # ΟΧΙ "ανεξαρτησία από εξωτερική επιρροή" -- βλ. σχόλιο στο
        # NORMALIZATION_RANGES (analytics.py) και SEED_SOURCE.md §3.1.
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2007, 9.85, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2008, 7.48, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2013, 4.08, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2018, 7.71, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2020, 6.24, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (serbia_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2023, 6.07, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        # 1998/1999/2000/2005: δεν υπάρχει στο World Bank API (σειρά ξεκινά 2007).

        # ============ SERBIA — GDP_absolute_usd ============
        # Απόλυτο μέγεθος οικονομίας (national-power convention), όχι per
        # capita -- πλήρες σκεπτικό: SEED_SOURCE.md.
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 1999, 20878694850.58, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 2005, 28334256180.88, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 2007, 44888028946.09, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 2008, 54220641201.65, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 2013, 50455529604.07, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (serbia_id, "ECONOMIC", "GDP_absolute_usd", 2023, 81343999280.02, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),

        # ============ SERBIA — MILITARY (World Bank API, πηγή SIPRI) ============
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 1999, 3.53, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2005, 2.22, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2007, 2.16, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2008, 2.05, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2013, 1.85, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        # 2018/2020: bonus fix 2026-08-21 -- ήδη εγκεκριμένο indicator/πηγή,
        # κενά seed rows εντοπίστηκαν κατά το CIA Factbook cross-check (βλ.
        # SEED_SOURCE.md §3.7), όχι νέα πηγή.
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2018, 2.02, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2020, 2.30, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2023, 2.21, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),

        # military_expenditure_usd: απόλυτη κλίμακα ικανότητας (λογαριθμική,
        # βλ. analytics.py), σε αντιδιαστολή με την ένταση προσπάθειας (%GDP)
        # παραπάνω -- ίδιο σκεπτικό με GDP_absolute_usd δίπλα σε GDP_growth.
        # World Bank API (MS.MIL.XPND.CD), raw JSON query 2026-08-21, όλα τα
        # 10 KEY_YEARS διαθέσιμα χωρίς κενά.
        (serbia_id, "MILITARY", "military_expenditure_usd", 1998, 642122263.43, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 1999, 737469450.76, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2000, 337080608.37, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2005, 629500942.83, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2007, 971570564.64, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2008, 1111631537.86, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2013, 932203595.30, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2018, 1064747316.86, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2020, 1282529332.71, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (serbia_id, "MILITARY", "military_expenditure_usd", 2023, 1796879440.10, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),

        # ============ SERBIA — SOCIAL (Freedom House, τιμές SEED_DATA_SPEC.md §2.4) ============
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 54.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 55.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2009, 53.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2011, 55.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 56.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2015, 55.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2017, 53.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2019, 49.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2021, 46.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 43.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),

        # ============ KOSOVO — ECONOMIC ============
        # GDP_growth: ίδιο σκεπτικό με Serbia παραπάνω.
        (kosovo_id, "ECONOMIC", "GDP_growth", 2013, 5.34, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", None),
        (kosovo_id, "ECONOMIC", "GDP_growth", 2023, 4.07, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", None),
        # 1999: δεν υπάρχει στο World Bank API -- το Κόσοβο δεν reportάρεται
        # ως ξεχωριστή entity πριν το 2008.

        (kosovo_id, "ECONOMIC", "unemployment_rate", 2005, 41.0, "%", "ILO/World Bank Open Data, Thesis Chart 1.5", None),
        (kosovo_id, "ECONOMIC", "unemployment_rate", 2007, 46.0, "%", "ILO/World Bank Open Data, Thesis Chart 1.5", None),
        (kosovo_id, "ECONOMIC", "unemployment_rate", 2008, 48.0, "%", "ILO/World Bank Open Data, Thesis Chart 1.5", None),

        (kosovo_id, "ECONOMIC", "trade_share_eu", 2018, 44.7, "%", "Council of the European Union 2018, Thesis Chart 1.7 (imports)", None),

        # ============ KOSOVO — FDI_net_inflows_pct_gdp ============
        # World Bank API (BX.KLT.DINV.WD.GD.ZS), raw JSON query 2026-08-21.
        # Ίδιο indicator_type/σκεπτικό με Serbia παραπάνω.
        (kosovo_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2008, 10.45, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (kosovo_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2013, 5.52, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (kosovo_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2018, 4.04, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (kosovo_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2020, 5.10, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        (kosovo_id, "ECONOMIC", "FDI_net_inflows_pct_gdp", 2023, 8.68, "%", "World Bank API (BX.KLT.DINV.WD.GD.ZS)", "EXACT"),
        # 1998/1999/2000/2005/2007: δεν υπάρχει στο World Bank API (σειρά
        # ξεκινά 2008, ίδιος περιορισμός με GDP_absolute_usd παρακάτω -- το
        # Κόσοβο δεν reportάρεται ως ξεχωριστή entity πριν την ανεξαρτησία).

        # ============ KOSOVO — GDP_absolute_usd ============
        # Μόνο 2008/2013/2023 -- το World Bank (XKX series) δεν έχει
        # δεδομένα για το Κόσοβο πριν την ανεξαρτησία (2008). Καμία τιμή
        # για 1999/2005/2007, δεν υπάρχει αξιόπιστη δημόσια πηγή.
        (kosovo_id, "ECONOMIC", "GDP_absolute_usd", 2008, 5202943075.49, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (kosovo_id, "ECONOMIC", "GDP_absolute_usd", 2013, 6735327512.05, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),
        (kosovo_id, "ECONOMIC", "GDP_absolute_usd", 2023, 10466753839.99, "USD", "World Bank API (NY.GDP.MKTP.CD)", "EXACT"),

        # ============ KOSOVO — MILITARY ============
        # military_expenditure_pct_gdp: World Bank/SIPRI, ίδιος indicator
        # code με Serbia (MS.MIL.XPND.GD.ZS). Μόνο 2008/2013/2023, ίδιος
        # περιορισμός με το GDP_absolute_usd παραπάνω. Confidence=EXACT εδώ
        # ενώ η αντίστοιχη Serbia εγγραφή έχει confidence=None παρόλο που
        # είναι ίδιας ποιότητας δεδομένο -- προϋπάρχουσα ασυνέπεια, βλ.
        # PROJECT_STATUS.md.
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2008, 0.0163, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2013, 0.7217, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        # 2018/2020: bonus fix 2026-08-21, ίδια λογική με Serbia παραπάνω.
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2018, 0.8044, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2020, 1.0230, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2023, 1.2735, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", "EXACT"),

        # 1998/1999/2000/2005/2007: value=0.0 είναι τεκμηριωμένο ιστορικό
        # γεγονός, όχι placeholder ή εκτίμηση -- το Kosovo Security Force
        # ιδρύθηκε Ιανουάριος 2009, πριν από αυτό δεν υπήρχε στρατιωτικό
        # σώμα του Κοσόβου (το προγενέστερο Kosovo Protection Corps ήταν
        # μη-στρατιωτικός οργανισμός πολιτικής προστασίας υπό UNMIK). Βλ.
        # SEED_SOURCE.md. Το 1998/2000 προστέθηκαν 2026-08-21 (bonus fix,
        # ίδιο ιστορικό γεγονός με τα ήδη υπάρχοντα 1999/2005/2007 -- δεν
        # είχαν μπει αρχικά, ασυνέπεια χωρίς λόγο).
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 1998, 0.0, "%GDP", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 1999, 0.0, "%GDP", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2000, 0.0, "%GDP", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2005, 0.0, "%GDP", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_pct_gdp", 2007, 0.0, "%GDP", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),

        # military_expenditure_usd: απόλυτη κλίμακα (λογαριθμική), ίδιο
        # σκεπτικό/πηγή με Serbia. World Bank API (MS.MIL.XPND.CD), raw JSON
        # query 2026-08-21. 1998/1999/2000/2005/2007 = 0.0, ίδιο ιστορικό
        # γεγονός (KSF) όπως το %GDP indicator ακριβώς από πάνω.
        (kosovo_id, "MILITARY", "military_expenditure_usd", 1998, 0.0, "USD", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 1999, 0.0, "USD", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2000, 0.0, "USD", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2005, 0.0, "USD", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2007, 0.0, "USD", "Historical fact: no Kosovo military body existed before KSF founding (Jan 2009) -- see SEED_SOURCE.md", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2008, 927234.77, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2013, 48597681.23, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2018, 63344074.22, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2020, 78965006.27, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),
        (kosovo_id, "MILITARY", "military_expenditure_usd", 2023, 133185465.92, "USD", "World Bank API / SIPRI (MS.MIL.XPND.CD)", "EXACT"),

        # troop_presence_index: context-only (δεν είναι στο
        # NORMALIZATION_RANGES) -- researcher estimate ξένης (NATO/KFOR)
        # στρατιωτικής παρουσίας, εννοιολογικά διαφορετικό από την εγγενή
        # στρατιωτική ικανότητα που μετράει το military_expenditure_pct_gdp
        # παραπάνω. Βλ. SEED_SOURCE.md.
        (kosovo_id, "MILITARY", "troop_presence_index", 1999, 90.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2005, 55.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2007, 45.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2008, 40.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2013, 25.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2023, 15.0, "index_score", "Researcher estimate based on the NATO/KFOR narrative in the thesis", None),

        # ============ KOSOVO — SOCIAL (Freedom House, τιμές SEED_DATA_SPEC.md §2.4) ============
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 27.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 27.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2009, 30.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2011, 31.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 29.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2015, 32.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2017, 34.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2019, 35.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2021, 35.5, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 38.0, "index_score", "Freedom House Nations in Transit, Thesis Chart 1.11", "CHART_READ"),
    ]

    for country_id, category, itype, year, value, unit, source, confidence in indicators:
        indicator_service.create_indicator(
            db,
            IndicatorCreate(
                country_id=country_id, category=category, indicator_type=itype,
                year=year, value=value, unit=unit, source=source, is_verified=True,
                confidence=confidence,
            ),
        )
    print(f"  Indicators: {len(indicators)} εγγραφές")


def seed_events(db, country_ids: dict):
    """
    Τα 10 events (E1-E10) του SEED_DATA_SPEC.md §3. Το spec δεν δίνει ρητά
    participants ανά event -- επιλέχθηκαν με βάση τους δρώντες που
    αναφέρονται στο batna/κείμενο κάθε event (σημειωμένο ανά event παρακάτω).
    """
    events = [
        # E1 -- participants: μόνο Serbia/Kosovo, καμία διεθνής μεσολάβηση
        # δεν αναφέρεται στο spec για αυτή την περίοδο (προ-1999)
        dict(
            title="Revocation of Kosovo's Autonomy", date="1989-03-28",
            description="Collapse of Kosovo's autonomy (1989) and gradual escalation through "
                        "1998: imposition of Serbian control and the development of parallel "
                        "Albanian structures under Ibrahim Rugova.",
            zopa_size="NARROW",
            zopa_reasoning="The positions are mutually exclusive; there is no overlap.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Neither side considers the cost of the conflict to be excessive.",
            batna_side_a="Military control over the territory; state sovereignty recognized internationally",
            batna_side_b="Rugova's parallel structures; non-violent resistance; international exposure of the issue",
            red_lines_side_a="No form of independence; preservation of territorial integrity",
            red_lines_side_b="Restoration of autonomous status as a minimum",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=2, military_weight=6, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY")],
        ),
        # E2 -- participants όπως στο προηγούμενο seed (NATO/UN mediators, βάσει batna)
        dict(
            title="Rambouillet Talks", date="1999-02-06",
            description="Negotiations at Rambouillet, France, which failed to reach an "
                        "agreement. Failure → Operation Allied Force (24/3/1999, 78 days).",
            zopa_size="NARROW",
            zopa_reasoning="Very limited ZOPA, identical red lines.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Neither side perceived a mutually hurting stalemate.",
            batna_side_a="Military strength + Russia/China veto at the UN Security Council",
            batna_side_b="International support from NATO and the UN; prospect of military intervention in its favor",
            red_lines_side_a="No foreign troops on its territory; no independence; guarantees "
                             "for Serbian religious/cultural heritage",
            red_lines_side_b="Withdrawal of Serbian forces; a path toward independence",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=2, military_weight=7, social_weight=1,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("NATO", "MEDIATOR"), ("UN", "MEDIATOR")],
            implementation_success=0.0,
        ),
        # E3 -- participants όπως στο προηγούμενο seed (UN/NATO guarantors, βάσει "διεθνή στρατιωτική προστασία")
        dict(
            title="UN Security Council Resolution 1244", date="1999-06-10",
            description="UN Security Council resolution that ended hostilities. An agreement "
                        "with deliberate ambiguity regarding final status -- this was the key "
                        "that made convergence possible.",
            zopa_size="MODERATE",
            zopa_reasoning="First time a point of mutual gain is identified.",
            ripeness_status="RIPE",
            ripeness_reasoning="The cost of the conflict has become overwhelming for both sides.",
            batna_side_a="Exhausted -- sanctions, bombing, destroyed infrastructure",
            batna_side_b="Complete dependence on humanitarian aid, but with international military protection",
            red_lines_side_a="Formal recognition that Kosovo remains part of the FRY",
            red_lines_side_b="No return of Serbian forces",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=2, military_weight=5, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "GUARANTOR"), ("NATO", "GUARANTOR")],
            implementation_success=0.7,
        ),
        # E4 -- participants: UN (UNMIK διοικούσε αυτή την περίοδο) ως mediator/administrator
        dict(
            title="Standards Before Status", date="2003-01-01",
            description="UNMIK/international community policy: institution-building before "
                        "addressing final status (2003-2005). In 2004, ethnic riots broke out "
                        "-- dozens of Serbian churches and monasteries were burned, thousands "
                        "of Serbs were displaced, and UNMIK temporarily lost control of the "
                        "situation. No progress -- the red lines remained unchanged.",
            zopa_size="NARROW",
            ripeness_status="NOT_RIPE",
            batna_side_a="Economic recovery (~5% GDP/year); Russian-Chinese backing; European "
                         "perspective as leverage",
            batna_side_b="UNMIK/KFOR presence; gradual institution-building",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=3, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR")],
        ),
        # E5 -- negotiation_type: το spec δίνει διπλή ετικέτα "INTEGRATIVE (ως πρόθεση) /
        # DISTRIBUTIVE (ως έκβαση)" -- επιλέχθηκε DISTRIBUTIVE (βάσει της πραγματικής
        # έκβασης/απόρριψης, όχι της αρχικής πρόθεσης)
        dict(
            title="Ahtisaari Plan", date="2007-03-26",
            description="Proposal by UN Special Envoy Martti Ahtisaari for supervised "
                        "independence. Rejected by Serbia -- the two positions are literally "
                        "non-intersecting, a textbook example of ZOPA=∅.",
            zopa_size="NARROW",
            zopa_reasoning="A widening attempt that failed.",
            ripeness_status="EMERGING",
            batna_side_a="Russian veto at the Security Council -- the plan didn't even reach a vote",
            batna_side_b="Unilateral declaration with Western backing",
            red_lines_side_a="\"Something more than autonomy, something less than independence\"",
            red_lines_side_b="\"Nothing less than independence\"",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=2, social_weight=4,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR"), ("EU", "MEDIATOR")],
            implementation_success=0.0,
        ),
        dict(
            title="Unilateral Declaration of Independence", date="2008-02-17",
            description="Unilateral declaration of Kosovo's independence. >100 recognitions; "
                        "5 EU member states refuse; 2010 ICJ advisory opinion (neither "
                        "legitimizes nor condemns it).",
            zopa_size="NARROW",
            ripeness_status="NOT_RIPE",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=2, social_weight=5,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("USA", "GUARANTOR"), ("EU", "GUARANTOR")],
        ),
        dict(
            title="Brussels Agreement", date="2013-04-19",
            description="Brussels Agreement on normalizing relations, mediated by the EU. An "
                        "agreement was reached, but implementation failed -- \"a bad "
                        "precedent.\" The ASM was blocked by Kosovo's Constitutional Court "
                        "(2015); Serbia maintained parallel structures.",
            zopa_size="WIDE",
            zopa_reasoning="The ZOPA had widened considerably compared to previous years.",
            ripeness_status="RIPE",
            ripeness_reasoning="The text explicitly names 2013 a \"critical ripening moment.\"",
            batna_side_a="Visibly weakened -- 2.79bn IPA, 60% of exports to the EU, 13bn FDI. "
                         "No substantive alternative beyond non-recognition",
            batna_side_b="Western backing, but unable to assert sovereignty over northern Kosovo",
            red_lines_side_a="Protection of Serbian communities through an ASM with substantive powers",
            red_lines_side_b="A unified institutional framework; the ASM to have no legislative power",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=6, military_weight=1, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR")],
            implementation_success=0.3,
        ),
        # E8 -- participants: EU mediator βάσει "ζήτησε παρέμβαση Βρυξελλών" στο batna_side_a
        dict(
            title="Kosovo Tariffs on Serbian Goods (100%)", date="2018-11-21",
            description="Trade war: Kosovo imposed 100% tariffs on Serbian (and Bosnian) "
                        "goods. Serious cost for both sides; gradually lifted by 2020 under "
                        "American pressure.",
            zopa_size="NARROW",
            zopa_reasoning="Drastic contraction.",
            ripeness_status="NOT_RIPE",
            batna_side_a="Voting down Kosovo's accession to international organizations; but "
                         "without a strong alternative -- requested Brussels' intervention to "
                         "lift the tariffs",
            batna_side_b="The tariffs reduced dependence on Serbian imports → increased its bargaining power",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=7, military_weight=1, social_weight=2,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("EU", "MEDIATOR")],
        ),
        # E9 -- negotiation_type: spec "INTEGRATIVE (μόνο οικονομικό επίπεδο)" -> INTEGRATIVE_WIN_WIN
        dict(
            title="Washington Agreement", date="2020-09-04",
            description="An economic agreement under American mediation (economic level "
                        "only, not political status). Failed -- lack of political will, "
                        "change of US leadership, absence of an enforcement mechanism.",
            zopa_size="NARROW",
            zopa_reasoning="Quite a limited ZOPA.",
            ripeness_status="EMERGING",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=8, military_weight=1, social_weight=1,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("USA", "MEDIATOR")],
            implementation_success=0.1,
        ),
        dict(
            title="Ohrid Agreement", date="2023-03-18",
            description="Ohrid Agreement on implementing the Basic Agreement for the "
                        "normalization of relations. Accepted but not formally signed; "
                        "verbal commitments; implementation pending.",
            zopa_size="WIDE",
            zopa_reasoning="The ZOPA assessment is positive, having widened compared to "
                          "previous agreements.",
            ripeness_status="RIPE",
            batna_side_a="Russian-Chinese backing, but the European perspective acts as a "
                         "constraint on its use",
            batna_side_b="Continued Western support for gradual international recognition",
            red_lines_side_a="No explicit recognition; self-governance for Serbian communities",
            red_lines_side_b="No obstruction of accession to international organizations",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=5, military_weight=1, social_weight=4,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR"), ("USA", "MEDIATOR")],
            implementation_success=0.2,
        ),
    ]

    for event_data in events:
        participants_raw = event_data.pop("participants")
        participants = [
            ParticipantCreate(country_id=country_ids[name], role=role)
            for name, role in participants_raw
        ]
        event_service.create_event(db, NegotiationEventCreate(**event_data, participants=participants))
        print(f"  Event: {event_data['title']}")


def run_seed():
    db = SessionLocal()
    try:
        # Idempotency guard -- χωρίς αυτό, ένα δεύτερο τρέξιμο πάνω σε ήδη
        # γεμάτη ΒΔ θα έσκαγε σε duplicate-key errors (κανένα ON CONFLICT
        # στο repository layer). Απαραίτητο γιατί το api container του
        # Docker Compose τρέχει αυτό το script σε κάθε startup (βλ.
        # docker-entrypoint.sh)· η χειροκίνητη ροή
        # `python -m app.scripts.seed` παραμένει ίδια.
        if country_service.list_countries(db):
            print("Seed data already present -- skipping (idempotent run_seed).")
            return

        print("Δημιουργία χωρών/δρώντων...")
        country_ids = seed_countries(db)
        print("Δημιουργία indicators...")
        seed_indicators(db, country_ids)
        print("Δημιουργία negotiation events...")
        seed_events(db, country_ids)
        print("\nSeed ολοκληρώθηκε επιτυχώς!")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
