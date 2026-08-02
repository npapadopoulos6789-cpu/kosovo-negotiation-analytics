"""
Seed script -- γεμίζει τη ΒΔ με τα δεδομένα της διπλωματικής.
Τρέχεται με: python -m app.scripts.seed

ΠΗΓΕΣ:
- Economic (GDP growth, unemployment): World Bank API, πραγματικά δεδομένα
- Military (% GDP δαπανών): World Bank API (πηγή SIPRI), πραγματικά δεδομένα
  ΓΙΑ ΤΗ ΣΕΡΒΙΑ. Για το Κόσοβο δεν υπάρχει API δεδομένο -- χρησιμοποιείται
  τεκμηριωμένη εκτίμηση έντασης στρατιωτικής παρουσίας (KFOR/NATO), βάσει
  του αφηγηματικού κειμένου της διπλωματικής.
- Social (Freedom House score): ανάγνωση από το Γράφημα 1.11 της
  διπλωματικής (Nations in Transit, δεν υπάρχει δημόσιο API)
- Kosovo unemployment (1999-2008): ανάγνωση από το Γράφημα 1.5 της
  διπλωματικής (ILO/World Bank Open Data, το ίδιο API δεν καλύπτει
  αυτή την περίοδο για το Κόσοβο)
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
    """
    Πραγματικά δεδομένα από World Bank API (Serbia πλήρη, Kosovo μερικά) +
    δεδομένα διαβασμένα από τα γραφήματα της διπλωματικής, ρητά σημειωμένα.
    """
    serbia_id = country_ids["Serbia"]
    kosovo_id = country_ids["Kosovo"]

    indicators = [
        # ============ SERBIA — ECONOMIC (World Bank API, πραγματικά) ============
        (serbia_id, "ECONOMIC", "GDP_growth", 1999, -10.33, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2005, 5.90, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2007, 7.83, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2008, 5.16, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2013, 0.45, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2023, 3.75, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),

        # ============ SERBIA — MILITARY (World Bank API, πηγή SIPRI, πραγματικά) ============
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 1999, 3.53, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2005, 2.22, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2007, 2.16, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2008, 2.05, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2013, 1.85, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),
        (serbia_id, "MILITARY", "military_expenditure_pct_gdp", 2023, 2.21, "%GDP", "World Bank API / SIPRI (MS.MIL.XPND.GD.ZS)"),

        # ============ SERBIA — SOCIAL (Γράφημα 1.11 διπλωματικής) ============
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 39.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 53.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2008, 53.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 63.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 43.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),

        # ============ KOSOVO — ECONOMIC (World Bank API όπου διαθέσιμο) ============
        (kosovo_id, "ECONOMIC", "GDP_growth", 2013, 5.34, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        (kosovo_id, "ECONOMIC", "GDP_growth", 2023, 4.07, "%", "World Bank API (NY.GDP.MKTP.KD.ZG)"),
        # 1999/2005/2007/2008: ΔΕΝ υπάρχουν στο World Bank API (πριν το 2009) -- σκόπιμα ΔΕΝ εικάζουμε

        # ============ KOSOVO — MILITARY (τεκμηριωμένη εκτίμηση) ============
        # Δεν υπάρχει δεδομένο κρατικών στρατιωτικών δαπανών Κοσόβου στο WB API.
        # Εναλλακτικά, δείκτης έντασης ξένης στρατιωτικής παρουσίας (KFOR/NATO),
        # βάσει του αφηγηματικού κειμένου της διπλωματικής (§ NATO intervention,
        # KFOR mandate). 0-100, όπου 100 = μέγιστη ένταση/παρουσία.
        (kosovo_id, "MILITARY", "troop_presence_index", 1999, 90.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2005, 55.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2007, 45.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2008, 40.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2013, 25.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2023, 15.0, "index_score", "Researcher estimate βάσει NATO/KFOR narrative στη διπλωματική"),

        # ============ KOSOVO — SOCIAL (Γράφημα 1.5 για ανεργία, Γράφημα 1.11 για FH) ============
        # ΣΗΜΕΙΩΣΗ: χρησιμοποιούμε freedom_house_score (0-100) ως τον social δείκτη,
        # συνεπές με τη Σερβία -- η ανεργία Κοσόβου (Γράφημα 1.5) υπάρχει σαν επιπλέον
        # πληροφορία αλλά ΔΕΝ μπαίνει εδώ γιατί δεν έχουμε NORMALIZATION_RANGES γι'
        # αυτήν ακόμα (θα προστεθεί αν χρειαστεί αργότερα).
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2005, 28.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2007, 29.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2008, 30.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 30.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 38.0, "index_score", "Freedom House Nations in Transit, Γράφημα 1.11 διπλωματικής"),
    ]

    for country_id, category, itype, year, value, unit, source in indicators:
        indicator_service.create_indicator(
            db,
            IndicatorCreate(
                country_id=country_id, category=category, indicator_type=itype,
                year=year, value=value, unit=unit, source=source, is_verified=True,
            ),
        )
    print(f"  Indicators: {len(indicators)} εγγραφές")


def seed_events(db, country_ids: dict):
    events = [
        dict(
            title="Rambouillet Talks", date="1999-02-06",
            description="Διαπραγματεύσεις στο Rambouillet της Γαλλίας, οι οποίες απέτυχαν να καταλήξουν σε συμφωνία.",
            zopa_size="NARROW",
            zopa_reasoning="Πανομοιότυπες, μη συμβατές κόκκινες γραμμές: η Σερβία ζητούσε εδαφική ακεραιότητα, το Κόσοβο πλήρη ανεξαρτησία.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Καμία πλευρά δεν αντιλαμβανόταν αμοιβαία επώδυνο αδιέξοδο.",
            batna_side_a="Στρατιωτική ισχύς, στήριξη Ρωσίας/Κίνας",
            batna_side_b="Διεθνής υποστήριξη ΝΑΤΟ/ΟΗΕ",
            red_lines_side_a="Εδαφική ακεραιότητα Σερβίας",
            red_lines_side_b="Πλήρης ανεξαρτησία Κοσόβου",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=5, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("NATO", "MEDIATOR"), ("UN", "MEDIATOR")],
        ),
        dict(
            title="UN Security Council Resolution 1244", date="1999-06-10",
            description="Ψήφισμα του Συμβουλίου Ασφαλείας του ΟΗΕ που τερμάτισε τις εχθροπραξίες.",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=2, military_weight=6, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "GUARANTOR"), ("NATO", "GUARANTOR")],
        ),
        dict(
            title="UNMIK Interim Administration", date="1999-06-12",
            description="Περίοδος προσωρινής διοίκησης του Κοσόβου υπό τον ΟΗΕ (1999-2005).",
            ripeness_status="EMERGING",
            ripeness_reasoning="Σταδιακή δημιουργία τοπικών θεσμών, χωρίς ακόμα ώριμες συνθήκες για οριστική συμφωνία.",
            economic_weight=4, military_weight=3, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR")],
        ),
        dict(
            title="Ahtisaari Plan", date="2007-03-26",
            description="Πρόταση του ειδικού απεσταλμένου του ΟΗΕ Martti Ahtisaari για επιτηρούμενη ανεξαρτησία.",
            zopa_size="MODERATE", negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=4, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR"), ("EU", "MEDIATOR")],
        ),
        dict(
            title="Unilateral Declaration of Independence", date="2008-02-17",
            description="Μονομερής ανακήρυξη ανεξαρτησίας του Κοσόβου.",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=3, social_weight=4,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("USA", "GUARANTOR"), ("EU", "GUARANTOR")],
        ),
        dict(
            title="Brussels Agreement", date="2013-04-19",
            description="Συμφωνία Βρυξελλών για την ομαλοποίηση των σχέσεων, με τη μεσολάβηση της ΕΕ.",
            zopa_size="WIDE",
            zopa_reasoning="Η Σερβία αποδέχτηκε ενσωμάτωση σερβικών κοινοτήτων στο σύστημα του Κοσόβου.",
            ripeness_status="RIPE",
            ripeness_reasoning="Η ευρωπαϊκή προοπτική της Σερβίας λειτούργησε ως ισχυρό κίνητρο ωρίμανσης, κατά Zartman.",
            batna_side_a="Αποδυναμωμένη BATNA λόγω οικονομικής κρίσης και ανάγκης ενταξιακής πορείας στην ΕΕ",
            batna_side_b="Σταθεροποιημένη διεθνής αναγνώριση",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=5, military_weight=2, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR")],
        ),
        dict(
            title="Ohrid Agreement", date="2023-03-18",
            description="Συμφωνία της Οχρίδας για την εφαρμογή του Βασικού Σχεδίου ομαλοποίησης σχέσεων.",
            zopa_size="MODERATE", negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=4, military_weight=2, social_weight=4,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR"), ("USA", "MEDIATOR")],
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
        print("\n✅ Seed ολοκληρώθηκε επιτυχώς!")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()