# SEED_SOURCE.md — Ενοποιημένη πηγή δεδομένων από τη διπλωματική

**Πηγή ground truth:** Παπαδόπουλος, Ν.Α. (2024). *Η Γεωπολιτική και Οικονομική
Διάσταση της Ανεξαρτησίας του Κοσόβου: Διαπραγματεύσεις και Προοπτικές
Συνεργασίας*. ΟΠΑ, Τμήμα ΔΕΟΣ. DOI: 10.26219/heal.aueb.7305 (CC BY-SA 4.0)

Αυτό το αρχείο ενοποιεί σε ΜΙΑ πηγή αλήθειας ό,τι μέχρι τώρα ήταν σκορπισμένο σε
`SEED_DATA_SPEC.md`, `actors_seed_data(1).md`, `actors_seed_data.md` και τμήμα
του `thesis_seed_data.md`. Όλα τα παρακάτω είναι παράφραση της διπλωματικής, όχι
αυτούσιο κείμενο (εκτός όπου σημειώνεται ρητά ως απόσπασμα σε εισαγωγικά).
`is_verified=true` όπου προέρχονται από αυτή την έρευνα.

**Κατάσταση ως προς το `seed.py`:** οι ενότητες 2 (Events) και 3 (Indicators)
είναι το spec — το πραγματικό `seed.py` το ακολουθεί με κάποιες τεκμηριωμένες
αποκλίσεις/προσθήκες (π.χ. επιπλέον έτη ανεργίας Σερβίας, live World Bank τιμές
αντί εκτιμήσεων γραφήματος). Το ακριβές change-log αυτών των αποκλίσεων μένει
στο `PROJECT_STATUS.md` (ενότητα "Seed script") — δεν διπλασιάζεται εδώ.

---

## 1. Countries / Actors

Το `Country` model καλύπτει και κράτη και διεθνείς/θεσμικούς δρώντες
(`actor_type: STATE | INTERNATIONAL_ORG | MILITARY_ALLIANCE`). Η διπλωματική
(κεφ. 3.1+3.2) δίνει ουσιαστικό ρόλο σε 11 δρώντες πέρα από Serbia/Kosovo:

| Δρώντας | actor_type | geopolitical_bloc | recognized_kosovo | στηρίζει |
|---|---|---|---|---|
| Serbia | STATE | EAST/NEUTRAL | false | — |
| Kosovo | STATE | WEST | — | — |
| European Union | INTERNATIONAL_ORG | EU | mixed (5 μέλη όχι) | mediator, κλίση Kosovo |
| United States | STATE | WEST | true | Kosovo |
| Russia | STATE | EAST | false | Serbia |
| China ⚠ | STATE | EAST | false | Serbia |
| Albania | STATE | WEST | true | Kosovo |
| India | STATE | NEUTRAL | false | (μη-αναγνώριση 2008) |
| NATO | MILITARY_ALLIANCE | WEST | — | Kosovo (ασφάλεια) |
| United Nations (UNMIK) | INTERNATIONAL_ORG | NEUTRAL | — | ουδέτερος |
| OSCE / ΟΑΣΕ | INTERNATIONAL_ORG | NEUTRAL | — | ουδέτερος (εκλογές) |
| ICJ (προαιρετικό) | INTERNATIONAL_ORG | NEUTRAL | — | ουδέτερος (γνωμ. 2010) |

**Ενημέρωση 2026-08-20:** India, OSCE, ICJ προστέθηκαν πλέον στο `seed.py`
(και τα 12 Country rows -- Serbia/Kosovo + 10 -- seed-άρονται από το script,
`role_description` για όλους τους μη-πρωταγωνιστές). ⚠ = παραμένει μόνο για
China: υπάρχει ως Country row αλλά χωρίς κανένα `event_participants` link
(βλ. ενότητα 4) -- αυτό δεν άλλαξε.

**Γλώσσα δεδομένων (2026-08-20):** όλα τα πεδία δεδομένων (description,
batna, red_lines, zopa/ripeness reasoning, role_description, indicator
source) είναι πλέον στα Αγγλικά -- μεταφράστηκαν από το πρωτότυπο Ελληνικό
κείμενο της διπλωματικής χωρίς αλλαγή νοήματος/αριθμών/ημερομηνιών, γιατί
το UI του frontend είναι στα Αγγλικά. Αυτό το ίδιο το SEED_SOURCE.md
παραμένει Ελληνικό (dev-facing τεκμηρίωση, τα quotes παρακάτω στο έγγραφο
είναι το πρωτότυπο Ελληνικό κείμενο πριν τη μετάφραση -- ΔΕΝ ενημερώθηκαν
retroactively, βλ. `backend/app/scripts/seed.py` για τις τρέχουσες Αγγλικές
τιμές).

**Modeling σημείωση (από το πρωτότυπο):** KFOR/UNMIK/EULEX είναι *αποστολές* του
NATO/UN/EU αντίστοιχα, ΟΧΙ ξεχωριστοί δρώντες — μοντελοποιούνται ως ρόλος του
NATO/UN/EU σε συγκεκριμένα events, όχι ως νέες εγγραφές Country (αλλιώς
διπλασιάζονται οντότητες). Ισπανία/Ελλάδα/Κύπρος/Σλοβακία/Ρουμανία (τα 5 μέλη
ΕΕ που δεν αναγνωρίζουν το Κόσοβο) είναι context μέσα στο role_description της
ΕΕ, όχι ξεχωριστοί δρώντες.

**Σημείωση ονοματολογίας (από `SEED_DATA_SPEC.md` §1, για το README/Limitations):**
ο όρος «Σερβία» αφορά την ονομασία από το 2006 και μετά· ιστορικά τα δεδομένα
προ-2006 αφορούν την Ομοσπονδιακή Δημοκρατία της Γιουγκοσλαβίας (1992-2003) και
την Ένωση Σερβίας-Μαυροβουνίου (2003-2006). Η χρήση και των δύο όρων είναι
περιγραφική, χωρίς πολιτική προδιάθεση.

---

## 2. Negotiation Events

Δέκα γεγονότα (E1-E10) που καλύπτουν όλη τη διαπραγματευτική διαδρομή
(1989-2023). `side_a` = **Σερβία**, `side_b` = **Κόσοβο** (σταθερή σύμβαση
παντού). Τα βάρη (`economic_weight + military_weight + social_weight = 10`)
εκφράζουν ποιος παράγοντας κυριαρχούσε σε εκείνη τη φάση — ερευνητική κρίση
τεκμηριωμένη από το κείμενο.

### E1 — Κατάρρευση αυτονομίας & κλιμάκωση (1989-1998)
- **date:** 1989-03-28 | **negotiation_type:** DISTRIBUTIVE
- **zopa_size:** NARROW — οι θέσεις είναι αμοιβαία αποκλειόμενες, δεν υπάρχει επικάλυψη
- **ripeness_status:** NOT_RIPE — καμία πλευρά δεν θεωρεί το κόστος της σύγκρουσης υπερβολικό
- **batna_side_a (Σερβία):** Στρατιωτικός έλεγχος επί του εδάφους· κρατική κυριαρχία αναγνωρισμένη διεθνώς
- **batna_side_b (Κόσοβο):** Παράλληλες δομές Ρουγκόβα· μη βίαιη αντίσταση· διεθνής προβολή του ζητήματος
- **red_lines_side_a:** Καμία μορφή ανεξαρτησίας· διατήρηση εδαφικής ακεραιότητας
- **red_lines_side_b:** Επαναφορά του καθεστώτος αυτονομίας ως ελάχιστο
- **weights:** economic 2 / military 6 / social 2

### E2 — Rambouillet (Φεβ-Μαρ 1999)
- **date:** 1999-02-06 | **negotiation_type:** DISTRIBUTIVE
- **zopa_size:** NARROW — «πολύ περιορισμένη ZOPA, πανομοιότυπες κόκκινες γραμμές»
- **ripeness_status:** NOT_RIPE
- **batna_side_a:** Στρατιωτική ισχύς + βέτο Ρωσίας/Κίνας στο ΣΑ του ΟΗΕ
- **batna_side_b:** Διεθνής υποστήριξη ΝΑΤΟ και ΟΗΕ· προοπτική στρατιωτικής παρέμβασης υπέρ της
- **red_lines_side_a:** Όχι ξένα στρατεύματα στο έδαφός της· όχι ανεξαρτησία· εγγυήσεις για σερβική θρησκευτική/πολιτισμική κληρονομιά
- **red_lines_side_b:** Αποχώρηση σερβικών δυνάμεων· πορεία προς ανεξαρτησία
- **weights:** economic 2 / military 7 / social 1
- **outcome:** Αποτυχία → επιχείρηση Allied Force (24/3/1999, 78 ημέρες)

### E3 — Ψήφισμα ΟΗΕ 1244 (10 Ιουν 1999)
- **date:** 1999-06-10 | **negotiation_type:** INTEGRATIVE_WIN_WIN
- **zopa_size:** MODERATE — πρώτη φορά που εντοπίζεται σημείο αμοιβαίου κέρδους
- **ripeness_status:** RIPE — το κόστος της σύγκρουσης έχει γίνει συντριπτικό και για τις δύο πλευρές
- **batna_side_a:** Εξαντλημένη — κυρώσεις, βομβαρδισμοί, κατεστραμμένες υποδομές
- **batna_side_b:** Πλήρης εξάρτηση από ανθρωπιστική βοήθεια, αλλά με διεθνή στρατιωτική προστασία
- **red_lines_side_a:** Τυπική αναγνώριση ότι το Κόσοβο παραμένει μέρος της ΟΔΓ
- **red_lines_side_b:** Μη επιστροφή σερβικών δυνάμεων
- **weights:** economic 2 / military 5 / social 3
- **outcome:** Συμφωνία. Σκόπιμη ασάφεια ως προς το τελικό καθεστώς — αυτό ήταν το κλειδί που επέτρεψε τη σύγκλιση

### E4 — Standards Before Status (2003-2005)
- **date:** 2003-01-01 | **negotiation_type:** DISTRIBUTIVE
- **zopa_size:** NARROW | **ripeness_status:** NOT_RIPE
- **batna_side_a:** Οικονομική ανάκαμψη (~5% ΑΕΠ/έτος)· ρωσοκινεζική στήριξη· ευρωπαϊκή προοπτική ως μοχλός
- **batna_side_b:** Παρουσία UNMIK/KFOR· σταδιακή θεσμική οικοδόμηση
- **weights:** economic 4 / military 3 / social 3
- **outcome:** Καμία πρόοδος. Το 2004 ξέσπασαν εθνοτικές ταραχές (πυρπόληση σερβικών εκκλησιών/μοναστηριών, εκτοπισμοί, UNMIK έχασε προσωρινά τον έλεγχο) — οι κόκκινες γραμμές παρέμειναν αμετάβλητες

### E5 — Σχέδιο Ahtisaari (2007)
- **date:** 2007-03-26 | **negotiation_type:** DISTRIBUTIVE (η διπλωματική δίνει διπλή ετικέτα: INTEGRATIVE ως πρόθεση / DISTRIBUTIVE ως έκβαση — επιλέχθηκε βάσει έκβασης)
- **zopa_size:** NARROW — απόπειρα διεύρυνσης που απέτυχε
- **ripeness_status:** EMERGING
- **batna_side_a:** Βέτο Ρωσίας στο ΣΑ — το σχέδιο δεν έφτασε καν προς ψήφιση
- **batna_side_b:** Μονομερής ανακήρυξη με δυτική στήριξη
- **red_lines_side_a:** «Κάτι περισσότερο από αυτονομία, κάτι λιγότερο από ανεξαρτησία»
- **red_lines_side_b:** «Όχι κάτι λιγότερο από ανεξαρτησία»
- **weights:** economic 4 / military 2 / social 4
- **outcome:** Απόρριψη από Σερβία. Οι δύο θέσεις είναι κυριολεκτικά μη τεμνόμενες — ιδανικό παράδειγμα ZOPA=∅

### E6 — Μονομερής Ανακήρυξη Ανεξαρτησίας (17 Φεβ 2008)
- **date:** 2008-02-17 | **negotiation_type:** DISTRIBUTIVE
- **zopa_size:** NARROW | **ripeness_status:** NOT_RIPE
- **zopa_reasoning:** Καμία συμφωνία — μονομερής πράξη. >100 χώρες αναγνώρισαν, αλλά Ρωσία/Κίνα/Ινδία/Σερβία + 5 κράτη ΕΕ όχι. «Μερική αναγνώριση»
- **weights:** economic 3 / military 2 / social 5
- **outcome:** >100 αναγνωρίσεις· 5 κράτη-μέλη ΕΕ αρνούνται· γνωμοδότηση ICJ 2010 (ούτε νομιμοποιεί ούτε καταδικάζει)

### E7 — Συμφωνία Βρυξελλών (19 Απρ 2013) ⭐
- **date:** 2013-04-19 | **negotiation_type:** INTEGRATIVE_WIN_WIN
- **zopa_size:** WIDE — «η ZOPA είχε διευρυνθεί αρκετά σε σύγκριση με τα προηγούμενα χρόνια»
- **ripeness_status:** RIPE — **το κείμενο ονομάζει ρητά το 2013 «κρίσιμη στιγμή ωρίμανσης»**
- **batna_side_a:** Εμφανώς αποδυναμωμένη — 2,79 δις IPA, 60% εξαγωγών προς ΕΕ, 13 δις FDI. Καμία ουσιαστική εναλλακτική πέραν της μη αναγνώρισης
- **batna_side_b:** Δυτική στήριξη, αλλά αδυναμία επιβολής κυριαρχίας στο Βόρειο Κόσοβο
- **red_lines_side_a:** Προστασία σερβικών κοινοτήτων μέσω ΑSM με ουσιαστικές αρμοδιότητες
- **red_lines_side_b:** Ενιαίο θεσμικό πλαίσιο· η ASM να μην έχει νομοθετική εξουσία
- **weights:** economic 6 / military 1 / social 3
- **outcome:** Συμφωνία, **αλλά αποτυχία εφαρμογής** → «κακό προηγούμενο». Η ASM μπλοκαρίστηκε από το Συνταγματικό Δικαστήριο του Κοσόβου (2015)· η Σερβία διατήρησε παράλληλες δομές

### E8 — Εμπορικός πόλεμος / δασμοί 100% (21 Νοε 2018)
- **date:** 2018-11-21 | **negotiation_type:** DISTRIBUTIVE
- **zopa_size:** NARROW — δραστική συρρίκνωση
- **ripeness_status:** NOT_RIPE
- **batna_side_a:** Καταψήφιση ένταξης Κοσόβου σε διεθνείς οργανισμούς· αλλά χωρίς ισχυρή εναλλακτική — ζήτησε παρέμβαση Βρυξελλών για άρση δασμών
- **batna_side_b:** Οι δασμοί μείωσαν την εξάρτηση από σερβικές εισαγωγές → **αύξησαν** τη διαπραγματευτική του ισχύ
- **weights:** economic 7 / military 1 / social 2
- **outcome:** Σοβαρό κόστος και για τις δύο πλευρές· άρση σταδιακά μέχρι το 2020 με αμερικανική πίεση

### E9 — Συμφωνία Ουάσιγκτον (4 Σεπτ 2020)
- **date:** 2020-09-04 | **negotiation_type:** EMERGING (μόνο οικονομικό επίπεδο)
- **zopa_size:** NARROW — «αρκετά περιορισμένη ZOPA»
- **ripeness_status:** EMERGING
- **weights:** economic 8 / military 1 / social 1
- **outcome:** Αποτυχία. Έλλειψη πολιτικής βούλησης, αλλαγή ηγεσίας ΗΠΑ, απουσία ελεγκτικού μηχανισμού

### E10 — Συμφωνία Οχρίδας (18 Μαρ 2023)
- **date:** 2023-03-18 | **negotiation_type:** INTEGRATIVE_WIN_WIN
- **zopa_size:** WIDE — «η αξιολόγηση της ZOPA είναι θετική, διευρύνθηκε σε σύγκριση με προηγούμενες συμφωνίες»
- **ripeness_status:** RIPE
- **batna_side_a:** Ρωσοκινεζική στήριξη, **αλλά** η ευρωπαϊκή προοπτική λειτουργεί ως περιοριστικός παράγοντας στη χρήση της
- **batna_side_b:** Διατήρηση δυτικής υποστήριξης για σταδιακή διεθνή αναγνώριση
- **red_lines_side_a:** Μη ρητή αναγνώριση· αυτοδιοίκηση σερβικών κοινοτήτων
- **red_lines_side_b:** Μη παρεμπόδιση ένταξης σε διεθνείς οργανισμούς
- **weights:** economic 5 / military 1 / social 4
- **outcome:** Έγινε δεκτή αλλά **δεν υπογράφηκε επισήμως**· προφορικές δεσμεύσεις· εκκρεμεί η εφαρμογή

**implementation_success** (0.0-1.0, τεκμηριωμένο από Κεφ. 3, μόνο για events με έκβαση):
Rambouillet 0.0 · Ψήφισμα 1244 0.7 · Ahtisaari 0.0 · Βρυξέλλες 0.3 · Ουάσιγκτον 0.1 · Οχρίδα 0.2
(`None`/άγνωστο στα υπόλοιπα 4 events).

---

## 3. Indicators

### Επίπεδα βεβαιότητας (`confidence` enum)
- **`EXACT`** — αναφέρεται ρητά στο κείμενο της διπλωματικής
- **`CHART_READ`** — διαβάστηκε από τον άξονα γραφήματος (±ακρίβεια ανάγνωσης)
- **`RANGE`** — το κείμενο δίνει εύρος (π.χ. «40-50%»), αποθηκεύουμε μέσο όρο + σημείωση

### 3.1 ECONOMIC — Serbia

**`GDP_growth`** (percent, Σχεδ. 1.2 / IMF DataMapper 2024)

| year | value | confidence |
|---|---|---|
| 1997 | 3.5 | CHART_READ |
| 1998 | -2.0 | CHART_READ |
| 1999 | -9.0 | CHART_READ |
| 2000 | 6.5 | CHART_READ |
| 2001 | 6.8 | CHART_READ |
| 2002 | 4.5 | CHART_READ |
| 2003 | 5.0 | CHART_READ |
| 2004 | 9.0 | CHART_READ |
| 2005 | 6.0 | CHART_READ |
| 2006 | 5.5 | CHART_READ |
| 2007 | 6.4 | CHART_READ |
| 2008 | 5.5 | CHART_READ |
| 2009 | -2.5 | CHART_READ |
| 2010 | 1.0 | CHART_READ |
| 2011 | 2.0 | CHART_READ |
| 2012 | -0.7 | CHART_READ |
| 2013 | 2.9 | CHART_READ |
| 2014 | -1.6 | CHART_READ |
| 2015 | 1.8 | CHART_READ |
| 2016 | 3.3 | CHART_READ |
| 2017 | 2.1 | CHART_READ |
| 2018 | 4.5 | CHART_READ |
| 2019 | 4.3 | CHART_READ |
| 2020 | -0.9 | CHART_READ |
| 2021 | 7.5 | CHART_READ |
| 2022 | 2.5 | CHART_READ |
| 2023 | 2.5 | CHART_READ |
| 2024 | 4.1 | EXACT |

> Το κείμενο επιβεβαιώνει: «από το 2000 στο 2004 το ΑΕΠ αυξανόταν κατά ~5% ετησίως».
>
> **Στο `seed.py`:** αντικαταστάθηκαν με πραγματικές live τιμές World Bank API
> (`NY.GDP.MKTP.KD.ZG`, `confidence=EXACT`) αντί των τιμών ανάγνωσης γραφήματος
> παραπάνω — βλ. `PROJECT_STATUS.md`/CLAUDE.md για το σχετικό ανοιχτό ζήτημα
> γύρω από το `is_verified`.

**`unemployment_rate`** (percent, Σχεδ. 1.3 / IMF DataMapper 2024)

| year | value | confidence |
|---|---|---|
| 1997 | 12.5 | CHART_READ |
| 1998 | 13.3 | CHART_READ |
| 1999 | 12.5 | CHART_READ |
| 2000 | 12.1 | CHART_READ |
| 2001 | 12.2 | CHART_READ |
| 2002 | 13.8 | CHART_READ |
| 2003 | 15.2 | CHART_READ |
| 2004 | 18.5 | CHART_READ |
| 2005 | 20.8 | CHART_READ |
| 2006 | 21.8 | CHART_READ |
| 2007 | 18.1 | CHART_READ |
| 2008 | 14.4 | CHART_READ |
| 2009 | 16.6 | CHART_READ |
| 2010 | 19.2 | CHART_READ |
| 2011 | 23.0 | CHART_READ |
| 2012 | 24.6 | CHART_READ |
| 2013 | 22.1 | CHART_READ |
| 2014 | 19.2 | CHART_READ |
| 2015 | 17.7 | CHART_READ |
| 2016 | 15.3 | CHART_READ |
| 2017 | 13.5 | CHART_READ |
| 2018 | 12.7 | CHART_READ |
| 2019 | 10.4 | CHART_READ |
| 2020 | 9.7 | CHART_READ |
| 2021 | 11.1 | CHART_READ |
| 2022 | 9.4 | CHART_READ |
| 2023 | 9.4 | CHART_READ |
| 2024 | 9.0 | EXACT |

> **Στο `seed.py`:** ίδια αντικατάσταση με live World Bank API (`SL.UEM.TOTL.ZS`,
> `confidence=EXACT`) για τα έτη 1998/1999/2000/2005/2007/2008/2013/2018/2020/2023.

**`eu_trade_share`** (percent_of_total_trade)

| year | value | source | confidence |
|---|---|---|---|
| 2013 | 60.0 | κείμενο (εξαγωγές προς ΕΕ) | EXACT |
| 2018 | 62.0 | Σχεδ. 1.6 (εισαγωγές) | EXACT |
| 2023 | 60.0 | Σχεδ. 1.8 / European Commission | EXACT |

**`FDI_net_inflows_pct_gdp`** (percent, World Bank `BX.KLT.DINV.WD.GD.ZS`) — ✅ **προστέθηκε στο `seed.py` 2026-08-21**, νέο 4ο ECONOMIC indicator. ΔΕΝ είναι το ίδιο με το `eu_fdi_share` παρακάτω (αυτό μετράει ΣΥΝΟΛΙΚΟ FDI ως % ΑΕΠ, ανεξαρτήτως προέλευσης· το eu_fdi_share μετράει τι ποσοστό του FDI είναι ευρωπαϊκό).

| year | value | confidence |
|---|---|---|
| 2007 | 9.85 | EXACT |
| 2008 | 7.48 | EXACT |
| 2013 | 4.08 | EXACT |
| 2018 | 7.71 | EXACT |
| 2020 | 6.24 | EXACT |
| 2023 | 6.07 | EXACT |

> **Κατεύθυνση (ρητή απόφαση 2026-08-21):** θετικός δείκτης στο Power Index
> (περισσότερο FDI = υψηλότερο ECONOMIC score) — μετράει οικονομική
> ελκυστικότητα/ρεύμα κεφαλαίου, ΙΔΙΑ λογική με τα υπόλοιπα ECONOMIC
> indicators. Αυτό είναι ΣΚΟΠΙΜΑ διαφορετικό από την ερμηνεία του κειμένου
> της διπλωματικής, που πλαισιώνει το υψηλό ευρωπαϊκό FDI της Σερβίας ως
> **εξάρτηση/ευπάθεια** που αποδυναμώνει το BATNA της (βλ. role_description
> ΕΕ, ενότητα 5). Οι δύο ερμηνείες ΔΕΝ αναιρούν η μία την άλλη — το Power
> Index μετράει ένα στενό, ποσοτικό "θετικό οικονομικό σήμα", ενώ το
> ποιοτικό εύρημα της διπλωματικής για εξάρτηση παραμένει ξεχωριστό, ήδη
> τεκμηριωμένο context για το LLM. Αν στην υπεράσπιση ζητηθεί να
> δικαιολογηθεί η κατεύθυνση, αυτό είναι το επιχείρημα: το Power Index δεν
> ισχυρίζεται ότι πιάνει "ανεξαρτησία" -- πιάνει "τρέχουσα οικονομική
> επίδοση/ελκυστικότητα", ένα υποσύνολο του ECONOMIC score μαζί με GDP/
> ανεργία.

**`eu_fdi_share`** (percent_of_total_FDI): 2016 → 78.0 (Σχεδ. 1.6, EXACT) — deferred

**`eu_preaccession_funds`** (EUR_million, cumulative)

| year | value | source | confidence |
|---|---|---|---|
| 2020 | 2790 | κείμενο, IPA 2007-2020 | EXACT |
| 2027 | 1500 | IPA III 2021-2027 (allocation) | EXACT |

> ⚠️ **Ασυμφωνία τεκμηριωμένη:** το κείμενο αναφέρει 2,79 δις για IPA 2007-2020,
> ενώ το Σχεδ. 1.6 δείχνει 2,2 δις για την ίδια περίοδο (πιθανή εξήγηση: το
> infographic του 2018 καταγράφει δεσμευμένα κονδύλια μέχρι εκείνη τη στιγμή, το
> κείμενο το τελικό σύνολο). Απόφαση: κρατάμε 2790, με `source` που αναφέρει
> και τις δύο πηγές. **Δεν έχει μπει ακόμα στο `seed.py`** (deferred, §Future Work).

> **Επανέλεγχος 2026-08-21** (πλαίσιο: αξιολόγηση ως πιθανό Power Index
> indicator): επιβεβαιώθηκε με επίσημη πηγή EU enlargement
> ([enlargement.ec.europa.eu](https://enlargement.ec.europa.eu/funding-technical-assistance/overview-instrument-pre-accession-assistance_en))
> ότι το IPA δίνεται σε πολυετείς περιόδους (IPA I 2007-2013, IPA II 2014-2020,
> IPA III 2021-2027), ΟΧΙ ετήσια ροή -- καμία αξιόπιστη annual time series
> βρέθηκε. Παραμένει ακατάλληλο για το per-year normalization μοντέλο του
> Power Index (θα έμπαινε σε 1 μόνο έτος ανά χώρα) -- ταιριάζει καλύτερα ως
> static context στο LLM prompt παρά ως normalized indicator. Παραμένει
> deferred, ΟΧΙ επειδή τα δεδομένα είναι αναξιόπιστα, αλλά επειδή η
> κοκκοποίηση (granularity) δεν ταιριάζει στο μοντέλο.

**`russian_gas_dependency`** (percent_of_imports): 2023 → 80.0 (κείμενο «>80%», EXACT lower bound) — deferred
**`chinese_loans_cumulative`** (EUR_billion): 2023 → 10.0 (κείμενο «>10 δις» 2010-2023, EXACT lower bound) — deferred

**Εμπορικοί εταίροι 2023** (Σχεδ. 1.8, EUR_billion, ένα `indicator_type` ανά εταίρο) — deferred:

| indicator_type | value |
|---|---|
| `trade_volume_EU` | 39.07 |
| `trade_volume_CEFTA` | 6.11 |
| `trade_volume_China` | 5.64 |
| `trade_volume_Russia` | 2.70 |
| `trade_volume_Turkey` | 2.28 |
| `trade_volume_USA` | 1.05 |
| `trade_volume_Other` | 8.59 |

> **Επανέλεγχος 2026-08-21:** καμία αντίστοιχη ανάλυση ανά εταίρο δεν
> εντοπίστηκε για το Κόσοβο (ούτε στη διπλωματική ούτε σε γρήγορη εξωτερική
> αναζήτηση) -- μόνο Serbia, μόνο 2023. Παραβιάζει το κριτήριο "ίδιο μέτρο
> και για τις δύο χώρες, πολυετής σειρά" -- η ουσιαστική ποιοτική εικόνα
> (π.χ. μηδενικές εμπορικές σχέσεις Κοσόβου-Κίνας/Ρωσίας λόγω μη
> αναγνώρισης) είναι ήδη τεκμηριωμένη στο role_description. Παραμένει
> deferred για το Power Index -- ασύμμετρα/μονού-έτους δεδομένα δεν θα
> άλλαζαν ουσιωδώς κάτι στο σκοράρισμα.

### 3.2 ECONOMIC — Kosovo

**`GDP_per_capita`** (EUR_constant_2003, Σχεδ. 1.4 / IMF staff estimates) — deferred, δεν έχει μπει ακόμα στο `seed.py`

| year | value | confidence |
|---|---|---|
| 1981 | 1780 | CHART_READ |
| 1983 | 1560 | CHART_READ |
| 1985 | 1500 | CHART_READ |
| 1987 | 1580 | CHART_READ |
| 1989 | 1380 | CHART_READ |
| 1991 | 1000 | CHART_READ |
| 1993 | 470 | CHART_READ |
| 1995 | 480 | CHART_READ |
| 1997 | 550 | CHART_READ |
| 1999 | 280 | CHART_READ |
| 2001 | 870 | CHART_READ |
| 2003 | 930 | CHART_READ |

> Το κείμενο αναφέρει «~400 δολάρια το 1999» και «400-500 δολάρια το 2000» — το
> γράφημα είναι σε ευρώ σταθερά 2003, όχι άμεσα συγκρίσιμο. Απόφαση: κρατάμε τις
> τιμές γραφήματος με ρητό `unit`, και ξεχωριστό `GDP_per_capita_USD` για 1999
> (400) και 2000 (450, RANGE) με διαφορετικό unit — το normalization του Power
> Index γίνεται ανά `indicator_type`, οπότε δεν υπάρχει πρόβλημα ανάμειξης μονάδων.

**`unemployment_rate`** (percent, Σχεδ. 1.5 / World Bank–ILO)

| year | value | confidence |
|---|---|---|
| 2000 | 11.5 | CHART_READ ⚠️ |
| 2001 | 57.0 | CHART_READ |
| 2002 | 55.0 | CHART_READ |
| 2003 | 49.5 | CHART_READ |
| 2004 | 40.0 | CHART_READ |
| 2005 | 41.5 | CHART_READ |
| 2006 | 45.0 | CHART_READ |
| 2007 | 46.0 | CHART_READ |
| 2008 | 47.5 | CHART_READ |

> ⚠️ **Σοβαρή ασυμφωνία:** η τιμή του 2000 (~11,5%) αντιφάσκει ευθέως με το
> κείμενο, που αναφέρει ανεργία 40-50% την ίδια περίοδο και «η διεθνής
> κοινότητα κάλυπτε το 90% των δημοσίων δαπανών». Πιθανή εξήγηση: το 2000 η
> στατιστική υπηρεσία μόλις ξεκινούσε υπό UNMIK, μη αντιπροσωπευτικό δείγμα.
> Απόφαση τότε: εισαγωγή με `is_verified=false` + `notes` + εξαίρεση από τον
> Power Index. **Στην πράξη: η τιμή του 2000 δεν μπήκε καθόλου στο `seed.py`**
> (το πραγματικό seed έχει μόνο 2005/2007/2008, βλ. πίνακα seed παρακάτω) — η
> απόφαση παρέμεινε θεωρητική, δεν χρειάστηκε εφαρμοστεί.
> Επίσης το κείμενο δίνει 45.0 για το 2005 (EXACT) ενώ το γράφημα ~41,5 — το
> `seed.py` χρησιμοποιεί τελικά **41.0** για το 2005 (Γράφημα 1.5, ILO/World Bank).

**`eu_trade_share`**: Kosovo 2018 → 44.7 (Σχεδ. 1.7, εισαγωγές, EXACT) — ✅ στο `seed.py`
**`FDI_net_inflows_pct_gdp`** (World Bank `BX.KLT.DINV.WD.GD.ZS`) — ✅ **προστέθηκε 2026-08-21**: 2008→10.45 · 2013→5.52 · 2018→4.04 · 2020→5.10 · 2023→8.68 (όλα EXACT). Ίδιο indicator_type/κατεύθυνση με Serbia, βλ. §3.1.
**`eu_fdi_share`**: Kosovo 2016 → 34.0 (Σχεδ. 1.7, EXACT) — deferred
**`eu_preaccession_funds`**: 2020 → 1480 / 2027 → 600 (Σχεδ. 1.7 / IPA III) — deferred
**`intl_aid_share_of_public_spending`**: 2000 → 90.0 (κείμενο, Weller 2009, EXACT) — deferred
**`has_own_currency`** / **`has_sovereign_bond_market`**: boolean-as-value (0 για όλα τα έτη) — τεκμηριώνουν τη δομική αδυναμία του Κεφ. 3.1.2, χρήσιμα για LLM context, όχι για Power Index. Deferred.

### 3.3 MILITARY

**Ενημέρωση 2026-08-21:** ο πυρήνας του MILITARY category (Serbia vs
Kosovo comparison) αναθεωρήθηκε πλήρως -- βλ. ενότητα 3.6 παρακάτω. Το
παρακάτω παραμένει ως ιστορικό αρχείο των boolean markers που θεωρήθηκαν
και ΔΕΝ μπήκαν στο seed.py.

**⚠️ Το μεγαλύτερο κενό δεδομένων** (πριν το 3.6). Η διπλωματική είναι
πλούσια σε ποιοτική στρατιωτική ανάλυση αλλά φτωχή σε αριθμούς:

| Country | indicator_type | year | value | unit | source |
|---|---|---|---|---|---|
| Serbia | `nato_airstrike_days` | 1999 | 78 | days | κείμενο (Allied Force) |
| Serbia | `infrastructure_damage` | 1999 | 20.0 | USD_billion (RANGE: «δεκάδες δισ.») | κείμενο |
| Kosovo | `kfor_presence` | 1999-2023 | 1 | boolean | κείμενο |
| Kosovo | `us_military_base` | 1999-2023 | 1 | boolean (Camp Bondsteel) | κείμενο |
| Serbia | `russian_arms_supply` | 2020-2023 | 1 | boolean (MiG-29, Pantsir-S1) | κείμενο |
| Serbia | `unsc_veto_protection` | 1999-2023 | 1 | boolean (Ρωσία, Κίνα) | κείμενο |

Καμία από αυτές τις boolean markers δεν έχει μπει στο `seed.py` — βλ. ενότητα 8
(απόφαση #3) για ποια επιλογή ακολουθήθηκε τελικά.

### 3.4 SOCIAL_UNREST

**`freedom_house_score`** (score_0_100, Σχεδ. 1.11 / Nations in Transit, Smeltzer & Karppi 2024) — **ο πιο πολύτιμος δείκτης**, δείχνει αντίστροφες τάσεις: πτωτική Σερβία, ανοδικό Κόσοβο.

| year | Serbia | Kosovo | confidence |
|---|---|---|---|
| 2005 | 54.0 | 27.5 | CHART_READ |
| 2007 | 55.0 | 27.0 | CHART_READ |
| 2009 | 53.5 | 30.5 | CHART_READ |
| 2011 | 55.5 | 31.0 | CHART_READ |
| 2013 | 56.0 | 29.5 | CHART_READ |
| 2015 | 55.5 | 32.5 | CHART_READ |
| 2017 | 53.0 | 34.0 | CHART_READ |
| 2019 | 49.0 | 35.5 | CHART_READ |
| 2021 | 46.0 | 35.5 | CHART_READ |
| 2023 | 43.0 | 38.0 | CHART_READ |

**Δημογραφικά** (Σχεδ. 1.1, static, year=2008) — deferred:

| Country | indicator_type | value | unit |
|---|---|---|---|
| Kosovo | `albanian_population_share` | 92.0 | percent |
| Kosovo | `serb_population_share` | 5.5 | percent (RANGE 5-6) |
| Kosovo | `serb_share_north_kosovo` | 90.0 | percent |

**Γεγονότα κοινωνικής αναταραχής** (event-based marker, value=1) — deferred:

| year | Country | indicator_type | περιγραφή |
|---|---|---|---|
| 2004 | Kosovo | `ethnic_violence_event` | Ταραχές, πυρπόληση σερβικών εκκλησιών/μοναστηριών, εκτοπισμοί |
| 2008 | Kosovo | `unilateral_declaration` | Ανακήρυξη ανεξαρτησίας |
| 2018 | Kosovo | `political_assassination` | Δολοφονία Ό. Ιβάνοβιτς, Μιτρόβιτσα |
| 2022 | Kosovo | `barricades_protests` | Κρίση πινακίδων, οδοφράγματα, στρατιωτική κινητοποίηση |

**`international_recognitions`** (count) — deferred: 2008→1 (Αλβανία), 2024→100 (κείμενο), 2024→5 (`eu_non_recognizers`)

### 3.5 `GDP_absolute_usd` — ΤΩΡΑ μέρος του Power Index (αναθεωρήθηκε 2026-08-21)

**Ιστορικό της απόφασης (δύο γύροι, βλ. PROJECT_STATUS.md για το πλήρες
session log):**

1. **1ος γύρος:** το `GDP_absolute_usd` μπήκε ως *context-only* (εκτός
   `NORMALIZATION_RANGES`), *αντικαθιστώντας* το `GDP_growth` στο σκοράρισμα.
   Πρόβλημα που βρέθηκε: με μόνο `GDP_growth`, δεν υπήρχε καθόλου μέτρο
   απόλυτου μεγέθους. Με μόνο `GDP_absolute_usd` (αντικατάσταση, όχι
   προσθήκη), χάθηκε η ικανότητα ανίχνευσης του οικονομικού σοκ Σερβίας
   1999 (βλ. P1 στο `test_validation_targets.py`) -- ο μοναδικός κοινός
   δείκτης 1998/1999 ήταν το `unemployment_rate`, ίδιο και τα δύο έτη
   (13.70%), άρα η "κατάρρευση" έγινε αδύνατο να ανιχνευθεί.
2. **2ος γύρος (τελικό):** `GDP_absolute_usd` προστέθηκε **μαζί με** το
   `GDP_growth` (και τα δύο scored, ισοβαρή μέσο όρο στο ECONOMIC μαζί με
   `unemployment_rate` -- 3 δείκτες συνολικά όπου διαθέσιμοι). Το
   `GDP_growth` πιάνει δυναμική/σοκ, το `GDP_absolute_usd` πιάνει δομικό
   μέγεθος -- διαφορετικά πράγματα, και τα δύο χρήσιμα.

**Λογαριθμική κλίμακα, όχι γραμμική:** με γραμμική κλίμακα $0-100B, το
Kosovo GDP component ήταν σχεδόν σταθερό χαμηλό (5.2%-10.5% normalized σε
όλα τα έτη) -- δομικό "ταβάνι" που δεν κινούνταν ανεξάρτητα από πραγματική
οικονομική δυναμική, και προκάλεσε reversal στο P4 (Power Gap διευρυνόταν
αντί να στενεύει). Log-scale ($1B-$100B όριο, raw USD πριν το `log10`)
δίνει στο Κόσοβο πραγματικό εύρος διακύμανσης (35.8%-51.0%) -- διόρθωσε
το P4.

**Ευστάθεια του ορίου ($1B-$100B):** ελέγχθηκε 2026-08-21 με εναλλακτικό,
εξίσου υπερασπίσιμο εύρος ($500M-$200B -- στρογγυλεμένα μεγέθη, ευρύτερη
περιφερειακή ομάδα που συμπεριλαμβάνει κλίμακα Ελλάδας αντί να εξαιρεί
οτιδήποτε πάνω από Βουλγαρία). Committed πριν το τρέξιμο, ΟΧΙ επιλεγμένο
για συγκεκριμένο αποτέλεσμα. Το P3 (`find_optimal_mutual_compromise_period`
= 2013) παρέμεινε robust και στα δύο σενάρια (βλ. ενότητα 3.6/
`test_2013_is_optimal_window` docstring για τα ακριβή νούμερα).

**Πηγή:** World Bank API, indicator `NY.GDP.MKTP.CD` (GDP, current US$),
verified με raw JSON query 2026-08-21.

| year | Serbia | Kosovo |
|---|---|---|
| 1999 | $20,878,694,851 | ❌ δεν υπάρχει (XKX series ξεκινά 2008) |
| 2005 | $28,334,256,181 | ❌ δεν υπάρχει |
| 2007 | $44,888,028,946 | ❌ δεν υπάρχει |
| 2008 | $54,220,641,202 | $5,202,943,075 |
| 2013 | $50,455,529,604 | $6,735,327,512 |
| 2023 | $81,343,999,280 | $10,466,753,840 |

Το World Bank ΔΕΝ έχει σειρά GDP για το Κόσοβο (XKX) πριν το 2008 — δεν
υπήρχε ως ξεχωριστή reporting entity πριν την ανεξαρτησία. Confirmed
κενό στο API (`value: null` για 1999/2005/2007), όχι απλά μη-ελεγμένο.
Δεν εικάσαμε τιμές γι' αυτά τα έτη -- το ECONOMIC score αυτών των ετών
στηρίζεται μόνο σε `GDP_growth`+`unemployment_rate` όπου διαθέσιμα.

**Τεχνική σημείωση (παραμένει σχετική):** το `get_category_score()`
αγνοεί indicator_types χωρίς normalization range αντί να σκάει με
`ValueError` -- αρχικά χτίστηκε για το context-only πείραμα του 1ου
γύρου, παραμένει χρήσιμο μηχανισμό (π.χ. το `troop_presence_index`
είναι πλέον context-only μέσω αυτού, βλ. 3.6).

### 3.6 MILITARY category — Kosovo, αναθεώρηση (2026-08-21)

**Πρόβλημα που βρέθηκε:** το MILITARY category συνέκρινε δύο
εννοιολογικά ασύμβατα μεγέθη κάτω από την ίδια κατηγορία -- Serbia
`military_expenditure_pct_gdp` (δικό της στρατιωτικό spending, World
Bank/SIPRI) vs Kosovo `troop_presence_index` (researcher estimate ΞΕΝΗΣ
NATO/KFOR στρατιωτικής παρουσίας, όχι δικό της spending/ικανότητα).
Ισοδύναμο με το να συγκρίνεις "πόσο ξοδεύει η Α χώρα στον στρατό της" με
"πόσο στρατό έχει σταθμεύσει μια ΑΛΛΗ χώρα στο έδαφος της Β" -- διαφορετικά
constructs.

**Έρευνα (2026-08-21):** επιβεβαιώθηκε ότι το World Bank/SIPRI ΕΧΕΙ
`military_expenditure_pct_gdp` και για το Κόσοβο (indicator `MS.MIL.XPND.
GD.ZS`, ΙΔΙΟ code με τη Σερβία), verified με raw API query:

| year | Kosovo military_expenditure_pct_gdp |
|---|---|
| 2008 | 0.0163% |
| 2013 | 0.7217% |
| 2023 | 1.2735% |

Εναλλακτικά που εξετάστηκαν και απορρίφθηκαν (βλ. PROJECT_STATUS.md για
πλήρη σύγκριση):
- **`active_personnel`**: World Bank `MS.MIL.TOTL.P1` έχει ΜΗΔΕΝ
  δεδομένα για Kosovo (25/25 έτη null). Δευτερεύουσες πηγές (NATO 2013:
  ~2,200· CIA World Factbook 2021: ~3,500· Wikipedia 2023: "surpassed
  5,000", χωρίς ακριβή παραπομπή) καλύπτουν αξιόπιστα μόνο το 2013 --
  χειρότερο κάλυμμα από το `military_expenditure_pct_gdp`. Απορρίφθηκε.
- **Global Firepower Index**: ιδιωτική πηγή, αδιαφανής μεθοδολογία --
  δεν εξετάστηκε περαιτέρω μετά την αρχική επιφύλαξη.

**1999/2005/2007 = 0.0, τεκμηριωμένο ιστορικό γεγονός, ΟΧΙ εκτίμηση
κενού:** το Kosovo Security Force ιδρύθηκε **Ιανουάριος 2009**. Πριν από
αυτό δεν υπήρχε ΚΑΝΕΝΑ στρατιωτικό σώμα του Κοσόβου να χρηματοδοτηθεί --
το προγενέστερο Kosovo Protection Corps (KPC, 1999-2009) ήταν **ρητά
μη-στρατιωτικός** οργανισμός πολιτικής προστασίας υπό UNMIK (πηγή:
Wikipedia "Kosovo Security Force", verified 2026-08-21). Άρα 0.0 δεν
είναι placeholder/interpolation -- είναι το πραγματικό, τεκμηριωμένο
γεγονός. `confidence="EXACT"`, `source` = ρητή αναφορά στο ιστορικό
γεγονός, όχι σε στατιστική βάση (βλ. seed.py).

**`troop_presence_index` παραμένει στη ΒΔ, context-only** (εκτός
`NORMALIZATION_RANGES`) -- researcher estimate ξένης στρατιωτικής
παρουσίας, χρήσιμο ως αφηγηματικό context αλλά ΔΕΝ ανακατεύεται πια στο
ίδιο average με το `military_expenditure_pct_gdp`.

**`military_expenditure_usd`** (World Bank `MS.MIL.XPND.CD`) — ✅
**προστέθηκε 2026-08-21**, δεύτερο MILITARY indicator δίπλα στο
`military_expenditure_pct_gdp` (απόλυτη κλίμακα ικανότητας αντί για ένταση
προσπάθειας -- ίδιο σκεπτικό με `GDP_absolute_usd` δίπλα στο `GDP_growth`,
βλ. §3.5). Λογαριθμική κλίμακα ($500K-$5δισ), απαραίτητη -- ο λόγος
Serbia/Kosovo σε απόλυτα δολάρια είναι ΑΚΟΜΑ πιο ακραίος από ό,τι στο GDP
(~690× το 2008, ~13.5× το 2023).

| year | Serbia | Kosovo |
|---|---|---|
| 1998 | $642,122,263 | $0 (ιστορικό γεγονός) |
| 1999 | $737,469,451 | $0 (ιστορικό γεγονός) |
| 2000 | $337,080,608 | $0 (ιστορικό γεγονός) |
| 2005 | $629,500,943 | $0 (ιστορικό γεγονός) |
| 2007 | $971,570,565 | $0 (ιστορικό γεγονός) |
| 2008 | $1,111,631,538 | $927,235 |
| 2013 | $932,203,595 | $48,597,681 |
| 2018 | $1,064,747,317 | $63,344,074 |
| 2020 | $1,282,529,333 | $78,965,006 |
| 2023 | $1,796,879,440 | $133,185,466 |

Serbia: **όλα τα 10 KEY_YEARS**, καμία null τιμή σε ολόκληρη τη σειρά
1998-2023 (verified raw JSON query 2026-08-21). Kosovo: 5 πραγματικές τιμές
+ 5 ιστορικά μηδενικά (KSF, ίδιο γεγονός/τεκμηρίωση με το §3.6 παραπάνω) = 8/10.

**Bonus fix 2026-08-21:** το ήδη-seeded `military_expenditure_pct_gdp` του
Κοσόβου είχε 0.0 μόνο για 1999/2005/2007, ΟΧΙ για 1998/2000 -- ίδια περίοδος,
ίδιο ιστορικό γεγονός (KSF Ιαν. 2009), καμία διαφορετική αιτιολόγηση για την
απουσία τους. Προστέθηκαν και τα δύο (1998, 2000 = 0.0) σε ΚΑΙ τα δύο
military indicator_types, για συνέπεια. Δεν αλλάζει ποια έτη έχουν πλήρες
Power Index (Kosovo ECONOMIC/SOCIAL παραμένουν `None` το 1998/2000 ούτως ή
άλλως) -- καθαρά διόρθωση ασυνέπειας τεκμηρίωσης.

### 3.7 Έρευνα στρατιωτικής "δύναμης πέρα από χρήματα" (2026-08-21) — καμία πηγή υιοθετήθηκε

Διερευνήθηκε αν υπάρχει αξιόπιστη, δημόσια, συμμετρική πηγή για
πραγματική στρατιωτική ικανότητα (όχι μόνο δαπάνες). Συμπέρασμα: **όχι** —
μένουμε με δαπάνες (§3.5-3.6, τώρα και τα δύο MILITARY indicator_types).

- **IISS Military Balance** — η πιο αναγνωρισμένη ακαδημαϊκή πηγή, ΑΛΛΑ το
  online database (Military Balance+) είναι **subscription-only**· καμία
  δωρεάν δημόσια πρόσβαση σε πραγματικά στοιχεία βρέθηκε. Απορρίφθηκε: μη
  επαληθεύσιμο χωρίς συνδρομή, δεν μπορεί να παρατεθεί υπεύθυνα.
- **SIPRI Arms Transfers Database** (`armstransfers.sipri.org`, ίδιο δημόσια
  προσβάσιμο re-publish και μέσω World Bank `MS.MIL.XPRT.KD`/`MS.MIL.MPRT.KD`) —
  αξιόπιστη πηγή (ίδιος οργανισμός με το ήδη χρησιμοποιούμενο military
  expenditure). Arms **exports**: Kosovo = 100% null σε 26/26 έτη (λογικό,
  δεν παράγει όπλα) -- πλήρως ασύμμετρο, απορρίφθηκε. Arms **imports** (TIV):
  δεδομένα και για τις δύο χώρες, αλλά Kosovo μόνο 3/10 KEY_YEARS
  (2018/2020/2023, τιμές $1-14εκ) έναντι 7/10 Serbia -- πολύ αραιή τομή (3
  έτη) για να δικαιολογήσει προσθήκη indicator. Απορρίφθηκε ως ΠΡΟΣ ΤΩΡΑ
  (δεδομένα αξιόπιστα αλλά ανεπαρκή κάλυψη, όχι πρόβλημα αξιοπιστίας).
- **Global Firepower Index** — αξιολογήθηκε ρητά η μεθοδολογία πριν
  εξεταστεί ως πηγή, όπως ζητήθηκε. **Απορρίφθηκε ως αναξιόπιστο**: αδιαφανής
  φόρμουλα (δεν δημοσιεύουν πλήρη υπολογισμό), υποκειμενικά bonus/penalty
  (π.χ. γεωγραφικοί παράγοντες) χωρίς τεκμηρίωση στάθμισης, ιδιωτική
  εταιρεία χωρίς σύνδεση με επίσημο στατιστικό οργανισμό. Επιβεβαιώνεται από
  πολλαπλές ανεξάρτητες πηγές: ["fallacy and inappropriateness of using a
  global military power rating"](https://www.researchgate.net/publication/388404119_Global_Firepower_Index_the_fallacy_and_inappropriateness_of_using_a_global_military_power_rating)
  (ResearchGate)· ["clickbait ranking"](https://www.bellingcat.com/news/uk-and-europe/2018/06/29/ukrainian-president-cites-clickbait-ranking-national-address/)
  (Bellingcat)· ["χωρίς επαληθευμένα στοιχεία ή διαφανή μεθοδολογία"](https://voxukraine.org/en/global-firepower-a-military-ranking-without-verified-facts-or-transparent-methodology)
  (VoxUkraine). **Ρητά ΔΕΝ αντιμετωπίζεται ως ισοδύναμο με World Bank/SIPRI.**

**Απόφαση:** προτιμήθηκαν λιγότερα αλλά αξιόπιστα δεδομένα (δαπάνες,
§3.5-3.6) αντί για προσθήκη αμφίβολης/ασύμμετρης πηγής. Μπορεί να
επανεξεταστεί στο μέλλον αν το SIPRI arms-imports TIV αποκτήσει πυκνότερη
κάλυψη Κοσόβου.

**Τελευταίος γύρος έρευνας (2026-08-21) -- CIA World Factbook + βρετανικές
πηγές, καμία νέα πηγή δεν προστέθηκε στο μοντέλο:**

- **CIA World Factbook, active personnel:** μόνο τρέχον snapshot (Serbia
  ~25,000 2022 est., Kosovo/KSF ~4,000 active + 5,000 εφεδρεία, χωρίς σαφές
  έτος), καμία ιστορική σειρά. Το πεδίο "Military and security forces" είναι
  αμιγώς περιγραφικό/οργανωτικό σε όλες τις αρχειοθετημένες εκδόσεις
  2006-2025 (verified μέσω `worldfactbookarchive.org`, mirror του
  cia.gov -- το ίδιο το cia.gov μπλοκάρει scraping, 403 σε όλα τα URLs).
  Καμία προσθήκη -- πληροί ακριβώς το preset κριτήριο απόρριψης (μόνο 1
  τρέχον snapshot).
- **CIA World Factbook, military expenditure %GDP:** ΕΧΕΙ πολυετή στοιχεία
  ανά έκδοση (Kosovo 2011-2024, Serbia 2010-2024), ΑΛΛΑ η υποκείμενη πηγή
  είναι η ΙΔΙΑ SIPRI βάση που ήδη χρησιμοποιούμε μέσω World Bank -- όχι
  ανεξάρτητη μέτρηση, αναδημοσίευση σε διαφορετικό σημείο αναθεώρησης.
  **Cross-check αποτέλεσμα:** Kosovo 2013 CIA 0.69% vs seeded 0.72% (κοντά)·
  Kosovo 2023 CIA ~1.3% vs seeded 1.27% (πολύ κοντά) -- ενισχύει την
  αξιοπιστία των ήδη-seeded τιμών. Serbia 2013 CIA 1.48% vs seeded 1.85% --
  πιο αισθητή απόκλιση, πιθανώς λόγω γνωστής τάσης του SIPRI να αναθεωρεί
  ιστορικές εκτιμήσεις με τον καιρό, όχι σφάλμα. Καμία νέα χρονιά πέρα από
  όσες ήδη καλύπτει το World Bank/SIPRI -- σύμφωνα με το preset κριτήριο,
  ΔΕΝ προστέθηκε ως νέα πηγή, μόνο ως τεκμηριωμένο cross-check εδώ.
- **Jane's (janes.com):** επιβεβαιωμένα subscription/marketing-only, καμία
  δωρεάν δημόσια πρόσβαση σε στοιχεία -- ίδια κατηγορία με IISS. Απορρίφθηκε.
- **UK House of Commons Library:** δημόσιο, δωρεάν, υπάρχουν σχετικά
  research briefings (π.χ. "Security in the Western Balkans"), αλλά
  αφηγηματικά policy briefings, όχι ποσοτικά datasets -- δεν πληρούν το
  κριτήριο "ίδια μέτρηση, πολυετής σειρά". Απορρίφθηκαν ως Power Index πηγή
  (PDF/σελίδα fetch μπλοκαρίστηκε 403 στο parliament.uk, η αξιολόγηση
  βασίζεται σε τίτλους/summaries, όχι πλήρη ανάγνωση -- τίμια σημείωση).
- **UK Ministry of Defence:** καμία αποκλειστική ποσοτική βάση δεδομένων
  βρέθηκε, μόνο ανακοινώσεις τύπου για KFOR αναπτύξεις (σχετικό με το ήδη
  context-only `troop_presence_index`, όχι νέο ποσοτικό indicator).
  Απορρίφθηκε.

**Bonus fix 2026-08-21 (εντοπίστηκε κατά το CIA cross-check, ΔΕΝ είναι νέα
πηγή):** το ΗΔΗ εγκεκριμένο World Bank `MS.MIL.XPND.GD.ZS`
(`military_expenditure_pct_gdp`) είχε τιμές για 2018/2020 και στις δύο
χώρες που ποτέ δεν seed-αρίστηκαν -- καθαρή παράλειψη, όχι απουσία
δεδομένων. Προστέθηκαν στο `seed.py`: Serbia 2018→2.02%, 2020→2.30% ·
Kosovo 2018→0.8044%, 2020→1.0230% (raw JSON query 2026-08-21). Ίδια πηγή/
indicator_type με τις ήδη seeded τιμές, καμία νέα απόφαση σχεδιασμού.

**ΤΕΛΙΚΗ ΑΠΟΦΑΣΗ, τέλος έρευνας MILITARY:** το MILITARY category κλειδώνει
με `military_expenditure_pct_gdp` + `military_expenditure_usd` (και τα δύο
World Bank/SIPRI, και οι δύο χώρες) -- καμία περαιτέρω πηγή θα εξεταστεί.

---

## 4. Actor roles per event (event_participants)

⚠️ **Πλοήγηση:** οι ενότητες 3.5-3.7 (GDP_absolute_usd, MILITARY revision,
military capability research) γράφτηκαν χρονολογικά ΜΕΤΑ τις ενότητες 4-9 —
παρέμειναν μέσα στην ενότητα 3 (Indicators) γιατί εννοιολογικά ανήκουν εκεί,
όχι στο τέλος του εγγράφου. Η ενότητα 9 (μεθοδολογική θεμελίωση CINC) είναι η
πιο πρόσφατη προσθήκη στο τέλος του αρχείου.

⚠️ **Αριθμοδότηση:** η αρίθμηση E1-E10 εδώ (από την εξαγωγή δρώντων, κεφ. 3.1+3.2)
**ΔΕΝ αντιστοιχεί** στην E1-E10 αρίθμηση της ενότητας 2 (SEED_DATA_SPEC/`seed.py`)
— είναι διαφορετική πηγή, διαφορετική καταμέτρηση. Γι' αυτό τα events παρακάτω
αναφέρονται με τίτλο+έτος, όχι με "E#", για να μην μπερδεύονται οι δύο αριθμήσεις.
Δύο σημεία προσοχής:
- Το «Rambouillet 1999» εδώ δεν έχει αντίστοιχο breakdown για το «Revocation of
  Kosovo's Autonomy 1989» (ενότητα 2, E1) — η εξαγωγή δρώντων δεν κάλυψε εκείνο το event.
- Η «Κρίση πινακίδων (2022)» παρακάτω **ΔΕΝ είναι** ένα από τα 10 seeded
  NegotiationEvents της ενότητας 2 — κρατιέται εδώ ως πληροφορία πηγής, σημειωμένη
  ως μη-υπαρκτή στη σημερινή βάση.

**Rambouillet Talks (1999):** Serbia PARTY · Kosovo PARTY · USA (Holbrooke) MEDIATOR (coercive diplomacy) · NATO MEDIATOR/pressure · Russia SUPPORTER(Serbia, βέτο-δυνατότητα ΣΑ) · China SUPPORTER(Serbia, βέτο-δυνατότητα ΣΑ) · UN SUPPORTER(Kosovo)

**Ψήφισμα ΟΗΕ 1244 (1999):** Serbia PARTY · Kosovo PARTY · UN MEDIATOR (UNMIK) · NATO GUARANTOR (KFOR, «de facto υπέρτατη εξουσία») · Russia SUPPORTER(Serbia) · China SUPPORTER(Serbia)

**Standards Before Status / UNMIK περίοδος (1999-2005, key 2004):** Serbia PARTY · Kosovo PARTY · UN(UNMIK) MEDIATOR · NATO(KFOR) GUARANTOR · OSCE GUARANTOR (παρακολούθηση) · EU SUPPORTER(Kosovo, πίεση για νέες συνομιλίες) · USA SUPPORTER(Kosovo) · Russia SUPPORTER(Serbia, στενός σύμμαχος)

**Ahtisaari Plan (2007):** Serbia PARTY · Kosovo PARTY · UN(Ahtisaari) MEDIATOR · EU(EULEX) GUARANTOR (προβλεπόμενη παρουσία) · USA SUPPORTER(Kosovo) · Russia SUPPORTER(Serbia, απειλή βέτο, δεν έφτασε στο ΣΑ) · China SUPPORTER(Serbia)

**Μονομερής Ανακήρυξη Ανεξαρτησίας (2008):** Kosovo PARTY · Serbia PARTY (αντίθεση, προσφυγή ICJ) · USA SUPPORTER(Kosovo) · EU SUPPORTER(Kosovo, αλλά 5 μέλη όχι) · Russia SUPPORTER(Serbia) · China SUPPORTER(Serbia) · India SUPPORTER(Serbia) · ICJ GUARANTOR/observer (γνωμοδότηση 2010)

**Συμφωνία Βρυξελλών (2013):** Serbia PARTY (Dačić) · Kosovo PARTY (Thaçi) · EU(Ashton) MEDIATOR («στιγμή ωρίμανσης») · OSCE GUARANTOR (εποπτεία δημοτικών εκλογών 2013). Μοχλός: οικον. εξάρτηση Σερβίας από ΕΕ (2.79δις IPA, 60% εξαγωγών, 13δις FDI)

**Εμπορικός Πόλεμος / Δασμοί 100% (2018-2020):** Kosovo PARTY (Haradinaj) · Serbia PARTY (Vučić, έκκληση ΕΕ) · USA(Trump/Grenell) MEDIATOR από 2019 · EU SUPPORTER/mediator

**Συμφωνία Ουάσιγκτον (2020):** Serbia PARTY (Vučić) · Kosovo PARTY · USA(Trump) MEDIATOR (Oval Office) · Russia SUPPORTER(Serbia) · China SUPPORTER(Serbia). Απέτυχε — αλλαγή ηγεσίας ΗΠΑ, έλλειψη ελεγκτικού μηχανισμού

**Κρίση πινακίδων (2022)** [⚠️ ΔΕΝ είναι seeded event]: Serbia PARTY (Vučić, στρατιωτική κινητοποίηση) · Kosovo PARTY (Kurti, κανονισμοί πινακίδων) · EU MEDIATOR (αποκλιμάκωση, συμφωνία 25/8/2022) · Russia SUPPORTER(Serbia) · China SUPPORTER(Serbia)

**Συμφωνία Οχρίδας (2023):** Serbia PARTY (Vučić) · Kosovo PARTY (Kurti) · EU(Borrell) MEDIATOR (τελικό σχέδιο, οδικός χάρτης) · Russia SUPPORTER(Serbia) · China SUPPORTER(Serbia). Δεν υπογράφηκε επίσημα· «κόκκινες γραμμές αμετάβλητες»

**Σημείωση για `SUPPORTER`:** ο ρόλος `SUPPORTER` (δρώντες που στήριζαν χωρίς να
είναι στο τραπέζι, π.χ. Russia/China με απειλή βέτο) **δεν υπάρχει σήμερα** στο
`ParticipantRole` enum (`PARTY | MEDIATOR | GUARANTOR`) — βλ. PROJECT_PLAN.md,
roadmap item "Actors feature", για την πρόταση προσθήκης του.

---

## 5. Role descriptions

Παράφραση από κεφ. 3.2 (+ κεφ. 4 όπου σημειώνεται). Προτεινόμενο πεδίο
`role_description` (Text, nullable) στο `Country` model — δεν υπάρχει ακόμα
στο schema, βλ. PROJECT_PLAN.md.

**European Union**: Ο σημαντικότερος εξωτερικός δρώντας στην εξομάλυνση των
σχέσεων. Μοχλός η οικονομική εξάρτηση και των δύο (IPA III: 1.5δις Σερβία/600εκ
Κόσοβο· 78% FDI Σερβίας ευρωπαϊκά· 60% εμπορίου Σερβίας με ΕΕ το 2023).
Χρησιμοποιεί την ευρωπαϊκή προοπτική της Σερβίας ως εργαλείο πίεσης· κύριος
μεσολαβητής σε Βρυξέλλες και Οχρίδα. Θέτει ως προαπαιτούμενο ένταξης Κοσόβου
την εφαρμογή της Συμφωνίας Βρυξελλών· εσωτερικά διχασμένη (5 μέλη — Ισπανία/
Ελλάδα/Κύπρος/Σλοβακία/Ρουμανία — δεν αναγνωρίζουν).

**United States**: Στρατηγικό βάρος στα Δ. Βαλκάνια· προωθεί ανεξαρτησία
Κοσόβου και ενσωμάτωση στην Ευρωατλαντική σφαίρα. Εργαλεία: USAID (1.2δις
2021-2025), MCC (300εκ Σερβία/500εκ Κόσοβο για ενεργειακή αποδέσμευση από
Ρωσία/Κίνα), Camp Bondsteel, FMF/IMET. Στόχος: περιορισμός ρωσικής/κινεζικής
επιρροής. Πρωταγωνιστικός ρόλος στην άρση δασμών 2019-2020 (Trump/Grenell,
οικονομική διπλωματία).

**Russia**: Ισχυρότερος σύμμαχος Σερβίας στην αποτροπή αναγνώρισης Κοσόβου.
Μοχλοί: απειλή βέτο ΟΗΕ, στρατιωτικός προμηθευτής (MiG-29, Pantsir-S1),
ενεργειακός έλεγχος (>80% φυσικού αερίου μέσω Gazprom, ελέγχει NIS). Στηρίζει
το σερβικό στοιχείο στη Β. Μιτρόβιτσα. Στα Γενικά Συμπεράσματα: εκμεταλλεύεται
τη διένεξη ως μοχλό πίεσης προς τη Δύση, με πρακτικές υβριδικού πολέμου,
εμποδίζοντας ψηφίσματα που νομιμοποιούν το νέο status quo.

**China**: Δεύτερος μεγαλύτερος οικονομικός εταίρος Σερβίας μετά την ΕΕ. Δεν
αναγνωρίζει το Κόσοβο (συνδέεται με την πολιτική της έναντι Ταϊβάν, ερμηνεία
Remedial Secession). BRI, >10δις δάνεια 2010-2023, μηδενικές σχέσεις με Κόσοβο.
Σταθερή στήριξη στη Σερβία, αποτρεπτικός ρόλος στην είσοδο Κοσόβου σε διεθνείς
οργανισμούς.

**Albania**: Ισχυρότερος πολιτικός σύμμαχος Κοσόβου· πρώτη χώρα που αναγνώρισε
την ανεξαρτησία. Κοινά υπουργικά συμβούλια, διακρατικές συμφωνίες, κοινή
εθνική/πολιτισμική/γλωσσική ταυτότητα. Το ΑΕΠ Κοσόβου εξαρτάται από αλβανική
δραστηριότητα. Η Σερβία την βλέπει ως παράγοντα αποσταθεροποίησης.

**NATO**: Παρουσία στο Κόσοβο μέσω KFOR από 1999· αποτροπή συγκρούσεων,
παράγοντας σταθερότητας. Επέμβαση 1999 (Allied Force) που ανέτρεψε τη
στρατιωτική BATNA της Σερβίας. Σερβία τη βλέπει ως κατοχή, Κόσοβο ως εγγύηση
ασφάλειας.

**United Nations**: UNMIK από 1999· επιτήρηση ανθρωπίνων δικαιωμάτων,
παρακολούθηση διαπραγματεύσεων, συντονιστής KFOR/ΟΑΣΕ. Ψήφισμα 1244. Ανέθεσε
το σχέδιο Ahtisaari.

**OSCE (ΟΑΣΕ)**: Πολιτική σταθερότητα μέσω παρακολούθησης εκλογών, προστασίας
ανθρωπίνων δικαιωμάτων, θεσμικών μεταρρυθμίσεων. Εποπτεία δημοτικών εκλογών
Κοσόβου 2013.

**India**: Μεταξύ των χωρών που αρνήθηκαν να αναγνωρίσουν την ανεξαρτησία
(2008), επικαλούμενη παραβίαση εθνικής κυριαρχίας και αρχών Διεθνούς Δικαίου.

**ICJ**: Γνωμοδότηση 2010 (προσφυγή Σερβίας): η διακήρυξη ανεξαρτησίας δεν
παραβίαζε το διεθνές δίκαιο, αλλά ούτε το νομιμοποιούσε.

---

## 6. Kosovo gap — political_status (1999-2007)

Από `thesis_seed_data.md` §4 — λύνει το ζήτημα του `political_status` flag. Η
διπλωματική τεκμηριώνει ρητά (σελ. 40-43, 3.1.2):

- Το Κόσοβο 1999-2008 ήταν **υπό διεθνή διοίκηση (UNMIK)**, βάσει Ψηφίσματος 1244.
- **«Δεν διέθετε τραπεζικό σύστημα ή εθνικό νόμισμα και δική του νομισματική
  πολιτική»** — χρησιμοποιούσε το ευρώ χωρίς να είναι στην ευρωζώνη.
- **«Η διεθνής κοινότητα κάλυπτε το 90% των δημοσίων δαπανών.»**
- **«Απουσία εγχώριας αγοράς ομολόγων»** — αδυναμία αυτοχρηματοδότησης.
- Η KFOR κατείχε **«de facto υπέρτατη εξουσία»**, λειτουργώντας υπεράνω της
  τοπικής νομοθεσίας.

**Άρα:** το `political_status` flag = `INTERNATIONAL_ADMINISTRATION` για Kosovo
1999-2007 είναι πλήρως τεκμηριωμένο ΑΠΟ ΤΗΝ ΙΔΙΑ ΤΗ ΔΙΠΛΩΜΑΤΙΚΗ, όχι από
εξωτερική σύμβαση. Η αδυναμία μέτρησης δεδομένων Κοσόβου προ-2008 δεν είναι
κενό δεδομένων — είναι το ίδιο το εύρημα της ασυμμετρίας.

**Απόφαση ήδη ληφθείσα (βλ. PROJECT_PLAN.md/PROJECT_STATUS.md):** αυτό μπαίνει
ΜΟΝΟ ως context στο system prompt του LLM (`SHARED_PREAMBLE` στο
`llm_prompts.py`), ΟΧΙ ως νέο πεδίο/migration στο `Country` model.

---

## 7. Research conclusions (κεφ. 4, δρώντες)

Ρητά συμπεράσματα της εργασίας για τους δρώντες — κρίσιμα για το LLM synthesis/
compare context, γιατί είναι το «τι σημαίνει» η συμμετοχή των δρώντων. Μεταφέρεται
**ολόκληρο**, χωρίς σύμπτυξη.

**Θεμελιώδες: το πλαίσιο είναι εξαρχής πολυδιάστατο.** Οι δύο πλευρές
διαπραγματεύονται σε περιβάλλον όπου «οι μεγάλες δυνάμεις (ΗΠΑ, Ρωσία, ΕΕ,
Κίνα κλπ) καθορίζουν τα περιθώρια δράσης της εκάστοτε οντότητας και ενίοτε τις
διαπραγματευτικές δυναμικές». Οι δρώντες ΔΕΝ είναι διακοσμητικοί — καθορίζουν
τη διαπραγμάτευση.

**Για το Κόσοβο**: Η βασική πηγή της διαπραγματευτικής του ισχύος ΔΕΝ
προέρχεται από εσωτερική αυτάρκεια αλλά από την υποστήριξη (στρατιωτική +
οικονομική) των μεγάλων δυνάμεων (ΗΠΑ, ΕΕ). Δεν διαθέτει ανεξάρτητη BATNA — η
ισχύς του διαμορφώνεται «κατά κύριο λόγο από τη στάση της Δύσης». Παραμένει
εξαρτημένο, ευάλωτο.

**Για τη Σερβία**: Μετά την επέμβαση ΝΑΤΟ 1999 (που μείωσε δραστικά τη
στρατιωτική BATNA της), ανασυγκροτήθηκε και διατηρεί «σταθερή BATNA βασισμένη
σε διπλωματική, οικονομική και ενεργειακή στήριξη από Ρωσία και Κίνα». Μετά το
2008: πολυδιάστατη σχέση — στενή οικονομική συνεργασία με ΕΕ (προενταξιακά) ΚΑΙ
ταυτόχρονα στενές σχέσεις με Ρωσία/Κίνα, παρά τις πιέσεις μετά τον πόλεμο στην
Ουκρανία.

**Η μετατόπιση τύπου ισχύος (ΚΕΝΤΡΙΚΟ ΕΥΡΗΜΑ ΓΙΑ ΤΟ COMPARE):**
- 1989-1999: Σερβία = στρατιωτική επιβολή + άκαμπτες κόκκινες γραμμές (μιλιταριστική).
- 1999: επέμβαση ΝΑΤΟ ανατρέπει — στρατιωτική ισχύς ΝΑΤΟ κυριαρχεί.
- Μετά 2008: Σερβία μετασχηματίζει ισχύ σε ΟΙΚΟΝΟΜΙΚΗ/ΔΙΠΛΩΜΑΤΙΚΗ (ΕΕ + Ρωσία/Κίνα).
- 2013-2023: ΕΕ κυριαρχεί μέσω οικονομικής μόχλευσης.

Δηλαδή: στρατιωτική μόχλευση (1999) → οικονομική μόχλευση (2013+). Ποιος
δρώντας «κρατάει» τη διαπραγμάτευση αλλάζει. (Αυτό είναι ακριβώς το contrast
που το `/compare` endpoint ήδη αναδεικνύει μεταξύ Rambouillet 1999 και
Βρυξέλλες 2013 — βλ. session log.)

**Το γεωπολιτικό χάσμα**: Η εφαρμογή διεθνών κανόνων «καθορίζεται κυρίως από
τα γεωπολιτικά και στρατηγικά συμφέροντα των κρατών». Η Remedial Secession
«εργαλειοποιείται από τις μεγάλες δυνάμεις ανάλογα με τα στρατηγικά τους
συμφέροντα». Δύση (ΗΠΑ/ΕΕ/ΝΑΤΟ) στηρίζει ανεξαρτησία· Ανατολή (Ρωσία/Κίνα) την
εμποδίζει· 5 κράτη ΕΕ διατηρούν «έννομο συμφέρον» μη-αναγνώρισης (φόβος
εσωτερικών αυτονομιστικών κινημάτων).

**Το τελικό συμπέρασμα**: Το Κόσοβο λειτουργεί ως «de facto ανεξάρτητο κράτος
χωρίς πλήρη διεθνή νομιμοποίηση». Οι παρεμβάσεις των μεγάλων δυνάμεων + η
εσωτερική πολιτική δυναμική «καθορίζουν τους διαθέσιμους πόρους για την
εξεύρεση λύσεων». Οι διαπραγματεύσεις μένουν σε φαύλο κύκλο προσωρινών
συμβιβασμών (Two-Level Game του Putnam: εσωτερικές πιέσεις περιορίζουν το win set).

---

## 8. Design decisions log (ιστορικό — από `SEED_DATA_SPEC.md` §6)

Πίνακας αποφάσεων όπως τέθηκε αρχικά, με σημείωση κατάστασης. Κρατιέται
ολόκληρος για ακαδημαϊκή αξία (δείχνει συνειδητές αποφάσεις, όχι παραλείψεις).

| # | Ζήτημα | Πρόταση | Κατάσταση |
|---|---|---|---|
| 1 | Πεδίο `confidence` στο Indicator | Ναι — φθηνό, ενισχύει το Limitations | ✅ αποφασίστηκε και υλοποιήθηκε (2026-08-02), βλ. PROJECT_STATUS.md — enum `EXACT/CHART_READ/RANGE`, nullable |
| 2 | Πεδίο `implementation_success` στο NegotiationEvent | Ναι — είναι ο άξονας της οθόνης Συμπερασμάτων | ✅ αποφασίστηκε και υλοποιήθηκε (2026-08-02), βλ. PROJECT_STATUS.md — Float 0.0-1.0, nullable |
| 3 | Military data gap | Επιλογή Γ: proxies τώρα (boolean/index), SIPRI ως Future Work | ✅ Επιλογή Γ ακολουθήθηκε στην πράξη — `military_expenditure_pct_gdp` (Serbia)/`troop_presence_index` (Kosovo) είναι οι μόνοι military indicators seeded, τα boolean markers του §2.3 δεν μπήκαν. ⚠️ Ανοιχτό: Serbia `military_expenditure_pct_gdp` προέρχεται στην πράξη από live World Bank/SIPRI API, όχι από τη διπλωματική — βλ. "Ανοιχτό ζήτημα" στο CLAUDE.md |
| 4 | Ανεργία Κοσόβου 2000 (11,5% vs 40-50%) | `is_verified=false` + εξαίρεση από Power Index | ⏸ θεωρητική — η τιμή του 2000 δεν μπήκε καθόλου στο `seed.py`, άρα δεν χρειάστηκε ποτέ να εφαρμοστεί το φίλτρο |
| 5 | IPA 2,79 δις vs 2,2 δις | Κρατάμε 2790, τεκμηρίωση και των δύο πηγών | ⏸ deferred — το `eu_preaccession_funds` indicator δεν έχει μπει ακόμα στο `seed.py` (§Future Work) |
| 6 | ΑΕΠ κατά κεφαλήν σε EUR-2003 vs USD | Δύο ξεχωριστοί indicator_types με διαφορετικό unit | ⏸ deferred — το `GDP_per_capita` Κοσόβου δεν έχει μπει ακόμα στο `seed.py` (§Future Work) |

**Legend:** ✅ αποφασίστηκε ΚΑΙ υλοποιήθηκε · ⏸ αποφασίστηκε σε επίπεδο σχεδίου αλλά το υποκείμενο indicator δεν είναι ακόμα seeded (§Future Work στο `seed.py`).

---

## 9. Μεθοδολογική θεμελίωση — Power Index vs. CINC (2026-08-21)

> ### ⚠️ ΡΗΤΗ ΔΗΛΩΣΗ — τα ποσοστά στάθμισης είναι δική μας θεωρία, ΟΧΙ παραπομπή
>
> Τα συγκεκριμένα ποσοστά στάθμισης που χρησιμοποιεί ο κώδικας —
> **Power Index: Economic 40% / Military 40% / Social 20%** (`POWER_INDEX_WEIGHTS`,
> `services/analytics.py`) και **Window Score: συμμετρία ισχύος 50% / αμοιβαία
> πτωτική τάση 30% / κοινωνική πίεση 20%** (`calculate_window_score`) — **ΔΕΝ
> παραπέμπουν σε καμία εξωτερική ακαδημαϊκή πηγή, μεθοδολογία ή δημοσίευση.**
> Δεν είναι αριθμοί που πάρθηκαν από κάποιο υπάρχον σύστημα δεικτών ισχύος
> (ούτε καν από το CINC παρακάτω, που δεν χρησιμοποιεί καθόλου στάθμιση —
> είναι απλός ισοβαρής μέσος όρος 6 συνιστωσών, 1/6 η καθεμία). Είναι **δική
> μας, a priori θεωρητική επιλογή** — ερευνητική κρίση για το τι θεωρούμε πιο
> καθοριστικό σε αυτό το πλαίσιο διαπραγμάτευσης, χωρίς εμπειρική παραγωγή
> (καμία regression/PCA/βελτιστοποίηση πάνω στα δεδομένα) και χωρίς
> βιβλιογραφική παραπομπή για τα ίδια τα ποσοστά.
>
> Αυτό είναι ξεχωριστό ζήτημα από την προέλευση των ΔΕΔΟΜΕΝΩΝ (indicators,
> events) — εκείνα ΕΙΝΑΙ τεκμηριωμένα/παραπεμπόμενα (διπλωματική, World Bank,
> SIPRI, Freedom House, βλ. ενότητες 1-3 παραπάνω). Το ζήτημα εδώ αφορά
> αποκλειστικά τη ΣΤΑΘΜΙΣΗ (τα ποσοστά %) που συνδυάζει αυτά τα δεδομένα σε
> ένα σύνθετο σκορ — αυτή η επιλογή είναι αμιγώς δική μας. Αν σου ζητηθεί στην
> υπεράσπιση να το δικαιολογήσεις, η ειλικρινής απάντηση είναι: "θεωρητικά
> τεκμηριωμένη επιλογή σχεδιασμού μέσα στο πλαίσιο της έρευνάς μου, όχι
> παραπομπή σε καθιερωμένη μεθοδολογία" — βλ. και σημείο 2 παρακάτω για την
> πλήρη σύγκριση με το CINC.

**Έμπνευση, όχι αντιγραφή.** Το Power Index αυτού του project εντάσσεται στην
παράδοση σύνθετων δεικτών εθνικής ισχύος της Διεθνούς Πολιτικής, με κεντρικό
σημείο αναφοράς το **CINC (Composite Index of National Capability)** του
Correlates of War project (Singer, Bremer & Stuckey 1972) — αλλά είναι μια
σκόπιμα διαφορετική προσαρμογή στο πλαίσιο μιας συγκεκριμένης διμερούς
διαπραγμάτευσης, όχι υλοποίηση ή αντιγραφή του CINC.

**Τι είναι το CINC:** έξι συνιστώσες — συνολικός πληθυσμός, αστικός
πληθυσμός, παραγωγή σιδήρου/χάλυβα, κατανάλωση πρωτογενούς ενέργειας,
στρατιωτικές δαπάνες, στρατιωτικό προσωπικό — η καθεμία εκφρασμένη ως
μερίδιο (%) του **παγκόσμιου συνόλου** του έτους, με τελικό σκορ τον απλό
μέσο όρο των έξι μεριδίων: `(TPR+UPR+ISPR+ECR+MER+MPR)/6`. Σχεδιάστηκε για
διαχρονική σύγκριση όλων των κρατών του διεθνούς συστήματος (1816-σήμερα),
με έμφαση σε "σκληρή" βιομηχανική/δημογραφική/στρατιωτική ισχύ (πηγή:
Correlates of War, *National Material Capabilities v7.0* documentation·
[en.wikipedia.org/wiki/Composite_Index_of_National_Capability](https://en.wikipedia.org/wiki/Composite_Index_of_National_Capability)).

**Γιατί το Power Index ΔΕΝ είναι CINC — ρητές διαφορές:**

1. **Διαφορετικές συνιστώσες.** Το CINC βασίζεται σε δείκτες βιομηχανικής
   εποχής (χάλυβας, ενέργεια) άσχετους με τη σημερινή Σερβία/Κόσοβο. Το
   Power Index χρησιμοποιεί ECONOMIC (ρυθμός/μέγεθος ΑΕΠ, ανεργία),
   MILITARY (στρατιωτικές δαπάνες % ΑΕΠ), SOCIAL_UNREST (Freedom House,
   θεσμική σταθερότητα) — δείκτες σχετικούς με σύγχρονη διαπραγματευτική
   μόχλευση, όχι βιομηχανική εποχή.
2. **Διαφορετική λογική στάθμισης.** Το CINC είναι ισοβαρής μέσος όρος 6
   συνιστωσών χωρίς θεωρητική ιεράρχηση μεταξύ τους. Το Power Index έχει
   a priori βάρη 40/40/20 (Economic/Military/Social) — δική μου θεωρητική
   κρίση για το τι μετράει περισσότερο σε αυτό το πλαίσιο, όχι εμπειρικά
   παραγόμενο βάρος (καμία regression/PCA από τα δεδομένα).
3. **Διαφορετικό εύρος σύγκρισης.** Το CINC κανονικοποιεί ως μερίδιο του
   ΠΑΓΚΟΣΜΙΟΥ συνόλου (>190 κράτη). Το Power Index κανονικοποιεί σε
   σταθερά, a priori όρια ανά indicator_type (π.χ. GDP $1-100δισ, βλ.
   ενότητα 3.5) επιλεγμένα ειδικά για το ζευγάρι Σερβία/Κόσοβο, όχι για
   παγκόσμια σύγκριση.
4. **Το CINC αγνοεί εντελώς τη θεσμική/κοινωνική διάσταση** ("μετράει μόνο
   hard power" — ομόφωνη παρατήρηση βιβλιογραφίας, βλ. πηγές παρακάτω). Το
   Power Index συμπεριλαμβάνει ρητά SOCIAL_UNREST (20%) ακριβώς επειδή
   είναι κρίσιμο για διαπραγματευτική ωριμότητα (Zartman ripeness) — κάτι
   που το CINC δεν πιάνει καθόλου.
5. **Το CINC θα ήταν δομικά ακατάλληλο για αυτό το ζευγάρι.** Το Κόσοβο
   είναι πολύ νέο κράτος (2008), με μηδενική βιομηχανική παραγωγή χάλυβα
   και αμελητέο μερίδιο παγκόσμιου πληθυσμού/ενέργειας — ένα CINC score
   Κοσόβου θα ήταν σχεδόν μηδέν σε κάθε έτος, ανεξάρτητα από την
   πραγματική διαπραγματευτική δυναμική. Αντίστοιχο δομικό πρόβλημα
   ("ταβάνι" που δεν κινείται με την πραγματική δυναμική) βρέθηκε ήδη
   εμπειρικά με το γραμμικό GDP scaling πριν διορθωθεί με λογαριθμική
   κλίμακα (βλ. ενότητα 3.5) — επιπλέον τεκμηρίωση γιατί χρειάστηκε δική
   μας προσαρμογή αντί άμεσης υιοθέτησης καθιερωμένου δείκτη.

**Άλλοι δείκτες εθνικής ισχύος που εντοπίστηκαν στη βιβλιογραφική επισκόπηση**
(αναφέρονται για πληρότητα, ΚΑΝΕΝΑΣ δεν υιοθετήθηκε — ίδιο πρόβλημα κλίμακας/
συνάφειας με το CINC για αυτό το ζευγάρι): Global Power Index (GPI, προσθέτει
πυρηνικά οπλοστάσια/R&D), Comprehensive National Power (CNP, κινεζική
παράδοση IR), Elcano Global Presence Index, DiME Index, Structural Network
Power Index (SNPI). Γνωστή κριτική στο CINC γενικά (Carnegie Endowment 2026,
"Methods of National Power Analysis: Pitfalls and Best Practices"): η ισχύς
είναι πολυδιάστατη, τα σύνθετα numeric indices έχουν "μικτή επιτυχία" όταν
κρίνονται έναντι του ιστορικού ρεκόρ, και η σύγκριση μεταξύ κρατών πολύ
διαφορετικού μεγέθους (όπως Σερβία/Κόσοβο) είναι γνωστά προβληματική όταν η
ομάδα σύγκρισης αλλάζει.

**Πηγές:** Correlates of War Project, *National Material Capabilities v7.0*
([correlatesofwar.org](https://correlatesofwar.org/data-sets/national-material-capabilities/))
· [Composite Index of National Capability — Wikipedia](https://en.wikipedia.org/wiki/Composite_Index_of_National_Capability)
· Carnegie Endowment for International Peace (2026), ["Methods of National Power Analysis: Pitfalls and Best Practices"](https://carnegieendowment.org/research/2026/04/methods-of-national-power-analysis-pitfalls-and-best-practices)
· Μεθοδολογική επισκόπηση εναλλακτικών δεικτών (GPI/CNP/Elcano/DiME/SNPI):
[Oxford Academic, *Chinese Journal of International Politics*](https://academic.oup.com/cjip/article/19/3/237/8711324).
