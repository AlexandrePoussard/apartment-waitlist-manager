import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "wohntraum.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            income_chf INTEGER NOT NULL,
            family_size INTEGER NOT NULL,
            years_in_zurich INTEGER NOT NULL,
            german_level TEXT NOT NULL,
            registered_at DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            score REAL DEFAULT 0.0,
            zurisack_compliant BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            kreis INTEGER NOT NULL,
            rooms REAL NOT NULL,
            size_m2 INTEGER NOT NULL,
            rent_chf INTEGER NOT NULL,
            has_balcony BOOLEAN NOT NULL DEFAULT 0,
            pet_friendly BOOLEAN NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'available'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id INTEGER NOT NULL REFERENCES applicants(id),
            apartment_id INTEGER NOT NULL REFERENCES apartments(id),
            applied_at DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


# ── Applicant queries ──────────────────────────────────────────────────────────

def get_all_applicants():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM applicants ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_applicant(applicant_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM applicants WHERE id = ?", (applicant_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_applicant(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO applicants
            (name, email, income_chf, family_size, years_in_zurich,
             german_level, registered_at, status, score, zurisack_compliant)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        data["name"], data["email"], data["income_chf"], data["family_size"],
        data["years_in_zurich"], data["german_level"], data["registered_at"],
        data.get("status", "pending"), data.get("score", 0.0),
        int(data.get("zurisack_compliant", False))
    ))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_applicant_status(applicant_id, status):
    conn = get_connection()
    conn.execute(
        "UPDATE applicants SET status = ? WHERE id = ?", (status, applicant_id)
    )
    conn.commit()
    conn.close()


def update_applicant_score(applicant_id, score):
    conn = get_connection()
    conn.execute(
        "UPDATE applicants SET score = ? WHERE id = ?", (score, applicant_id)
    )
    conn.commit()
    conn.close()


def count_applicants():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM applicants").fetchone()
    conn.close()
    return row["cnt"]


def count_approvals_this_year():
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM applicants WHERE status='approved' AND registered_at >= date('now','start of year')"
    ).fetchone()
    conn.close()
    return row["cnt"]


# ── Apartment queries ──────────────────────────────────────────────────────────

def get_all_apartments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM apartments ORDER BY kreis, rooms").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_apartment(apartment_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM apartments WHERE id = ?", (apartment_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_apartment(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO apartments
            (address, kreis, rooms, size_m2, rent_chf, has_balcony, pet_friendly, status)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        data["address"], data["kreis"], data["rooms"], data["size_m2"],
        data["rent_chf"], int(data.get("has_balcony", False)),
        int(data.get("pet_friendly", False)), data.get("status", "available")
    ))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def count_available_apartments():
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM apartments WHERE status='available'"
    ).fetchone()
    conn.close()
    return row["cnt"]


# ── Application queries ────────────────────────────────────────────────────────

def get_all_applications():
    conn = get_connection()
    rows = conn.execute("""
        SELECT ap.*, a.name as applicant_name, apt.address as apartment_address
        FROM applications ap
        JOIN applicants a ON ap.applicant_id = a.id
        JOIN apartments apt ON ap.apartment_id = apt.id
        ORDER BY ap.applied_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_application(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO applications (applicant_id, apartment_id, applied_at, status, notes)
        VALUES (?,?,?,?,?)
    """, (
        data["applicant_id"], data["apartment_id"], data["applied_at"],
        data.get("status", "pending"), data.get("notes", "")
    ))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def has_data():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM applicants").fetchone()
    conn.close()
    return row["cnt"] > 0
