"""
Υπολογιστικός πυρήνας: Power Index, Power Gap, Window Score, Optimal
Periods, Best Moments. ΚΑΝΕΝΑΣ υπολογισμός εδώ δεν καλεί LLM -- όλα
είναι ντετερμινιστικά, ίδιο input δίνει πάντα ίδιο output.
"""
import math

from sqlalchemy.orm import Session

from app.repositories import indicator as indicator_repository
from app.repositories import negotiation_event as event_repository


# ECONOMIC = GDP_growth + GDP_absolute_usd + unemployment_rate +
# FDI_net_inflows_pct_gdp, ισοβαρή μέσο όρο (βλ. get_category_score). Το
# GDP_growth πιάνει σοκ/ρυθμό μεταβολής (π.χ. την κατάρρευση του 1999), το
# GDP_absolute_usd το μέγεθος της οικονομίας, το FDI_net_inflows_pct_gdp
# την οικονομική ελκυστικότητα/ρεύμα ξένου κεφαλαίου -- διαφορετικές
# διαστάσεις, χρειάζονται όλες. ΣΗΜΕΙΩΣΗ ερμηνείας: το FDI_net_inflows_pct_gdp
# εδώ μετράει θετικό οικονομικό σήμα (περισσότερη εισροή κεφαλαίου = υψηλότερο
# score), ΟΧΙ "ανεξαρτησία από εξωτερική επιρροή" -- η ερμηνεία της
# διπλωματικής (FDI ως δείκτης οικονομικής εξάρτησης/ευπάθειας BATNA)
# παραμένει ξεχωριστό, ποιοτικό εύρημα στο role_description της ΕΕ, όχι κάτι
# που το Power Index αντικαθιστά ή αναιρεί. Πλήρες σκεπτικό/πηγές:
# SEED_SOURCE.md.
# MILITARY χρησιμοποιεί military_expenditure_pct_gdp (ένταση προσπάθειας
# σχετικά με το μέγεθος της οικονομίας) + military_expenditure_usd (απόλυτη
# κλίμακα ικανότητας, λογαριθμική κλίμακα -- ίδιο σκεπτικό με GDP_absolute_usd)
# και για τις δύο χώρες, ίδιο indicator_type/πηγή -- το troop_presence_index
# (ξένη στρατιωτική παρουσία) παραμένει context-only, εννοιολογικά
# διαφορετικό μέγεθος.
NORMALIZATION_RANGES = {
    "GDP_growth": (-20.0, 10.0),
    # $1B-$100B, λογαριθμική κλίμακα (βλ. LOG_SCALE_INDICATORS) -- γραμμική
    # κλίμακα σε τόσο μεγάλο εύρος συνέθλιβε το μικρότερο Kosovo GDP σε μια
    # σχεδόν σταθερή χαμηλή τιμή, ανεξάρτητα από πραγματική οικονομική
    # δυναμική. Κάτω όριο κάτω από το μικρότερο πραγματικό Kosovo GDP
    # ($5.2B, 2008) ώστε να μην clamp-άρει στο μηδέν.
    "GDP_absolute_usd": (1_000_000_000.0, 100_000_000_000.0),
    "freedom_house_score": (0.0, 100.0),
    "unemployment_rate": (0.0, 60.0),
    "trade_share_eu": (0.0, 100.0),
    "military_expenditure_pct_gdp": (0.0, 8.0),
    # World Bank BX.KLT.DINV.WD.GD.ZS -- παρατηρημένο εύρος 2.8%-10.45% και
    # στις δύο χώρες (2007-2023), 20% δίνει άνετο περιθώριο (ίδιο σκεπτικό με
    # unemployment_rate 0-60 έναντι παρατηρημένου 8-48).
    "FDI_net_inflows_pct_gdp": (0.0, 20.0),
    # $500K-$5B, λογαριθμική κλίμακα -- κάτω όριο κάτω από το μικρότερο
    # πραγματικό Kosovo military spending ($927K, 2008), άνω όριο πάνω από
    # το μεγαλύτερο Serbia ($1.8δισ, 2023). Ίδιο πρόβλημα/λύση με
    # GDP_absolute_usd: ο λόγος Serbia/Kosovo εδώ (~690× το 2008) είναι ΑΚΟΜΑ
    # μεγαλύτερος από το GDP, άρα γραμμική κλίμακα θα συνέθλιβε το Kosovo
    # ακόμα πιο δραστικά.
    "military_expenditure_usd": (500_000.0, 5_000_000_000.0),
}

# indicator_types όπου χαμηλότερη raw τιμή σημαίνει ισχυρότερη θέση (π.χ.
# ανεργία) -- το normalize() τα αντιστρέφει.
LOWER_IS_BETTER = {"unemployment_rate"}

# indicator_types όπου η κλίμακα είναι λογαριθμική, όχι γραμμική --
# κατάλληλο για μεγέθη με διαφορά τάξεων μεγέθους (στάνταρ οικονομετρική
# πρακτική). Τα δύο άκρα στο NORMALIZATION_RANGES ερμηνεύονται ΠΡΙΝ το
# log10 (raw USD), όχι ήδη-λογαριθμισμένα.
LOG_SCALE_INDICATORS = {"GDP_absolute_usd", "military_expenditure_usd"}


def normalize(value: float, indicator_type: str) -> float:
    if indicator_type not in NORMALIZATION_RANGES:
        raise ValueError(f"Δεν υπάρχουν normalization όρια για '{indicator_type}'")

    min_val, max_val = NORMALIZATION_RANGES[indicator_type]

    if indicator_type in LOG_SCALE_INDICATORS:
        # clamp πρώτα στο raw εύρος (πριν το log10) -- αλλιώς log10(0) ή
        # log10 αρνητικού θα έσκαγε για τιμές έξω από το εύρος.
        value = max(min_val, min(value, max_val))
        value = math.log10(value)
        min_val = math.log10(min_val)
        max_val = math.log10(max_val)

    clamped = max(min_val, min(value, max_val))
    normalized = (clamped - min_val) / (max_val - min_val) * 100
    if indicator_type in LOWER_IS_BETTER:
        normalized = 100 - normalized
    return round(normalized, 2)


def get_category_score(
    db: Session, country_id: int, year: int, category: str
) -> float | None:
    all_indicators = indicator_repository.get_by_country(db, country_id)

    matching = [
        ind for ind in all_indicators
        if ind.year == year and ind.category.value == category
        # Αγνοούμε indicator_types εκτός Power Index (context-only, π.χ.
        # troop_presence_index, βλ. SEED_SOURCE.md) -- χωρίς αυτό το
        # φίλτρο, το normalize() παρακάτω θα έσκαγε με ValueError για κάθε
        # τέτοιο indicator.
        and ind.indicator_type in NORMALIZATION_RANGES
    ]

    if not matching:
        return None

    normalized_values = [normalize(ind.value, ind.indicator_type) for ind in matching]
    average = sum(normalized_values) / len(normalized_values)
    return round(average, 2)


POWER_INDEX_WEIGHTS = {
    "ECONOMIC": 0.40,
    "MILITARY": 0.40,
    "SOCIAL_UNREST": 0.20,
}


def calculate_power_index(db: Session, country_id: int, year: int) -> float | None:
    economic = get_category_score(db, country_id, year, "ECONOMIC")
    military = get_category_score(db, country_id, year, "MILITARY")
    social = get_category_score(db, country_id, year, "SOCIAL_UNREST")

    if economic is None or military is None or social is None:
        return None

    power_index = (
        economic * POWER_INDEX_WEIGHTS["ECONOMIC"]
        + military * POWER_INDEX_WEIGHTS["MILITARY"]
        + social * POWER_INDEX_WEIGHTS["SOCIAL_UNREST"]
    )
    return round(power_index, 2)


def calculate_power_index_breakdown(db: Session, country_id: int, year: int) -> dict | None:
    economic = get_category_score(db, country_id, year, "ECONOMIC")
    military = get_category_score(db, country_id, year, "MILITARY")
    social = get_category_score(db, country_id, year, "SOCIAL_UNREST")

    if economic is None or military is None or social is None:
        return None

    return {
        "economic": economic,
        "military": military,
        "social": social,
        "power_index": calculate_power_index(db, country_id, year),
    }


def calculate_power_gap(
    db: Session, serbia_id: int, kosovo_id: int, year: int
) -> float | None:
    serbia_pi = calculate_power_index(db, serbia_id, year)
    kosovo_pi = calculate_power_index(db, kosovo_id, year)

    if serbia_pi is None or kosovo_pi is None:
        return None

    return round(abs(serbia_pi - kosovo_pi), 2)


def calculate_trend_score(
    current_serbia: float, previous_serbia: float,
    current_kosovo: float, previous_kosovo: float,
) -> float:
    serbia_decline = max(0.0, previous_serbia - current_serbia)
    kosovo_decline = max(0.0, previous_kosovo - current_kosovo)
    avg_decline = (serbia_decline + kosovo_decline) / 2
    return round(min(100.0, avg_decline / 30 * 100), 2)


def calculate_social_stability_score(
    db: Session, serbia_id: int, kosovo_id: int, year: int
) -> float | None:
    """
    ΔΙΟΡΘΩΣΗ ΚΑΤΕΥΘΥΝΣΗΣ 2026-08-21 (πριν: calculate_social_pressure_score,
    επέστρεφε 100-avg_stability -- "περισσότερη αστάθεια = υψηλότερο
    Window Score"). Η διπλωματική δείχνει ρητά ότι η εσωτερική αστάθεια
    ΑΥΞΑΝΕΙ το πολιτικό κόστος μιας υποχώρησης -- δυσκολεύει, όχι
    διευκολύνει, τη συμφωνία. Άρα η κατεύθυνση αντιστράφηκε: επιστρέφει
    το ΑΚΑΤΕΡΓΑΣΤΟ (0-100, υψηλότερο=πιο σταθερό) SOCIAL_UNREST category
    score, όχι το αντεστραμμένο του. Βλ. SEED_SOURCE.md §10 για πλήρες
    σκεπτικό/παραπομπή.
    """
    serbia_social = get_category_score(db, serbia_id, year, "SOCIAL_UNREST")
    kosovo_social = get_category_score(db, kosovo_id, year, "SOCIAL_UNREST")

    if serbia_social is None or kosovo_social is None:
        return None

    avg_stability = (serbia_social + kosovo_social) / 2
    return round(avg_stability, 2)


def calculate_window_score(
    db: Session,
    serbia_id: int,
    kosovo_id: int,
    year: int,
    previous_year: int | None = None,
) -> float | None:
    gap = calculate_power_gap(db, serbia_id, kosovo_id, year)
    if gap is None:
        return None
    symmetry_score = round(100 - gap, 2)

    trend_score = 0.0
    if previous_year is not None:
        current_serbia = calculate_power_index(db, serbia_id, year)
        previous_serbia = calculate_power_index(db, serbia_id, previous_year)
        current_kosovo = calculate_power_index(db, kosovo_id, year)
        previous_kosovo = calculate_power_index(db, kosovo_id, previous_year)

        if None not in (current_serbia, previous_serbia, current_kosovo, previous_kosovo):
            trend_score = calculate_trend_score(
                current_serbia, previous_serbia, current_kosovo, previous_kosovo
            )

    social_stability = calculate_social_stability_score(db, serbia_id, kosovo_id, year)
    if social_stability is None:
        return None

    window_score = (
        symmetry_score * 0.50
        + trend_score * 0.30
        + social_stability * 0.20
    )
    return round(window_score, 2)


KEY_YEARS = [1998, 1999, 2000, 2005, 2007, 2008, 2013, 2018, 2020, 2023]


def find_optimal_agreement_period(db: Session, country_id: int) -> dict | None:
    best_year = None
    best_score = None

    for year in KEY_YEARS:
        score = calculate_power_index(db, country_id, year)
        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_year = year

    if best_year is None:
        return None

    return {"year": best_year, "power_index": best_score}


def _most_recent_year_with_data(
    db: Session, serbia_id: int, kosovo_id: int, year: int
) -> int | None:
    """
    Το πιο πρόσφατο έτος στο KEY_YEARS πριν το `year` όπου και οι δύο
    χώρες έχουν πλήρες Power Index -- χρησιμοποιείται σαν `previous_year`
    στο calculate_window_score. Με αραιά KEY_YEARS, το απλά-προηγούμενο
    στοιχείο της λίστας μπορεί να μην έχει δεδομένα, μηδενίζοντας αθόρυβα
    το trend_score (30% βάρος στο Window Score) -- γι' αυτό ψάχνουμε αντί
    να υποθέτουμε.
    """
    idx = KEY_YEARS.index(year)
    for candidate in reversed(KEY_YEARS[:idx]):
        if (
            calculate_power_index(db, serbia_id, candidate) is not None
            and calculate_power_index(db, kosovo_id, candidate) is not None
        ):
            return candidate
    return None


def find_optimal_mutual_compromise_period(
    db: Session, serbia_id: int, kosovo_id: int
) -> dict | None:
    best_year = None
    best_score = None

    for year in KEY_YEARS:
        previous_year = _most_recent_year_with_data(db, serbia_id, kosovo_id, year)
        score = calculate_window_score(db, serbia_id, kosovo_id, year, previous_year)

        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_year = year

    if best_year is None:
        return None

    return {"year": best_year, "window_score": best_score}


BEST_MOMENT_THRESHOLD = 60.0


def find_best_moments(db: Session, serbia_id: int, kosovo_id: int) -> list[dict]:
    events = event_repository.get_all(db)
    results = []

    for event in events:
        year = event.date.year
        if year not in KEY_YEARS:
            continue

        qualitative_positive = (
            (event.ripeness_status is not None and event.ripeness_status.value == "RIPE")
            or (event.zopa_size is not None and event.zopa_size.value == "WIDE")
        )

        prev = _most_recent_year_with_data(db, serbia_id, kosovo_id, year)
        window_score = calculate_window_score(db, serbia_id, kosovo_id, year, prev)
        quantitative_positive = (
            window_score is not None and window_score >= BEST_MOMENT_THRESHOLD
        )

        if qualitative_positive and quantitative_positive:
            confidence = "HIGH"
        elif qualitative_positive or quantitative_positive:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        results.append({
            "event_id": event.id,
            "title": event.title,
            "year": year,
            "qualitative_positive": qualitative_positive,
            "window_score": window_score,
            "confidence": confidence,
        })

    return results