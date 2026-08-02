"""
Seed script -- γεμίζει τη ΒΔ με τα πραγματικά δεδομένα της διπλωματικής.
Τρέχεται ΜΙΑ φορά (ή όποτε θέλουμε να "ξαναφτιάξουμε" τα δεδομένα από την
αρχή), με: python -m app.scripts.seed
"""
from app.core.database import SessionLocal
from app.services import country as country_service
from app.services import indicator as indicator_service
from app.services import negotiation_event as event_service
from app.schemas.country import CountryCreate
from app.schemas.indicator import IndicatorCreate
from app.schemas.negotiation_event import NegotiationEventCreate, ParticipantCreate


def seed_countries(db):
    """
    Οι δύο πρωταγωνιστές (με πλήρη Indicator data) + οι διεθνείς δρώντες
    (μόνο context, χωρίς δικά τους Indicators).
    """
    countries_data = [
        # (name, actor_type, geopolitical_bloc, recognized_kosovo, country_code)
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
                name=name,
                actor_type=actor_type,
                geopolitical_bloc=bloc,
                recognized_kosovo=recognized,
                country_code=code,
            ),
        )
        created[name] = country.id
        print(f"  Country: {name} (id={country.id})")
    return created


def seed_indicators(db, country_ids: dict):
 
    serbia_id = country_ids["Serbia"]
    kosovo_id = country_ids["Kosovo"]

    indicators = [
        # Serbia -- Economic (GDP growth %)
        (serbia_id, "ECONOMIC", "GDP_growth", 1999, -18.0, "%", "IMF, ενδεικτικό"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2005, 5.5, "%", "IMF, ενδεικτικό"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2013, 2.6, "%", "IMF, ενδεικτικό"),
        (serbia_id, "ECONOMIC", "GDP_growth", 2023, 2.5, "%", "IMF, ενδεικτικό"),
        # Serbia -- Social (Freedom House score, 0-100)
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 1999, 38.0, "index_score", "Freedom House, ενδεικτικό"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 63.0, "index_score", "Freedom House, ενδεικτικό"),
        (serbia_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 59.0, "index_score", "Freedom House, ενδεικτικό"),
        # Kosovo -- Economic
        (kosovo_id, "ECONOMIC", "GDP_growth", 2005, 3.9, "%", "World Bank, ενδεικτικό"),
        (kosovo_id, "ECONOMIC", "GDP_growth", 2013, 3.4, "%", "World Bank, ενδεικτικό"),
        (kosovo_id, "ECONOMIC", "GDP_growth", 2023, 4.0, "%", "World Bank, ενδεικτικό"),
        # Kosovo -- Social
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2013, 47.0, "index_score", "Freedom House, ενδεικτικό"),
        (kosovo_id, "SOCIAL_UNREST", "freedom_house_score", 2023, 55.0, "index_score", "Freedom House, ενδεικτικό"),
        # Military -- π.χ. KFOR παρουσία (ενδεικτικός δείκτης έντασης 0-100)
        (kosovo_id, "MILITARY", "troop_presence_index", 1999, 90.0, "index_score", "NATO/KFOR, ενδεικτικό"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2013, 25.0, "index_score", "NATO/KFOR, ενδεικτικό"),
        (kosovo_id, "MILITARY", "troop_presence_index", 2023, 15.0, "index_score", "NATO/KFOR, ενδεικτικό"),
    ]

    for country_id, category, itype, year, value, unit, source in indicators:
        indicator_service.create_indicator(
            db,
            IndicatorCreate(
                country_id=country_id,
                category=category,
                indicator_type=itype,
                year=year,
                value=value,
                unit=unit,
                source=source,
                is_verified=True,
            ),
        )
    print(f"  Indicators: {len(indicators)} εγγραφές")


def seed_events(db, country_ids: dict):
    """
    Τα 7 βασικά διαπραγματευτικά γεγονότα, με τη δομημένη ανάλυση από τη
    διπλωματική (παράφραση -- ΝΑ ΑΝΤΙΚΑΤΑΣΤΑΘΕΙ με τη δική σου ακριβή
    διατύπωση όπου χρειάζεται).
    """
    events = [
        dict(
            title="Rambouillet Talks",
            date="1999-02-06",
            description="Διαπραγματεύσεις στο Rambouillet της Γαλλίας, οι οποίες απέτυχαν να καταλήξουν σε συμφωνία.",
            zopa_size="NARROW",
            zopa_reasoning="Πανομοιότυπες, μη συμβατές κόκκινες γραμμές: η Σερβία ζητούσε εδαφική ακεραιότητα, το Κόσοβο πλήρη ανεξαρτησία.",
            ripeness_status="NOT_RIPE",
            ripeness_reasoning="Καμία πλευρά δεν αντιλαμβανόταν αμοιβαία επώδυνο αδιέξοδο (mutually hurting stalemate).",
            batna_side_a="Στρατιωτική ισχύς, στήριξη Ρωσίας/Κίνας",
            batna_side_b="Διεθνής υποστήριξη ΝΑΤΟ/ΟΗΕ",
            red_lines_side_a="Εδαφική ακεραιότητα Σερβίας",
            red_lines_side_b="Πλήρης ανεξαρτησία Κοσόβου",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=5, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("NATO", "MEDIATOR"), ("UN", "MEDIATOR")],
        ),
        dict(
            title="UN Security Council Resolution 1244",
            date="1999-06-10",
            description="Ψήφισμα του Συμβουλίου Ασφαλείας του ΟΗΕ που τερμάτισε τις εχθροπραξίες.",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=2, military_weight=6, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "GUARANTOR"), ("NATO", "GUARANTOR")],
        ),
        dict(
            title="UNMIK Interim Administration",
            date="1999-06-12",
            description="Περίοδος προσωρινής διοίκησης του Κοσόβου υπό τον ΟΗΕ (1999-2005).",
            ripeness_status="EMERGING",
            ripeness_reasoning="Σταδιακή δημιουργία τοπικών θεσμών, χωρίς ακόμα ώριμες συνθήκες για οριστική συμφωνία.",
            economic_weight=4, military_weight=3, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR")],
        ),
        dict(
            title="Ahtisaari Plan",
            date="2007-03-26",
            description="Πρόταση του ειδικού απεσταλμένου του ΟΗΕ Martti Ahtisaari για επιτηρούμενη ανεξαρτησία.",
            zopa_size="MODERATE",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=4, military_weight=4, social_weight=2,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("UN", "MEDIATOR"), ("EU", "MEDIATOR")],
        ),
        dict(
            title="Unilateral Declaration of Independence",
            date="2008-02-17",
            description="Μονομερής ανακήρυξη ανεξαρτησίας του Κοσόβου.",
            negotiation_type="DISTRIBUTIVE",
            economic_weight=3, military_weight=3, social_weight=4,
            participants=[("Kosovo", "PARTY"), ("Serbia", "PARTY"), ("USA", "GUARANTOR"), ("EU", "GUARANTOR")],
        ),
        dict(
            title="Brussels Agreement",
            date="2013-04-19",
            description="Συμφωνία Βρυξελλών για την ομαλοποίηση των σχέσεων, με τη μεσολάβηση της ΕΕ.",
            zopa_size="WIDE",
            zopa_reasoning="Η Σερβία αποδέχτηκε ενσωμάτωση σερβικών κοινοτήτων στο σύστημα του Κοσόβου, ένδειξη ευρύτερης ζώνης συμφωνίας.",
            ripeness_status="RIPE",
            ripeness_reasoning="Η ευρωπαϊκή προοπτική της Σερβίας λειτούργησε ως ισχυρό κίνητρο ωρίμανσης, κατά Zartman.",
            batna_side_a="Αποδυναμωμένη BATNA λόγω οικονομικής κρίσης και ανάγκης ενταξιακής πορείας στην ΕΕ",
            batna_side_b="Σταθεροποιημένη διεθνής αναγνώριση",
            negotiation_type="INTEGRATIVE_WIN_WIN",
            economic_weight=5, military_weight=2, social_weight=3,
            participants=[("Serbia", "PARTY"), ("Kosovo", "PARTY"), ("EU", "MEDIATOR")],
        ),
        dict(
            title="Ohrid Agreement",
            date="2023-03-18",
            description="Συμφωνία της Οχρίδας για την εφαρμογή του Βασικού Σχεδίου ομαλοποίησης σχέσεων.",
            zopa_size="MODERATE",
            negotiation_type="INTEGRATIVE_WIN_WIN",
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
        event_service.create_event(
            db, NegotiationEventCreate(**event_data, participants=participants)
        )
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