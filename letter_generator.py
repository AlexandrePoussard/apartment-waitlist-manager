"""
WohnTraum Zürich — Official Letter Generator
Producing bureaucratic Swiss correspondence since 1987.
"""

from datetime import date
import random


REJECTION_INTROS = [
    "It is our honour to inform you that",
    "After careful review of your extensive documentation, we regret to inform you that",
    "With great sorrow and following thorough internal deliberation, we must inform you that",
    "The Housing Allocation Commission, in its 847th session, voted 7:0 to conclude that",
]

REJECTION_SUGGESTIONS = [
    "We recommend exploring the charms of Basel — a city with demonstrably shorter waiting lists.",
    "Have you considered Basel? The rents are comparable and the Rhine swimming is most invigorating.",
    "Bern also offers a high quality of life and — we are told — occasionally has available apartments.",
    "Perhaps now is the time to discover the advantages of Winterthur. Direct S-Bahn to Zürich, only 20 minutes.",
]

APPROVAL_CAVEATS = [
    "Please note that this approval is subject to the complete verification of all submitted documents.",
    "This provisional approval only becomes legally binding after the signing of a total of 14 forms.",
    "We reserve the right to reconsider this decision should any new circumstances come to light.",
]

ZURISACK_REMINDERS = [
    "We remind you, as a precaution, that the proper use of the Züri-Sack is not only a legal obligation, but a sign of commitment to our community.",
    "Please note: waste disposal inspections are carried out quarterly. The correct Züri-Sack is mandatory and enforced with friendly firmness.",
    "As a future tenant of the WohnTraum cooperative, you are required to use the official Züri-Sack. This was already confirmed in your application. We are merely reminding you. Three times.",
]


def generate_rejection_letter(
    applicant_name: str,
    applicant_email: str,
    rank: int,
    wait_years: float,
    apartment_address: str = None,
) -> str:
    today = date.today().strftime("%d. %B %Y")
    intro = random.choice(REJECTION_INTROS)
    suggestion = random.choice(REJECTION_SUGGESTIONS)

    apt_line = ""
    if apartment_address:
        apt_line = f"regarding the apartment at {apartment_address}"
    else:
        apt_line = "regarding your application for a cooperative apartment"

    letter = f"""
WohnTraum Zürich Cooperative
Bahnhofstrasse 42, 8001 Zürich
Tel: +41 44 000 00 00
wohntraum@example.ch

Zürich, {today}

{applicant_name}
{applicant_email}


Re: Decision on Your Housing Application — {apt_line}

Dear {applicant_name.split()[0]},

{intro} your application {apt_line} cannot be considered at the present time.

The WohnTraum Zürich Cooperative receives several thousand applications each year from highly qualified individuals, all of whom harbour an irresistible desire to live in Zürich. We have reviewed your documents with the utmost care — in fact, we reviewed them multiple times — and have concluded that it was simply not meant to be on this occasion.

Your current waitlist rank: {rank}
Estimated waiting time: {wait_years} years

Please understand that this is in no way a reflection of your personality, character, or qualities as a tenant. It is simply mathematics. And Zürich.

{suggestion}

Your application naturally remains active and you will be notified once your position on the waitlist has improved significantly. This could well occur in approximately {wait_years} years.

We thank you for your trust in the WohnTraum Zürich Cooperative and wish you all the best in your continued search for housing.

Yours sincerely and with genuine regret,

Dr. Ursula Kägi-Müller
Head of the Housing Allocation Commission
WohnTraum Zürich Cooperative

---
This decision is final and binding in accordance with Swiss Civil Code Art. 271.
WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — All rejections are final.
    """.strip()

    return letter


def generate_approval_letter(
    applicant_name: str,
    applicant_email: str,
    apartment_address: str,
    apartment_kreis: int,
    rent_chf: int,
    zurisack_compliant: bool,
) -> str:
    today = date.today().strftime("%d. %B %Y")
    caveat = random.choice(APPROVAL_CAVEATS)
    zurisack_reminder = random.choice(ZURISACK_REMINDERS)

    zurisack_line = ""
    if zurisack_compliant:
        zurisack_line = f"\nYour confirmed Züri-Sack compliance has been noted favourably. {zurisack_reminder}"
    else:
        zurisack_line = f"\nATTENTION: In your application you did NOT confirm Züri-Sack compliance. {zurisack_reminder} This is your first and final reminder."

    letter = f"""
WohnTraum Zürich Cooperative
Bahnhofstrasse 42, 8001 Zürich
Tel: +41 44 000 00 00
wohntraum@example.ch

Zürich, {today}

{applicant_name}
{applicant_email}


Re: PROVISIONAL APPROVAL — Apartment {apartment_address}, Kreis {apartment_kreis}

Dear {applicant_name.split()[0]},

It is an extraordinary and exceptionally rare pleasure to inform you that the Housing Allocation Commission of the WohnTraum Zürich Cooperative, in its extraordinary session, has resolved to PROVISIONALLY assign you the apartment at {apartment_address} (Kreis {apartment_kreis}).

We emphasise: PROVISIONALLY.

Apartment details:
- Address: {apartment_address}, Zürich
- Kreis: {apartment_kreis}
- Monthly rent: CHF {rent_chf:,}

{caveat}

Next steps (all mandatory):
1. Confirm this offer in writing within 5 working days
2. Submit completed forms WT-2024-A through WT-2024-M
3. Schedule a viewing appointment (waiting time: 3–6 weeks)
4. Sign the tenancy agreement in triplicate
5. Provide proof of personal liability insurance
6. Reconfirm your Züri-Sack compliance in writing
{zurisack_line}

Please note that failure to fulfil any of the above conditions will result in automatic withdrawal of this offer and notification of the next person on the waitlist.

We congratulate you on this extraordinary stroke of fortune and trust that you will prove yourself a worthy tenant of our cooperative.

Yours formally and with restrained delight,

Heinrich Zünd-Keller
President, WohnTraum Zürich Cooperative
Member: Swiss Association of Housing Cooperatives

Cc: Housing Allocation Commission (7 members)
    WohnTraum Legal Department
    Züri-Sack Inspection Authority Zürich
    Archive (2 copies)

---
This approval is provisional and subject to Swiss Tenancy Law OR Art. 253 et seq.
WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — All rejections are final and binding.
    """.strip()

    return letter


def generate_letter(
    letter_type: str,
    applicant: dict,
    rank: int = 0,
    wait_years: float = 0.0,
    apartment: dict = None,
) -> str:
    """
    Unified entry point.
    letter_type: 'rejection' | 'approval'
    """
    if letter_type == "rejection":
        apt_address = apartment["address"] if apartment else None
        return generate_rejection_letter(
            applicant_name=applicant["name"],
            applicant_email=applicant["email"],
            rank=rank,
            wait_years=wait_years,
            apartment_address=apt_address,
        )
    elif letter_type == "approval":
        if apartment is None:
            raise ValueError("An apartment must be provided for an approval letter.")
        return generate_approval_letter(
            applicant_name=applicant["name"],
            applicant_email=applicant["email"],
            apartment_address=apartment["address"],
            apartment_kreis=apartment["kreis"],
            rent_chf=apartment["rent_chf"],
            zurisack_compliant=bool(applicant.get("zurisack_compliant", False)),
        )
    else:
        raise ValueError(f"Unknown letter_type: {letter_type}")
