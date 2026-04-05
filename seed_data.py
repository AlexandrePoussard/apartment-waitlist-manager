"""
WohnTraum Zürich — Seed Data Generator
Run this script once to populate the database with fake but plausible data.
"""

import sys
import os
import random
from datetime import date, timedelta

# Allow running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from faker import Faker
import database as db
import scoring

fake = Faker("de_CH")
Faker.seed(42)
random.seed(42)

SWISS_FIRST_NAMES = [
    "Hans", "Peter", "Markus", "Thomas", "Daniel", "Andreas", "Stefan", "Christian",
    "Michael", "Beat", "Reto", "Urs", "Martin", "Lukas", "Felix", "Simon", "Tobias",
    "Anna", "Maria", "Sandra", "Christine", "Claudia", "Monika", "Sabine", "Katharina",
    "Elisabeth", "Ursula", "Heidi", "Brigitte", "Franziska", "Regula", "Vreni", "Esther",
]

SWISS_LAST_NAMES = [
    "Müller", "Meier", "Schmid", "Keller", "Weber", "Huber", "Schneider", "Meyer",
    "Steiner", "Fischer", "Zimmermann", "Brunner", "Widmer", "Kaufmann", "Bauer",
    "Frei", "Moser", "Baumann", "Fuchs", "Koch", "Lüthi", "Küng", "Roth", "Zürcher",
    "Kägi", "Zünd", "Wenger", "Stalder", "Gasser", "Lenz",
]

ZURICH_STREETS = [
    ("Langstrasse", [1, 4]),
    ("Bahnhofstrasse", [1]),
    ("Rämistrasse", [1]),
    ("Limmatquai", [1]),
    ("Seestrasse", [2, 8]),
    ("Bederstrasse", [2]),
    ("Birmensdorferstrasse", [3]),
    ("Zweierstrasse", [3]),
    ("Wiedingstrasse", [3, 9]),
    ("Militärstrasse", [4]),
    ("Rolandstrasse", [4]),
    ("Hardstrasse", [5]),
    ("Escher-Wyss-Platz", [5]),
    ("Josefstrasse", [5]),
    ("Hohlstrasse", [4, 5]),
    ("Winterthurerstrasse", [6, 11]),
    ("Schaffhauserstrasse", [6, 11]),
    ("Gladbachstrasse", [6]),
    ("Susenbergstrasse", [7]),
    ("Hottingerstrasse", [7]),
    ("Seefeldstrasse", [8]),
    ("Feldeggstrasse", [8]),
    ("Kreuzstrasse", [8]),
    ("Albisriederstrasse", [9]),
    ("Altstetten", [9]),
    ("Badenerstrasse", [9, 4]),
    ("Zürichbergstrasse", [7]),
    ("Oerlikonerstrasse", [11]),
    ("Thurgauerstrasse", [11]),
    ("Schwamendingenstrasse", [12]),
    ("Saatlenstrasse", [12]),
    ("Wehntalerstrasse", [11, 12]),
    ("Dübendorfstrasse", [12]),
    ("Forchstrasse", [8]),
    ("Klausstrasse", [8]),
    ("Manessestrasse", [9]),
    ("Friedaustrasse", [9]),
    ("Gloriastrasse", [6]),
    ("Universitätstrasse", [6]),
    ("Voltastrasse", [5]),
]

GERMAN_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
GERMAN_WEIGHTS = [5, 10, 15, 25, 25, 20]  # B2/C1 most common

APPLICANT_STATUSES = ["pending", "under_review", "approved", "rejected"]
APPLICANT_STATUS_WEIGHTS = [50, 25, 10, 15]

APPLICATION_STATUSES = ["pending", "shortlisted", "rejected", "accepted"]
APPLICATION_STATUS_WEIGHTS = [40, 30, 20, 10]

APARTMENT_STATUSES = ["available", "reserved", "occupied"]
APARTMENT_STATUS_WEIGHTS = [40, 20, 40]

ROOMS_OPTIONS = [1.5, 2.5, 3.5, 4.5, 5.5]
ROOMS_WEIGHTS = [10, 30, 35, 20, 5]


def random_swiss_name():
    first = random.choice(SWISS_FIRST_NAMES)
    last = random.choice(SWISS_LAST_NAMES)
    return f"{first} {last}"


def random_street_address():
    street, kreise = random.choice(ZURICH_STREETS)
    number = random.randint(1, 120)
    kreis = random.choice(kreise)
    return f"{street} {number}", kreis


def random_registration_date():
    """Random date between 2018 and 2025."""
    start = date(2018, 1, 1)
    end = date(2025, 6, 30)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_applicants(n=50):
    applicants = []
    for _ in range(n):
        name = random_swiss_name()
        email = f"{name.lower().replace(' ', '.').replace('ü','ue').replace('ä','ae').replace('ö','oe')}@{random.choice(['gmail.com','bluewin.ch','gmx.ch','sunrise.ch','hispeed.ch'])}"
        income = random.choice([
            random.randint(40_000, 79_999),   # low income (most applicants)
            random.randint(80_000, 120_000),  # middle
            random.randint(120_001, 200_000), # high
        ])
        family_size = random.randint(1, 6)
        years_in_zurich = random.randint(0, 40)
        german_level = random.choices(GERMAN_LEVELS, GERMAN_WEIGHTS)[0]
        registered_at = random_registration_date()
        status = random.choices(APPLICANT_STATUSES, APPLICANT_STATUS_WEIGHTS)[0]
        zurisack_compliant = random.choices([True, False], [75, 25])[0]

        score = scoring.compute_score(
            registered_at=registered_at,
            years_in_zurich=years_in_zurich,
            income_chf=income,
            family_size=family_size,
            german_level=german_level,
            zurisack_compliant=zurisack_compliant,
        )

        applicants.append({
            "name": name,
            "email": email,
            "income_chf": income,
            "family_size": family_size,
            "years_in_zurich": years_in_zurich,
            "german_level": german_level,
            "registered_at": registered_at.isoformat(),
            "status": status,
            "score": score,
            "zurisack_compliant": zurisack_compliant,
        })

    inserted_ids = []
    for a in applicants:
        aid = db.insert_applicant(a)
        inserted_ids.append(aid)
    print(f"  Inserted {len(inserted_ids)} applicants.")
    return inserted_ids


def seed_apartments(n=20):
    apartment_ids = []
    used_addresses = set()

    for _ in range(n):
        for _ in range(100):  # retry loop for unique addresses
            address, kreis = random_street_address()
            if address not in used_addresses:
                used_addresses.add(address)
                break

        rooms = random.choices(ROOMS_OPTIONS, ROOMS_WEIGHTS)[0]
        size_m2 = int(rooms * random.randint(22, 30))
        # Zurich rents: brutal
        base_rent = {1.5: 1200, 2.5: 1800, 3.5: 2400, 4.5: 3000, 5.5: 3800}
        rent_chf = base_rent[rooms] + random.randint(-200, 800)
        has_balcony = random.choices([True, False], [35, 65])[0]
        pet_friendly = random.choices([True, False], [20, 80])[0]
        status = random.choices(APARTMENT_STATUSES, APARTMENT_STATUS_WEIGHTS)[0]

        apt_id = db.insert_apartment({
            "address": address,
            "kreis": kreis,
            "rooms": rooms,
            "size_m2": size_m2,
            "rent_chf": rent_chf,
            "has_balcony": has_balcony,
            "pet_friendly": pet_friendly,
            "status": status,
        })
        apartment_ids.append(apt_id)

    print(f"  Inserted {len(apartment_ids)} apartments.")
    return apartment_ids


def seed_applications(applicant_ids, apartment_ids, n=30):
    pairs = set()
    count = 0
    attempts = 0

    while count < n and attempts < n * 10:
        attempts += 1
        applicant_id = random.choice(applicant_ids)
        apartment_id = random.choice(apartment_ids)
        pair = (applicant_id, apartment_id)
        if pair in pairs:
            continue
        pairs.add(pair)

        applied_at = random_registration_date()
        status = random.choices(APPLICATION_STATUSES, APPLICATION_STATUS_WEIGHTS)[0]
        notes_options = [
            "",
            "Sehr interessante Bewerbung. Weitere Prüfung erforderlich.",
            "Einkommensnachweis fehlt.",
            "Züri-Sack-Konformität bestätigt.",
            "Familie bevorzugt grössere Wohnung.",
            "Haustierhalter — bitte Rücksprache.",
            "Referenzen ausstehend.",
            "Priorität aufgrund langer Wartezeit.",
        ]
        notes = random.choice(notes_options)

        db.insert_application({
            "applicant_id": applicant_id,
            "apartment_id": apartment_id,
            "applied_at": applied_at.isoformat(),
            "status": status,
            "notes": notes,
        })
        count += 1

    print(f"  Inserted {count} applications.")


def main():
    print("WohnTraum Zürich — Seeding database...")
    db.init_db()

    if db.has_data():
        print("  Database already contains data. Skipping seed.")
        print("  (Delete wohntraum.db to reseed.)")
        return

    print("  Seeding applicants...")
    applicant_ids = seed_applicants(50)

    print("  Seeding apartments...")
    apartment_ids = seed_apartments(20)

    print("  Seeding applications...")
    seed_applications(applicant_ids, apartment_ids, 30)

    print("Done! The WohnTraum database is ready.")
    print("Remember: your grandchildren may benefit from this data.")


if __name__ == "__main__":
    main()
