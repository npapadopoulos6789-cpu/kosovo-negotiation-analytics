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
(social) δεν έχει καμία τιμή πριν το 2005 (και είναι odd-years only, άρα
ούτε το 2008 έχει πλήρες κάλυμμα). Όπου το πρωτότυπο P1-P5 της
διπλωματικής αναφέρεται σε έτη εκτός αυτού του εύρους, το test rescope-άρεται
στο πλησιέστερο διαθέσιμο εύρος -- σημειωμένο ρητά στο docstring κάθε test.

ΜΕΘΟΔΟΛΟΓΙΚΗ ΑΝΑΘΕΩΡΗΣΗ 2026-08-21 (βλ. SEED_SOURCE.md/PROJECT_STATUS.md
για το πλήρες change-log): ECONOMIC category = GDP_growth + GDP_absolute_usd
(λογαριθμική κλίμακα) + unemployment_rate μαζί. MILITARY category:
Kosovo military_expenditure_pct_gdp (ΙΔΙΟ indicator/πηγή με Serbia, World
Bank/SIPRI) αντί για troop_presence_index (context-only πλέον) -- 1999/
2005/2007 = 0.0, τεκμηριωμένο ιστορικό γεγονός (KSF ιδρύθηκε Ιαν 2009,
όχι εκτίμηση κενού). unemployment_rate direction bug διορθώθηκε
(LOWER_IS_BETTER). Το log-scale εύρος ($1B-$100B) ελέγχθηκε για ευστάθεια
με εναλλακτικό, εξίσου υπερασπίσιμο εύρος ($500M-$200B, committed πριν
το τρέξιμο) -- το P3 αποτέλεσμα (2013 optimal) έμεινε robust και στα δύο.

ΔΕΥΤΕΡΗ ΜΕΘΟΔΟΛΟΓΙΚΗ ΑΝΑΘΕΩΡΗΣΗ 2026-08-21 (ίδια ημέρα, μετά έγκριση):
προστέθηκαν FDI_net_inflows_pct_gdp (4ο ECONOMIC indicator, World Bank
BX.KLT.DINV.WD.GD.ZS, θετική κατεύθυνση) και military_expenditure_usd (2ο
MILITARY indicator, World Bank/SIPRI MS.MIL.XPND.CD, λογαριθμική κλίμακα
$500K-$5δισ) -- πλήρες σκεπτικό/πηγές: SEED_SOURCE.md §3.1/§3.6/§3.7. Όλα
τα P1-P4 assertions (κατεύθυνση, όχι ακριβείς τιμές) παρέμειναν robust μετά
την προσθήκη -- μόνο τα απόλυτα νούμερα άλλαξαν, ενημερώθηκαν παρακάτω.

ΤΡΙΤΗ ΜΕΘΟΔΟΛΟΓΙΚΗ ΑΝΑΘΕΩΡΗΣΗ 2026-08-21 (διαφορετική ημέρα): διόρθωση
κατεύθυνσης στο 20% κοινωνικό συστατικό του Window Score --
`calculate_social_stability_score` (πρώην `calculate_social_pressure_score`)
πλέον επιστρέφει το ακατέργαστο SOCIAL_UNREST category score (σταθερότητα
συνεισφέρει θετικά), όχι το `100 - score` (αστάθεια συνεισφέρει θετικά)
που ίσχυε πριν -- πλήρες σκεπτικό/παραπομπή στη διπλωματική (Two-Level
Game του Putnam): SEED_SOURCE.md §10. Επηρεάζει ΜΟΝΟ το Window Score (P3,
regression test) -- το P1/P2/P4/P5 (Power Index/Power Gap, δεν αγγίζουν το
Window Score) παρέμειναν byte-ίδια, επιβεβαιωμένο.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.repositories import country as country_repository
from app.services import analytics as analytics_service
from main import app


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

    Μεθοδολογική σημείωση 2026-08-21: το 1998 ΔΕΝ έχει GDP_absolute_usd
    (η σειρά μας ξεκινά 1999), άρα το 1998 scored set = {GDP_growth,
    unemployment_rate} ενώ το 1999 = {GDP_growth, unemployment_rate,
    GDP_absolute_usd} -- ασύμμετρα σύνολα. Επαληθεύτηκε ρητά (like-for-
    like σύγκριση, μόνο κοινοί δείκτες) ότι η κατεύθυνση ΔΕΝ είναι
    artifact της ασυμμετρίας: 1998=80.82 και με τα δύο σύνολα (είναι ήδη
    υποσύνολο), 1999=58.46 (full) / 54.7 (like-for-like) -- και στις δύο
    περιπτώσεις 1999 < 1998, το GDP_growth (-10.33% έναντι +5.34%)
    κουβαλάει το πραγματικό σήμα κατάρρευσης.
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
    (π.χ. το 1999 έχει και economic ΚΑΙ military -- military πλέον 0.0,
    τεκμηριωμένο ιστορικό γεγονός, όχι κενό -- αλλά όχι social).
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

    Μετά τη μεθοδολογική αναθεώρηση 2026-08-21 (combined ECONOMIC,
    log-scale GDP_absolute_usd): 2005=51.79 -> 2007=54.5, ίδια κατεύθυνση
    με πριν, νέα απόλυτα επίπεδα.

    Μετά τη ΔΕΥΤΕΡΗ αναθεώρηση ίδιας ημέρας (+FDI_net_inflows_pct_gdp,
    +military_expenditure_usd): 2005=61.74 -> 2007=62.29 -- ίδια
    κατεύθυνση, robust στην προσθήκη των δύο νέων indicators.
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

    Μεθοδολογική αναθεώρηση 2026-08-21: gap 2013=14.61 -> 2023=11.53,
    στενεύει -- επιβεβαιώνεται. (Ενδιάμεσα, με μόνο GDP_absolute_usd
    γραμμικό αντί για GDP_growth+GDP_absolute_usd log-scale, το gap
    ΔΙΕΥΡΥΝΟΤΑΝ αντί να στενεύει -- artifact γραμμικής συμπίεσης του
    Kosovo GDP component, βλ. PROJECT_STATUS.md. Διορθώθηκε.)

    Μετά τη ΔΕΥΤΕΡΗ αναθεώρηση ίδιας ημέρας (+FDI, +military_expenditure_usd):
    gap 2013=17.76 -> 2023=13.8 -- εξακολουθεί να στενεύει, robust.
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
    `find_optimal_mutual_compromise_period` επέστρεφε 2023 αντί για 2013
    -- επειδή χρησιμοποιούσε σαν "προηγούμενο έτος" απλά το προηγούμενο
    στοιχείο της αραιής λίστας KEY_YEARS, μηδενίζοντας αθόρυβα το
    trend_score.

    Μεθοδολογική αναθεώρηση 2026-08-21 -- ΔΕΥΤΕΡΗ φορά που το 2013 χάθηκε
    και ξαναβρέθηκε, διαφορετική αιτία: όταν το ECONOMIC category έγινε
    (προσωρινά) μόνο GDP_absolute_usd γραμμικό, και όταν το Kosovo
    MILITARY ήταν None για 1999/2005/2007 (κανένα KSF spending record πριν
    το 2008), το `_most_recent_year_with_data` δεν έβρισκε ΚΑΝΕΝΑ έγκυρο
    previous_year για το 2013 (κανένα προγενέστερο KEY_YEAR με πλήρη
    Kosovo δεδομένα) -- το 2013 έχανε ΟΛΟΚΛΗΡΟ το trend_score (30% βάρος),
    το 2023 (previous_year=2013, έγκυρο) όχι. Διορθώθηκε με: (α) combined
    ECONOMIC (GDP_growth+GDP_absolute_usd log-scale+unemployment_rate),
    (β) Kosovo military_expenditure_pct_gdp=0.0 για 1999/2005/2007
    (τεκμηριωμένο ιστορικό γεγονός -- KSF ιδρύθηκε Ιαν 2009, βλ.
    SEED_SOURCE.md), το οποίο δίνει στο 2013 έγκυρο previous_year=2007.

    Αποτέλεσμα: 2013=56.75 (previous_year=2007) vs 2023=56.13
    (previous_year=2013) -- 2013 κερδίζει, στενό περιθώριο (0.62).
    ΕΛΕΓΧΘΗΚΕ ΕΥΣΤΑΘΕΙΑ: με εναλλακτικό, εξίσου υπερασπίσιμο log-scale
    εύρος για GDP_absolute_usd ($500M-$200B αντί για $1B-$100B, committed
    πριν το τρέξιμο ώστε να μην επιλεγεί για συγκεκριμένο αποτέλεσμα) --
    2013=57.52 vs 2023=56.64, το 2013 κερδίζει ΚΑΙ εκεί (margin μεγαλώνει
    στα 0.88). Robust ως προς αυτή τη μεθοδολογική παράμετρο.

    Μετά τη ΔΕΥΤΕΡΗ αναθεώρηση ίδιας ημέρας (+FDI_net_inflows_pct_gdp,
    +military_expenditure_usd): 2013=55.79 (previous_year=2007) vs
    2023=55.0 (previous_year=2013) -- 2013 ΕΞΑΚΟΛΟΥΘΕΙ να κερδίζει, μάλιστα
    με μεγαλύτερο περιθώριο (0.79 αντί 0.62). Τρίτη ανεξάρτητη επιβεβαίωση
    της ευστάθειας του P3 εύρηματος.

    ΤΡΙΤΗ αναθεώρηση, ΔΙΑΦΟΡΕΤΙΚΗ ημέρα (2026-08-21) -- διόρθωση
    κατεύθυνσης στο 20% κοινωνικό συστατικό του Window Score (βλ.
    SEED_SOURCE.md §10): `calculate_social_stability_score` (πρώην
    `calculate_social_pressure_score`) πλέον επιστρέφει το ΑΚΑΤΕΡΓΑΣΤΟ
    (όχι αντεστραμμένο) SOCIAL_UNREST category score -- κοινωνική
    ΣΤΑΘΕΡΟΤΗΤΑ συνεισφέρει θετικά, όχι αστάθεια (η διπλωματική δείχνει
    ότι η αστάθεια αυξάνει το πολιτικό κόστος υποχώρησης, δυσκολεύει τη
    συμφωνία). Αποτέλεσμα: 2013=52.89 (previous_year=2007) vs 2023=51.2
    (previous_year=2013) -- 2013 ΕΞΑΚΟΛΟΥΘΕΙ να κερδίζει, με ΑΚΟΜΑ
    μεγαλύτερο περιθώριο (1.69 αντί 0.79). Τέταρτη ανεξάρτητη επιβεβαίωση
    της ευστάθειας του P3 εύρηματος -- το "2013 είναι η στιγμή ωρίμανσης"
    επιβίωσε τέσσερις ξεχωριστές μεθοδολογικές αναθεωρήσεις.
    """
    result = analytics_service.find_optimal_mutual_compromise_period(db, serbia_id, kosovo_id)

    assert result is not None
    assert result["year"] == 2013


# ---------------------------------------------------------------------------
# P5 -- "Το Κόσοβο δεν έχει ανεξάρτητη BATNA" (ΜΕΡΙΚΩΣ επιβεβαιώνεται)
# ---------------------------------------------------------------------------

def test_kosovo_indicator_breakdown_documented(db, kosovo_id):
    """
    Καταγράφει (χωρίς normative assertion πέρα από τα ίδια τα νούμερα) τις
    τρεις category τιμές του Κοσόβου ανά έτος. Δύο μεθοδολογικές
    αναθεωρήσεις 2026-08-21, ίδια ημέρα:

    1η (combined ECONOMIC + military_expenditure_pct_gdp αντί για
    troop_presence_index):

        year  economic  military  social
        2005  31.67     0.0       27.5
        2007  23.33     0.0       27.0
        2013  62.95     9.02      29.5
        2023  65.61     15.92     38.0

    2η, ΙΔΙΑ ημέρα (+FDI_net_inflows_pct_gdp στο ECONOMIC,
    +military_expenditure_usd στο MILITARY, μετά έγκριση):

        year  economic  military  social
        2005  31.67     0.0       27.5   (αμετάβλητο -- Kosovo FDI/
        2007  23.33     0.0       27.0   military_usd ξεκινούν 2008)
        2013  51.16     29.35     29.5
        2023  58.21     38.28     38.0

    2005/2007 αμετάβλητα -- το Kosovo FDI_net_inflows_pct_gdp ξεκινά 2008
    (καμία τιμή World Bank πριν) και το military_expenditure_usd έχει την
    ίδια τεκμηριωμένη 0.0 τιμή με το ήδη υπάρχον %GDP indicator για εκείνα
    τα έτη -- ο μέσος όρος δεν αλλάζει. 2013/2023 άλλαξαν αισθητά και στα
    δύο components.

    P5 της αρχικής υπόθεσης (economic+military χαμηλό) -- ΜΕΡΙΚΩΣ
    επιβεβαιώνεται, μεικτή εικόνα ανά component, ΙΔΙΑ ερμηνεία με πριν:
    - military: αυξήθηκε αισθητά το 2013/2023 (9.02->29.35, 15.92->38.28)
      μετά την προσθήκη του military_expenditure_usd -- λογικό, το Κόσοβο
      έχει σχετικά υψηλότερο score σε απόλυτη κλίμακα παρά σε ένταση
      προσπάθειας (μικρή οικονομία, ο λόγος Serbia/Kosovo σε απόλυτα $
      παραμένει τεράστιος αλλά η log-scale normalization τον συμπιέζει
      λιγότερο δραστικά απ' ό,τι φοβόμασταν) -- ΠΑΡΑΜΕΝΕΙ χαμηλότερο από
      Serbia (δεν ελέγχεται ρητά εδώ, βλ. Power Gap στο P4), απλά όχι πια
      "σχεδόν μηδέν" σε κάθε έτος όπως πριν.
    - economic: παρέμεινε μεικτό -- χαμηλό το 2005/2007, μέτριο το
      2013/2023 (51-58, ελαφρώς χαμηλότερο από πριν λόγω FDI ως 4ου
      ισοβαρή indicator -- το Kosovo FDI 2013/2023 είναι υψηλότερο από το
      Serbia αντίστοιχο έτος, οπότε αυτό καθαυτό ΘΑ ανέβαζε το economic
      score, αλλά η προσθήκη ενός επιπλέον ισοβαρή indicator αραιώνει την
      επιρροή του ήδη υψηλού GDP_absolute_usd -- καθαρό αποτέλεσμα οριακά
      χαμηλότερο, όχι artifact, βλ. get_category_score).
    Άρα: το military component της P5 ΕΞΑΚΟΛΟΥΘΕΙ να επιβεβαιώνεται
    (χαμηλότερο από Serbia σε κάθε έτος), αν και λιγότερο ακραία απ' ό,τι
    έδειχνε μόνο το %GDP· το economic ΟΧΙ ομοιόμορφα -- τεκμηριωμένος
    περιορισμός/εύρημα, όχι απόδειξη ότι η δομική αδυναμία δεν υπάρχει,
    βλ. README Limitations.
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
        2005: {"economic": 31.67, "military": 0.0, "social": 27.5},
        2007: {"economic": 23.33, "military": 0.0, "social": 27.0},
        2013: {"economic": 51.16, "military": 29.35, "social": 29.5},
        2023: {"economic": 58.21, "military": 38.28, "social": 38.0},
    }


# ---------------------------------------------------------------------------
# Regression -- GET /analytics/window-score/{year} πρέπει να συμφωνεί με τα
# άλλα δύο analytics endpoints για το ίδιο έτος (Finding A, 2026-08-03)
# ---------------------------------------------------------------------------

def test_window_score_endpoint_autocomputes_previous_year(serbia_id, kosovo_id):
    """
    Μέχρι αυτή τη διόρθωση, το GET /analytics/window-score/{year} απαιτούσε
    ο caller να δώσει ρητά previous_year -- αν δεν το έδινε, το trend_score
    (30% του Window Score) μηδενιζόταν αθόρυβα, ίδιο bug pattern με αυτό
    που διορθώθηκε στο find_optimal_mutual_compromise_period/
    find_best_moments (βλ. test_2013_is_optimal_window), αλλά η διόρθωση
    δεν είχε εφαρμοστεί σε αυτό το endpoint.

    Μετά τη διόρθωση, το endpoint αυτο-υπολογίζει το previous_year με τον
    ίδιο _most_recent_year_with_data helper όταν ο caller δεν το δίνει --
    οπότε τα δύο endpoints πρέπει τώρα να συμφωνούν. Τιμή ενημερωμένη
    2026-08-21 μετά τη μεθοδολογική αναθεώρηση (61.98 -> 56.75), ξανά μετά
    τη δεύτερη αναθεώρηση ίδιας ημέρας (+FDI, +military_expenditure_usd:
    56.75 -> 55.79), και ΞΑΝΑ μετά την τρίτη αναθεώρηση, διαφορετική ημέρα
    (διόρθωση κατεύθυνσης social component, 55.79 -> 52.89 -- βλ.
    test_2013_is_optimal_window για το πλήρες σκεπτικό).
    """
    client = TestClient(app)

    window_score_response = client.get(
        "/analytics/window-score/2013",
        params={"serbia_id": serbia_id, "kosovo_id": kosovo_id},
    )
    optimal_response = client.get(
        "/analytics/optimal-mutual-compromise",
        params={"serbia_id": serbia_id, "kosovo_id": kosovo_id},
    )

    assert window_score_response.status_code == 200
    assert optimal_response.status_code == 200
    assert window_score_response.json()["window_score"] == 52.89
    assert optimal_response.json()["window_score"] == 52.89
