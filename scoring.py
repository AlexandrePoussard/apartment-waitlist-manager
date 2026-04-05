"""
WohnTraum Zürich — Applicant Scoring Module
The algorithm that decides your fate. Bureaucratically.
"""

from datetime import date, datetime


GERMAN_SCORES = {
    "A1": 0, "A2": 0, "B1": 0,
    "B2": 5, "C1": 8, "C2": 10
}

APARTMENTS_PER_YEAR = 20  # Very optimistic. Don't tell the applicants.


def compute_score(
    registered_at,
    years_in_zurich: int,
    income_chf: int,
    family_size: int,
    german_level: str,
    zurisack_compliant: bool,
) -> float:
    """
    Compute the official WohnTraum waiting list score.
    Maximum theoretical score: 100 pts.
    """
    # Years on waitlist (capped at 5 years → max 40 pts)
    if isinstance(registered_at, str):
        reg_date = datetime.strptime(registered_at[:10], "%Y-%m-%d").date()
    else:
        reg_date = registered_at

    years_on_waitlist = min((date.today() - reg_date).days / 365.25, 5)
    waitlist_pts = round(years_on_waitlist * 8, 2)

    # Years in Zürich (capped at 10 → max 20 pts)
    zurich_pts = min(years_in_zurich, 10) * 2

    # Income bracket (10 pts if < 80k CHF/year)
    income_pts = 10 if income_chf < 80_000 else 0

    # Family size (5 pts per member, max 15 pts → cap at 3)
    family_pts = min(family_size, 3) * 5

    # German level
    german_pts = GERMAN_SCORES.get(german_level.upper(), 0)

    # Züri-Sack compliance bonus
    zurisack_pts = 5 if zurisack_compliant else 0

    total = (
        waitlist_pts
        + zurich_pts
        + income_pts
        + family_pts
        + german_pts
        + zurisack_pts
    )
    return round(total, 2)


def get_waitlist_rank(applicant_id: int, all_applicants: list) -> int:
    """
    Returns 1-based rank of the applicant among all 'pending' applicants,
    sorted by score descending.
    """
    pending = sorted(
        [a for a in all_applicants if a["status"] in ("pending", "under_review")],
        key=lambda x: x["score"],
        reverse=True,
    )
    for i, a in enumerate(pending, start=1):
        if a["id"] == applicant_id:
            return i
    return -1  # Not in the active queue (approved / rejected)


def estimate_wait_years(rank: int) -> float:
    """
    Estimates how many years until an apartment becomes available.
    Returns a precise-sounding float to inspire false confidence.
    Assumes APARTMENTS_PER_YEAR openings per year.
    """
    if rank <= 0:
        return 0.0
    years = rank / APARTMENTS_PER_YEAR
    return round(years, 1)


def sarcastic_wait_message(wait_years: float) -> str:
    """Returns a contextually appropriate (devastating) wait time message."""
    if wait_years < 0.5:
        return f"Estimated wait: {wait_years} years. Don't celebrate yet — paperwork takes 6 months minimum."
    elif wait_years < 2:
        return f"Estimated wait: {wait_years} years. You may wish to inform your employer."
    elif wait_years < 5:
        return f"Estimated wait: {wait_years} years. We suggest taking up a hobby. Several hobbies."
    elif wait_years < 10:
        return f"Estimated wait: {wait_years} years. Have you considered renting? In Winterthur?"
    elif wait_years < 20:
        return f"Estimated wait: {wait_years} years. Your children may have better luck. Maybe."
    else:
        return f"Estimated wait: {wait_years} years. We recommend informing your next of kin."
