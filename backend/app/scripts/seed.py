"""
Seed script -- γεμίζει τη ΒΔ με τα δεδομένα της διπλωματικής.
Τρέχεται με: python -m app.scripts.seed

ΠΗΓΕΣ:
- Economic (GDP growth, unemployment), Serbia: World Bank API, πραγματικά,
  confidence=EXACT (ακριβής δημοσιευμένη τιμή -- βλ. απόφαση 2026-08-02)
- Military (% GDP δαπανών, Σερβία): World Bank API (πηγή SIPRI), πραγματικά
- Military (Κόσοβο): τεκμηριωμένη εκτίμηση έντασης ξένης στρατιωτικής
  παρουσίας (KFOR/NATO), βάσει αφηγηματικού κειμένου διπλωματικής
- Social (Freedom House score, Σερβία+Κόσοβο): τιμές SEED_DATA_SPEC.md §2.4
  (Γράφημα 1.11 διπλωματικής), confidence=CHART_READ -- υιοθετήθηκαν
  2026-08-02 αντί των αρχικών ενδεικτικών τιμών
- Kosovo unemployment (2005-2008): Γράφημα 1.5 διπλωματικής (ILO/WB, δεν
  καλύπτεται από το World Bank API για αυτή την περίοδο)
- Kosovo trade_share_eu (2018): Γράφημα 1.7 διπλωματικής (εισαγωγές, 44.7%
  -- υιοθετήθηκε 2026-08-02 αντί του δικού μας μέσου όρου εισαγωγών/εξαγωγών)
- Serbia trade_share_eu (2023): Γράφημα 1.8 διπλωματικής

10 negotiation events (E1-E10) όπως περιγράφονται στο SEED_DATA_SPEC.md §3
(υιοθετήθηκαν 2026-08-02, αντικατέστησαν τα αρχικά 7 -- βλ. PROJECT_STATUS.md
για το πλήρες change-log αυτής της αναθεώρησης).

FUTURE WORK (αποφασίστηκε ρητά να ΜΗΝ μπουν τώρα, βλ. SEED_DATA_SPEC.md
ενότητες 2.1-2.4 για τα πλήρη στοιχεία όταν χρειαστεί):
- Indicators: eu_fdi_share, eu_preaccession_funds, russian_gas_dependency,
  chinese_loans_cumulative, trade_volume_* ανά εμπορικό εταίρο (Serbia 2023),
  Kosovo GDP_per_capita/GDP_per_capita_USD, δημογραφικά (albanian/serb_
  population_share, serb_share_north_kosovo), has_own_currency,
  has_sovereign_bond_market, intl_aid_share_of_public_spending,
  international_recognitions
- Event-markers ως Indicators: ethnic_violence_event, unilateral_declaration,
  political_assassination, barricades_protests
- Military boolean markers του spec (nato_airstrike_days, infrastructure_
  damage, kfor_presence, us_military_base, russian_arms_supply,
  unsc_veto_protection) -- κρατάμε την τρέχουσα military_expenditure_pct_gdp
  / troop_presence_index προσέγγιση αμετάβλητη
"""
from app.core.database import SessionLocal
from app.services import country as country_service
from app.services import indicator as indicator_service
from app.services import negotiation_event as event_service
from app.schemas.country import CountryCreate
from app.schemas.indicator import IndicatorCreate
from app.schemas.negotiation_event import NegotiationEventCreate, ParticipantCreate


def seed_countries(db):
    countries_data = [
        ("Serbia", "STATE", "EAST", False, "SRB"),
        ("Kosovo", "STATE", "WEST", None, "XKX"),
        ("USA", "STATE", "WEST", True, "USA"),
        ("EU", "INTERNATIONAL_ORG", "EU", True, None),
        ("Russia", "STATE", "EAST", False, "RUS"),
        ("China", "STATE", "EAST", False, "CHN"),
        ("NATO", "MILITARY_ALLIANCE", "WEST", None, None),
        ("UN", "INTERNATIONAL_ORG", "NEUTRAL", None, None),
        ("Albania", "STATE", "WEST", True, "ALB"),
    ]

    created = {}
    for name, actor_type, bloc, recognized, code in countries_data:
        country = country_service.create_country(
            db,
            CountryCreate(
                name=name, actor_type=actor_type, geopolitical_bloc=bloc,
                recognized_kosovo=recognized, country_code=code,
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

        (serbia_id, "ECONOMIC", "trade_share_eu", 2023, 60.0, "%", "European Commission/IMF/Statistical Office of Serbia, Γράφημα 1.8 διπλωματικής", None),

        # ============ SERBIA — MILITARY (World Bank API, πηγή SIPRI, πραγματικά -- ΑΜΕΤΑΒΛΗΤΟ) ============
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 1999, 3.53, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2005, 2.22, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2007, 2.16, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2008, 2.05, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2013, 1.85, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2023, 2.21, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)", None),

        # ============ SERBIA — SOCIAL (Freedom House, τιμές SEED_DATA_SPEC.md §2.4) ============
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 54.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 55.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2009, 53.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2011, 55.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 56.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2015, 55.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2017, 53.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2019, 49.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2021, 46.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 43.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),

        # ============ KOSOVO — ECONOMIC ============
        (kosovo_id, "ECONOMIC", "GDP_growth", 2013, 5.34, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", None),
        (kosovo_id, "ECONOMIC", "GDP_growth", 2023, 4.07, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)", None),
        # 1999: δεν υπάρχει στο World Bank API (πριν το 2009) -- σκόπιμα δεν εικάζουμε

        (kosovo_id, "ECONOMIC", "unemployment_rate", 2005, 41.0, "%", "ILO/World Bank Open Data, Γράφημα 1.5 διπλωματικής", None),
        (kosovo_id, "ECONOMIC", "unemployment_rate", 2007, 46.0, "%", "ILO/World Bank Open Data, Γράφημα 1.5 διπλωματικής", None),
        (kosovo_id, "ECONOMIC", "unemployment_rate", 2008, 48.0, "%", "ILO/World Bank Open Data, Γράφημα 1.5 διπλωματικής", None),

        (kosovo_id, "ECONOMIC", "trade_share_eu", 2018, 44.7, "%", "Council of the European Union 2018, Γράφημα 1.7 διπλωματικής (εισαγωγές)", None),

        # ============ KOSOVO — MILITARY (τεκμηριωμένη εκτίμηση -- ΑΜΕΤΑΒΛΗΤΟ) ============
        (kosovo_id, "MILITARY", "troop_presence_index", 1999, 90.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2005, 55.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2007, 45.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2008, 40.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2013, 25.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),
        (kosovo_id, "MILITARY", "troop_presence_index", 2023, 15.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική", None),

        # ============ KOSOVO — SOCIAL (Freedom House, τιμές SEED_DATA_SPEC.md §2.4) ============
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 27.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 27.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2009, 30.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2011, 31.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 29.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2015, 32.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2017, 34.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2019, 35.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2021, 35.5, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 38.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής", "CHART_READ"),
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
            description="Κατάρρευση της αυτονομίας του Κοσόβου (1989) και σταδιακή κλιμάκωση "
                        "έως το 1998: επιβολή σερβικού ελέγχου και ανάπτυξη παράλληλων "
                        "αλβανικών δομών υπό τον Ibrahim Rugova.",
            zopa_size="NARROW",
            zopa_reasoning="Οι θέσεις είναι αμοιβαία αποκλειόμενες, δεν υπάρχει επικάλυψη.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Καμία πλευρά δεν θεωρεί το κόστος της σύγκρουσης υπερβολικό.",
            batna_side_a="Στρατιωτικός έλεγχος επί του εδάφους· κρατική κυριαρχία αναγνωρισμένη διεθνώς",
            batna_side_b="Παράλληλες δομές Ρουγκόβα· μη βίαιη αντίσταση· διεθνής προβολή του ζητήματος",
            red_lines_side_a="Καμία μορφή ανεξαρτησίας· διατήρηση εδαφικής ακεραιότητας",
            red_lines_side_b="Επαναφορά του καθεστώτος αυτονομίας ως ελάχιστο",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=2, military_weight=6, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY")],
        ),
        # E2 -- participants όπως στο προηγούμενο seed (NATO/UN mediators, βάσει batna)
        dict(
            title="Rambouillet Talks", date="1999-02-06",
            description="Διαπραγματεύσεις στο Rambouillet της Γαλλίας, οι οποίες απέτυχαν να "
                        "καταλήξουν σε συμφωνία. Αποτυχία → επιχείρηση Allied Force "
                        "(24/3/1999, 78 ημέρες).",
            zopa_size="NARROW",
            zopa_reasoning="Πολύ περιορισμένη ZOPA, πανομοιότυπες κόκκινες γραμμές.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Καμία πλευρά δεν αντιλαμβανόταν αμοιβαία επώδυνο αδιέξοδο.",
            batna_side_a="Στρατιωτική ισχύς + βέτο Ρωσίας/Κίνας στο ΣΑ του ΟΗΕ",
            batna_side_b="Διεθνής υποστήριξη ΝΑΤΟ και ΟΗΕ· προοπτική στρατιωτικής παρέμβασης υπέρ της",
            red_lines_side_a="Όχι ξένα στρατεύματα στο έδαφός της· όχι ανεξαρτησία· εγγυήσεις για "
                             "σερβική θρησκευτική/πολιτισμική κληρονομιά",
            red_lines_side_b="Αποχώρηση σερβικών δυνάμεων· πορεία προς ανεξαρτησία",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=2, military_weight=7, social_weight=1,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("NATO", "MEDIATOR"), ("UN", "MEDIATOR")],
            implementation_success=0.0,
        ),
        # E3 -- participants όπως στο προηγούμενο seed (UN/NATO guarantors, βάσει "διεθνή στρατιωτική προστασία")
        dict(
            title="UN Security Council Resolution 1244", date="1999-06-10",
            description="Ψήφισμα του Συμβουλίου Ασφαλείας του ΟΗΕ που τερμάτισε τις εχθροπραξίες. "
                        "Συμφωνία με σκόπιμη ασάφεια ως προς το τελικό καθεστώς -- αυτό ήταν το "
                        "κλειδί που επέτρεψε τη σύγκλιση.",
            zopa_size="MODERATE",
            zopa_reasoning="Πρώτη φορά που εντοπίζεται σημείο αμοιβαίου κέρδους.",
            ripeness_status="RIPE",
            ripeness_reasoning="Το κόστος της σύγκρουσης έχει γίνει συντριπτικό και για τις δύο πλευρές.",
            batna_side_a="Εξαντλημένη -- κυρώσεις, βομβαρδισμοί, κατεστραμμένες υποδομές",
            batna_side_b="Πλήρης εξάρτηση από ανθρωπιστική βοήθεια, αλλά με διεθνή στρατιωτική προστασία",
            red_lines_side_a="Τυπική αναγνώριση ότι το Κόσοβο παραμένει μέρος της ΟΔΓ",
            red_lines_side_b="Μη επιστροφή σερβικών δυνάμεων",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=2, military_weight=5, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "GUARANTOR"), ("NATO", "GUARANTOR")],
            implementation_success=0.7,
        ),
        # E4 -- participants: UN (UNMIK διοικούσε αυτή την περίοδο) ως mediator/administrator
        dict(
            title="Standards Before Status", date="2003-01-01",
            description="Πολιτική UNMIK/διεθνούς κοινότητας: θεσμική οικοδόμηση πριν την "
                        "εξέταση τελικού καθεστώτος (2003-2005). Το 2004 ξέσπασαν εθνοτικές "
                        "ταραχές -- δεκάδες σερβικές εκκλησίες και μοναστήρια πυρπολήθηκαν, "
                        "χιλιάδες Σέρβοι εκτοπίστηκαν, και η UNMIK έχασε προσωρινά τον έλεγχο "
                        "της κατάστασης. Καμία πρόοδος -- οι κόκκινες γραμμές παρέμειναν "
                        "αμετάβλητες.",
            zopa_size="NARROW",
            ripeness_status="NOT_RIPE",
            batna_side_a="Οικονομική ανάκαμψη (~5% ΑΕΠ/έτος)· ρωσοκινεζική στήριξη· ευρωπαϊκή "
                         "προοπτική ως μοχλός",
            batna_side_b="Παρουσία UNMIK/KFOR· σταδιακή θεσμική οικοδόμηση",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=3, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR")],
        ),
        # E5 -- negotiation_type: το spec δίνει διπλή ετικέτα "INTEGRATIVE (ως πρόθεση) /
        # DISTRIBUTIVE (ως έκβαση)" -- επιλέχθηκε DISTRIBUTIVE (βάσει της πραγματικής
        # έκβασης/απόρριψης, όχι της αρχικής πρόθεσης)
        dict(
            title="Ahtisaari Plan", date="2007-03-26",
            description="Πρόταση του ειδικού απεσταλμένου του ΟΗΕ Martti Ahtisaari για "
                        "επιτηρούμενη ανεξαρτησία. Απόρριψη από Σερβία -- οι δύο θέσεις είναι "
                        "κυριολεκτικά μη τεμνόμενες, ιδανικό παράδειγμα ZOPA=∅.",
            zopa_size="NARROW",
            zopa_reasoning="Απόπειρα διεύρυνσης που απέτυχε.",
            ripeness_status="EMERGING",
            batna_side_a="Βέτο Ρωσίας στο ΣΑ -- το σχέδιο δεν έφτασε καν προς ψήφιση",
            batna_side_b="Μονομερής ανακήρυξη με δυτική στήριξη",
            red_lines_side_a="«Κάτι περισσότερο από αυτονομία, κάτι λιγότερο από ανεξαρτησία»",
            red_lines_side_b="«Όχι κάτι λιγότερο από ανεξαρτησία»",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=2, social_weight=4,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR"), ("EU", "MEDIATOR")],
            implementation_success=0.0,
        ),
        dict(
            title="Unilateral Declaration of Independence", date="2008-02-17",
            description="Μονομερής ανακήρυξη ανεξαρτησίας του Κοσόβου. >100 αναγνωρίσεις· 5 "
                        "κράτη-μέλη ΕΕ αρνούνται· γνωμοδότηση ICJ 2010 (ούτε νομιμοποιεί ούτε "
                        "καταδικάζει).",
            zopa_size="NARROW",
            ripeness_status="NOT_RIPE",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=2, social_weight=5,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("USA", "GUARANTOR"), ("EU", "GUARANTOR")],
        ),
        dict(
            title="Brussels Agreement", date="2013-04-19",
            description="Συμφωνία Βρυξελλών για την ομαλοποίηση των σχέσεων, με τη μεσολάβηση "
                        "της ΕΕ. Συμφωνία, αλλά αποτυχία εφαρμογής -- «κακό προηγούμενο». Η ASM "
                        "μπλοκαρίστηκε από το Συνταγματικό Δικαστήριο του Κοσόβου (2015)· η "
                        "Σερβία διατήρησε παράλληλες δομές.",
            zopa_size="WIDE",
            zopa_reasoning="Η ZOPA είχε διευρυνθεί αρκετά σε σύγκριση με τα προηγούμενα χρόνια.",
            ripeness_status="RIPE",
            ripeness_reasoning="Το κείμενο ονομάζει ρητά το 2013 «κρίσιμη στιγμή ωρίμανσης».",
            batna_side_a="Εμφανώς αποδυναμωμένη -- 2,79 δις IPA, 60% εξαγωγών προς ΕΕ, 13 δις "
                         "FDI. Καμία ουσιαστική εναλλακτική πέραν της μη αναγνώρισης",
            batna_side_b="Δυτική στήριξη, αλλά αδυναμία επιβολής κυριαρχίας στο Βόρειο Κόσοβο",
            red_lines_side_a="Προστασία σερβικών κοινοτήτων μέσω ΑSM με ουσιαστικές αρμοδιότητες",
            red_lines_side_b="Ενιαίο θεσμικό πλαίσιο· η ASM να μην έχει νομοθετική εξουσία",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=6, military_weight=1, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR")],
            implementation_success=0.3,
        ),
        # E8 -- participants: EU mediator βάσει "ζήτησε παρέμβαση Βρυξελλών" στο batna_side_a
        dict(
            title="Kosovo Tariffs on Serbian Goods (100%)", date="2018-11-21",
            description="Εμπορικός πόλεμος: το Κόσοβο επέβαλε δασμούς 100% σε σερβικά (και "
                        "βοσνιακά) προϊόντα. Σοβαρό κόστος και για τις δύο πλευρές· άρση "
                        "σταδιακά μέχρι το 2020 με αμερικανική πίεση.",
            zopa_size="NARROW",
            zopa_reasoning="Δραστική συρρίκνωση.",
            ripeness_status="NOT_RIPE",
            batna_side_a="Καταψήφιση ένταξης Κοσόβου σε διεθνείς οργανισμούς· αλλά χωρίς ισχυρή "
                         "εναλλακτική -- ζήτησε παρέμβαση Βρυξελλών για άρση δασμών",
            batna_side_b="Οι δασμοί μείωσαν την εξάρτηση από σερβικές εισαγωγές → αύξησαν τη "
                         "διαπραγματευτική του ισχύ",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=7, military_weight=1, social_weight=2,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("EU", "MEDIATOR")],
        ),
        # E9 -- negotiation_type: spec "INTEGRATIVE (μόνο οικονομικό επίπεδο)" -> INTEGRATIVE_WIN_WIN
        dict(
            title="Washington Agreement", date="2020-09-04",
            description="Οικονομικής φύσης συμφωνία υπό αμερικανική μεσολάβηση (μόνο σε "
                        "οικονομικό επίπεδο, όχι πολιτικό καθεστώς). Αποτυχία -- έλλειψη "
                        "πολιτικής βούλησης, αλλαγή ηγεσίας ΗΠΑ, απουσία ελεγκτικού μηχανισμού.",
            zopa_size="NARROW",
            zopa_reasoning="Αρκετά περιορισμένη ZOPA.",
            ripeness_status="EMERGING",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=8, military_weight=1, social_weight=1,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("USA", "MEDIATOR")],
            implementation_success=0.1,
        ),
        dict(
            title="Ohrid Agreement", date="2023-03-18",
            description="Συμφωνία της Οχρίδας για την εφαρμογή του Βασικού Σχεδίου ομαλοποίησης "
                        "σχέσεων. Έγινε δεκτή αλλά δεν υπογράφηκε επισήμως· προφορικές "
                        "δεσμεύσεις· εκκρεμεί η εφαρμογή.",
            zopa_size="WIDE",
            zopa_reasoning="Η αξιολόγηση της ZOPA είναι θετική, διευρύνθηκε σε σύγκριση με "
                          "προηγούμενες συμφωνίες.",
            ripeness_status="RIPE",
            batna_side_a="Ρωσοκινεζική στήριξη, αλλά η ευρωπαϊκή προοπτική λειτουργεί ως "
                         "περιοριστικός παράγοντας στη χρήση της",
            batna_side_b="Διατήρηση δυτικής υποστήριξης για σταδιακή διεθνή αναγνώριση",
            red_lines_side_a="Μη ρητή αναγνώριση· αυτοδιοίκηση σερβικών κοινοτήτων",
            red_lines_side_b="Μη παρεμπόδιση ένταξης σε διεθνείς οργανισμούς",
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
