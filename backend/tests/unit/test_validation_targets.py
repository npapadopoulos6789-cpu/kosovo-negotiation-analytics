"""
Validation tests: επιβεβαιώνουν αν ο ντετερμινιστικός analytics πυρήνας
αναπαράγει τα ποιοτικά συμπεράσματα του Κεφ. 4 της διπλωματικής
(SEED_DATA_SPEC.md §4.1, προτάσεις P1-P5).

ΔΙΑΦΟΡΕΤΙΚΟ από τα υπόλοιπα unit tests: χρησιμοποιεί πραγματική σύνδεση
στην ήδη-γεμάτη ΒΔ (SessionLocal, όχι mocked/SQLite in-memory) -- τρέξε
πρώτα `python -m app.scripts.seed` πριν αυτά τα tests, αλλιώς θα αποτύχουν
λόγω απουσίας δεδομένων.

Κάλυψη δεδομένων (βλ. PROJECT_STATUS.md για πλήρη πίνακα): πλήρες
multidimensional Power Index (economic+military+social) υπολογίσιμο ΜΟΝΟ
για {2005, 2007, 2013, 2023} και στις δύο χώρες -- το Freedom House
(social) δεν έχει καμία τιμή πριν το 2005. Όπου το πρωτότυπο P1-P5 της
διπλωματικής αναφέρεται σε έτη εκτός αυτού του εύρους, το test rescope-άρεται
στο πλησιέστερο διαθέσιμο εύρος -- σημειωμένο ρητά στο docstring κάθε test.
"""
import pytest

from app.core.database import SessionLocal
from app.repositories import country as country_repository
from app.services import analytics as analytics_service


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def serbia_id(db):
    return country_repository.get_by_name(db, "Serbia").id


@pytest.fixture(scope="module")
def kosovo_id(db):
    return country_repository.get_by_name(db, "Kosovo").id


# ---------------------------------------------------------------------------
# P1 -- "Η ισχύς της Σερβίας καταρρέει το 1999"
# ---------------------------------------------------------------------------

def test_serbia_economic_collapse_1998_1999(db, serbia_id):
    """
    Το πλήρες multidimensional Power Index δεν είναι υπολογίσιμο για
    1998/1999 λόγω απουσίας military data (1998) και social/Freedom
    House data (και τα δύο έτη, FH ξεκινάει 2005). Αυτό το test
    επιβεβαιώνει την οικονομική κατάρρευση (P1 της διπλωματικής) στο
    επίπεδο δεδομένων που όντως διαθέτουμε -- βλ. README Limitations
    για πλήρη συζήτηση κάλυψης δεδομένων.
    """
    score_1998 = analytics_service.get_category_score(db, serbia_id, 1998, "ECONOMIC")
    score_1999 = analytics_service.get_category_score(db, serbia_id, 1999, "ECONOMIC")

    assert score_1998 is not None
    assert score_1999 is not None
    assert score_1999 < score_1998


def test_full_power_index_unavailable_pre_2005(db, serbia_id):
    """
    ΑΝΑΜΕΝΟΜΕΝΗ συμπεριφορά, ΟΧΙ bug -- τεκμηριωμένο όριο δεδομένων.
    Το Freedom House (social) δεν έχει καμία τιμή πριν το 2005, οπότε το
    πλήρες Power Index (economic+military+social) γυρνάει None για κάθε
    έτος πριν το 2005, ακόμα κι όταν economic/military δεδομένα υπάρχουν
    (π.χ. το 1999 έχει και economic ΚΑΙ military, αλλά όχι social).
    """
    assert analytics_service.calculate_power_index(db, serbia_id, 1998) is None
    assert analytics_service.calculate_power_index(db, serbia_id, 1999) is None


# ---------------------------------------------------------------------------
# P2 -- "Η Σερβία ανασυγκροτείται μετά το 2000"
# ---------------------------------------------------------------------------

def test_serbia_recovery_trend(db, serbia_id):
    """
    Στο πρωτότυπο P2: ανοδική τάση Power Index 2000-2008. Πλήρες Power
    Index δεν υπάρχει στο 2000 ή στο 2008 (βλ. κάλυψη δεδομένων) -- η μόνη
    σύγκριση με πλήρη δεδομένα μέσα σε αυτό το εύρος είναι 2005 -> 2007.
    """
    pi_2005 = analytics_service.calculate_power_index(db, serbia_id, 2005)
    pi_2007 = analytics_service.calculate_power_index(db, serbia_id, 2007)

    assert pi_2005 is not None
    assert pi_2007 is not None
    assert pi_2007 > pi_2005


# ---------------------------------------------------------------------------
# P4 -- "Η ισχύς του Κοσόβου ενισχύεται" (Power Gap στενεύει)
# ---------------------------------------------------------------------------

def test_power_gap_narrows_2013_to_2023(db, serbia_id, kosovo_id):
    """
    Στο πρωτότυπο P4: μείωση Power Gap μετά το 2018. Το 2018/2020 δεν
    έχουν πλήρη δεδομένα και για τις δύο χώρες (βλ. κάλυψη δεδομένων) --
    η πλησιέστερη διαθέσιμη σύγκριση είναι 2013 vs 2023.
    """
    gap_2013 = analytics_service.calculate_power_gap(db, serbia_id, kosovo_id, 2013)
    gap_2023 = analytics_service.calculate_power_gap(db, serbia_id, kosovo_id, 2023)

    assert gap_2013 is not None
    assert gap_2023 is not None
    assert gap_2023 < gap_2013


# ---------------------------------------------------------------------------
# P3 -- "Το 2013 είναι η στιγμή ωρίμανσης" (Zartman mutually hurting stalemate)
# ---------------------------------------------------------------------------

def test_2013_is_optimal_window(db, serbia_id, kosovo_id):
    """
    Μέχρι τη διόρθωση bug στο `previous_year` (2026-08-03, βλ.
    `_most_recent_year_with_data` στο analytics.py), το
    `find_optimal_mutual_compromise_period` επέστρεφε 2023
    (window_score 59.07) αντί για 2013 -- επειδή χρησιμοποιούσε σαν
    "προηγούμενο έτος" απλά το προηγούμενο στοιχείο της αραιής λίστας
    KEY_YEARS (συχνά χωρίς δεδομένα), μηδενίζοντας αθόρυβα το trend_score
    (30% βάρος στο Window Score). Μετά τη διόρθωση, το previous_year
    είναι το πιο πρόσφατο έτος με πραγματικά δεδομένα και για τις δύο
    χώρες -- το 2013 κερδίζει οριακά (61.98 vs 61.79 του 2023), και το
    P3 της διπλωματικής επιβεβαιώνεται.
    """
    result = analytics_service.find_optimal_mutual_compromise_period(db, serbia_id, kosovo_id)

    assert result is not None
    assert result["year"] == 2013


# ---------------------------------------------------------------------------
# P5 -- "Το Κόσοβο δεν έχει ανεξάρτητη BATNA" (ΔΕΝ επιβεβαιώνεται, τεκμηρίωση)
# ---------------------------------------------------------------------------

def test_kosovo_indicator_breakdown_documented(db, kosovo_id):
    """
    Καταγράφει (χωρίς normative assertion) τις τρεις category τιμές του
    Κοσόβου ανά έτος:

        year  economic  military  social
        2005  68.33     55.0      27.5
        2007  76.67     45.0      27.0
        2013  84.47     25.0      29.5
        2023  80.23     15.0      38.0

    P5 της αρχικής υπόθεσης (economic+military χαμηλό) ΔΕΝ επιβεβαιώνεται
    από τον τρέχοντα δείκτη -- το economic component μετράει ρυθμό
    ανάπτυξης (όπου μικρές οικονομίες βαθμολογούνται ψηλά ανεξαρτήτως
    απόλυτου μεγέθους), όχι απόλυτη οικονομική ισχύ. Το military
    (troop_presence) έχει αμφίσημη κατεύθυνση ερμηνείας. Αυτό είναι
    τεκμηριωμένος περιορισμός του normalization σχεδιασμού, βλ. README
    Limitations -- ΔΕΝ αποτελεί απόδειξη ότι η δομική αδυναμία δεν
    υπάρχει, μόνο ότι ο τρέχων δείκτης δεν την πιάνει.
    """
    breakdown = {
        year: {
            "economic": analytics_service.get_category_score(db, kosovo_id, year, "ECONOMIC"),
            "military": analytics_service.get_category_score(db, kosovo_id, year, "MILITARY"),
            "social": analytics_service.get_category_score(db, kosovo_id, year, "SOCIAL_UNREST"),
        }
        for year in (2005, 2007, 2013, 2023)
    }

    # Καταγραφή, όχι κρίση -- επιβεβαιώνουμε ότι οι τιμές είναι ακριβώς
    # αυτές που παρατηρήθηκαν, ΟΧΙ ότι "είναι χαμηλές/υψηλές"
    assert breakdown == {
        2005: {"economic": 68.33, "military": 55.0, "social": 27.5},
        2007: {"economic": 76.67, "military": 45.0, "social": 27.0},
        2013: {"economic": 84.47, "military": 25.0, "social": 29.5},
        2023: {"economic": 80.23, "military": 15.0, "social": 38.0},
    }
