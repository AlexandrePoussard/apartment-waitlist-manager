"""
WohnTraum Zürich — Streamlit Application
Genossenschaft WohnTraum Zürich — Since 1987.
Probably your grandchildren will get an apartment.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from datetime import date

import database as db
import scoring as sc
import letter_generator as lg

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WohnTraum Zürich",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Swiss red accent */
    :root {
        --swiss-red: #FF0000;
        --swiss-red-dark: #CC0000;
        --light-grey: #F5F5F5;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FF0000;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 0.95rem;
        color: #666;
        font-style: italic;
        margin-top: 0;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-approved  { background: #d4edda; color: #155724; }
    .badge-pending   { background: #e2e3e5; color: #383d41; }
    .badge-under_review { background: #fff3cd; color: #856404; }
    .badge-rejected  { background: #f8d7da; color: #721c24; }
    .badge-available { background: #d4edda; color: #155724; }
    .badge-reserved  { background: #fff3cd; color: #856404; }
    .badge-occupied  { background: #f8d7da; color: #721c24; }

    /* Kreis chip */
    .kreis-chip {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #FF0000;
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
        line-height: 28px;
        margin-right: 6px;
    }

    /* Apartment card */
    .apt-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        background: white;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .apt-card:hover {
        box-shadow: 0 3px 10px rgba(0,0,0,0.12);
        border-color: #FF0000;
    }

    /* Metric card override */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #CC0000 !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.75rem;
        color: #999;
        padding: 20px 0 8px;
        border-top: 1px solid #eee;
        margin-top: 40px;
    }

    /* Letter box */
    .letter-box {
        background: #fafafa;
        border: 1px solid #ccc;
        border-left: 4px solid #FF0000;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        white-space: pre-wrap;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ── Bootstrap DB ───────────────────────────────────────────────────────────────
db.init_db()


# ── Session state defaults ─────────────────────────────────────────────────────
if "selected_applicant_id" not in st.session_state:
    st.session_state.selected_applicant_id = None
if "selected_apartment_id" not in st.session_state:
    st.session_state.selected_apartment_id = None
if "generated_letter" not in st.session_state:
    st.session_state.generated_letter = ""


# ── Helper utilities ───────────────────────────────────────────────────────────

def status_badge(status: str) -> str:
    label_map = {
        "pending": "Pending",
        "under_review": "Under Review",
        "approved": "Approved",
        "rejected": "Rejected",
        "available": "Available",
        "reserved": "Reserved",
        "occupied": "Occupied",
    }
    label = label_map.get(status, status.title())
    return f'<span class="badge badge-{status}">{label}</span>'


def kreis_chip(k: int) -> str:
    return f'<span class="kreis-chip">{k}</span>'


def no_data_warning():
    st.warning(
        "The database appears to be empty. "
        "Please run **seed_data.py** first:\n\n"
        "```\npython seed_data.py\n```",
        icon="⚠️",
    )


# ── Sidebar navigation ─────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div style="text-align:center; font-size:2rem;">🏔️</div>'
    '<div style="text-align:center; font-weight:800; color:#FF0000; font-size:1.1rem;">WohnTraum Zürich</div>'
    '<div style="text-align:center; font-size:0.7rem; color:#999; margin-bottom:16px;">Since 1987</div>',
    unsafe_allow_html=True,
)

PAGES = [
    "🏠  Dashboard",
    "👥  Applicants",
    "🏢  Apartments",
    "✉️  Letter Generator",
    "➕  Add Applicant",
]
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div style="font-size:0.7rem;color:#bbb;text-align:center;">'
    'Genossenschaft WohnTraum Zürich<br>All rejections are final.</div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    st.markdown('<div class="main-title">🏔️ WohnTraum Zürich</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Genossenschaft WohnTraum Zürich — Since 1987. '
        'Probably your grandchildren will get an apartment.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    applicants = db.get_all_applicants()
    apartments = db.get_all_apartments()

    if not applicants:
        no_data_warning()
        st.stop()

    # ── Metric cards ───────────────────────────────────────────────────────────
    total_applicants = len(applicants)
    available_apts = sum(1 for a in apartments if a["status"] == "available")
    pending = [a for a in applicants if a["status"] in ("pending", "under_review")]
    avg_wait = round(sc.estimate_wait_years(len(pending) // 2), 1) if pending else 0.0
    approvals = sum(1 for a in applicants if a["status"] == "approved")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Applicants", f"{total_applicants:,}", help="Souls hoping for a Zürich apartment")
    with col2:
        st.metric("Available Apartments", available_apts, help="Yes, this number is correct")
    with col3:
        st.metric("Avg. Wait Time", f"{avg_wait} yrs", help="Statistically speaking")
    with col4:
        st.metric("Approvals This Year", approvals, delta=None, help="Suspiciously low. We know.")

    st.markdown("---")

    # ── Charts ─────────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Applicants by Preferred Kreis")

        # Use apartment kreis as a proxy for preference (via applications)
        applications = db.get_all_applications()
        if applications:
            app_df = pd.DataFrame(applications)
            apt_df = pd.DataFrame(apartments)[["id", "kreis"]]
            merged = app_df.merge(apt_df, left_on="apartment_id", right_on="id", how="left")
            kreis_counts = merged.groupby("kreis").size().reset_index(name="count")
            kreis_counts = kreis_counts.sort_values("kreis")
            kreis_counts["kreis"] = kreis_counts["kreis"].apply(lambda x: f"Kreis {x}")
            st.bar_chart(kreis_counts.set_index("kreis")["count"])
        else:
            # Fallback: random distribution based on applicant count
            import random
            kreis_data = pd.DataFrame({
                "Kreis": [f"Kreis {i}" for i in range(1, 13)],
                "Applicants": [random.randint(2, 15) for _ in range(12)],
            })
            st.bar_chart(kreis_data.set_index("Kreis")["Applicants"])

    with col_b:
        st.subheader("Income Distribution (CHF/year)")
        inc_df = pd.DataFrame(applicants)[["income_chf"]]
        st.bar_chart(
            inc_df["income_chf"]
            .apply(lambda x: f"{(x // 20000) * 20}k–{(x // 20000 + 1) * 20}k")
            .value_counts()
            .sort_index()
        )

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Applicant Status Breakdown")
        status_df = pd.DataFrame(applicants)["status"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]
        # Use st.bar_chart as a simple fallback (no plotly dependency)
        st.bar_chart(status_df.set_index("Status")["Count"])

    with col_d:
        st.subheader("Score Distribution")
        score_df = pd.DataFrame(applicants)[["score"]]
        score_df["bucket"] = score_df["score"].apply(lambda x: f"{int(x // 10) * 10}–{int(x // 10) * 10 + 10}")
        st.bar_chart(score_df["bucket"].value_counts().sort_index())

    st.markdown(
        '<div class="footer">WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — '
        'All rejections are final and binding under Swiss Civil Code Art. 271.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — APPLICANTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[1]:
    st.markdown('<div class="main-title">👥 Applicants</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">The waiting list. Every name here is a dream deferred.</div>', unsafe_allow_html=True)
    st.markdown("---")

    applicants = db.get_all_applicants()
    if not applicants:
        no_data_warning()
        st.stop()

    # ── Sidebar filters ────────────────────────────────────────────────────────
    st.sidebar.markdown("### Filters")
    status_opts = ["All"] + sorted(list({a["status"] for a in applicants}))
    sel_status = st.sidebar.selectbox("Status", status_opts)

    german_opts = ["All"] + sorted(list({a["german_level"] for a in applicants}))
    sel_german = st.sidebar.selectbox("German Level", german_opts)

    max_family = max(a["family_size"] for a in applicants)
    sel_family = st.sidebar.slider("Max Family Size", 1, max_family, max_family)

    min_score = st.sidebar.slider("Minimum Score", 0, 100, 0)

    search_query = st.text_input("Search by name or email", placeholder="e.g. Müller or hans@bluewin.ch")

    # Apply filters
    filtered = applicants
    if sel_status != "All":
        filtered = [a for a in filtered if a["status"] == sel_status]
    if sel_german != "All":
        filtered = [a for a in filtered if a["german_level"] == sel_german]
    filtered = [a for a in filtered if a["family_size"] <= sel_family]
    filtered = [a for a in filtered if a["score"] >= min_score]
    if search_query:
        q = search_query.lower()
        filtered = [a for a in filtered if q in a["name"].lower() or q in a["email"].lower()]

    st.write(f"Showing **{len(filtered)}** of {len(applicants)} applicants")

    if not filtered:
        st.info("No applicants match the current filters.")
        st.stop()

    # ── Applicant table ────────────────────────────────────────────────────────
    df = pd.DataFrame(filtered)[[
        "id", "name", "email", "score", "status",
        "income_chf", "family_size", "german_level", "years_in_zurich", "registered_at"
    ]].copy()
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.columns = [
        "ID", "Name", "Email", "Score", "Status",
        "Income (CHF)", "Family", "German", "Yrs in ZH", "Registered"
    ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.NumberColumn(format="%.1f"),
            "Income (CHF)": st.column_config.NumberColumn(format="%d"),
        },
    )

    st.markdown("---")
    st.subheader("Applicant Detail")

    applicant_options = {a["id"]: f"{a['name']} (score: {a['score']:.1f})" for a in filtered}
    selected_id = st.selectbox(
        "Select applicant for details",
        options=list(applicant_options.keys()),
        format_func=lambda x: applicant_options[x],
        key="applicant_detail_select",
    )

    if selected_id:
        applicant = db.get_applicant(selected_id)
        rank = sc.get_waitlist_rank(selected_id, applicants)
        wait_years = sc.estimate_wait_years(rank)
        wait_msg = sc.sarcastic_wait_message(wait_years)

        with st.expander(f"Detail: {applicant['name']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Name:** {applicant['name']}")
                st.markdown(f"**Email:** {applicant['email']}")
                st.markdown(f"**Registered:** {applicant['registered_at']}")
                st.markdown(
                    f"**Status:** {status_badge(applicant['status'])}",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(f"**Income:** CHF {applicant['income_chf']:,}/year")
                st.markdown(f"**Family size:** {applicant['family_size']}")
                st.markdown(f"**Years in Zürich:** {applicant['years_in_zurich']}")
                st.markdown(f"**German level:** {applicant['german_level']}")
            with c3:
                st.markdown(f"**Score:** `{applicant['score']:.2f}` pts")
                if rank > 0:
                    st.markdown(f"**Waitlist rank:** #{rank}")
                    st.markdown(f"**Züri-Sack compliant:** {'Yes ✓' if applicant['zurisack_compliant'] else 'No ✗'}")
                    st.info(f"⏳ {wait_msg}")
                else:
                    st.markdown("*Not currently on active waitlist.*")

            st.markdown("---")
            c_upd, c_let = st.columns(2)

            with c_upd:
                st.markdown("**Update Status**")
                new_status = st.selectbox(
                    "New status",
                    ["pending", "under_review", "approved", "rejected"],
                    index=["pending", "under_review", "approved", "rejected"].index(
                        applicant["status"]
                    ),
                    key=f"status_sel_{selected_id}",
                )
                if st.button("Update Status", key=f"upd_btn_{selected_id}", type="primary"):
                    db.update_applicant_status(selected_id, new_status)
                    st.success(f"Status updated to **{new_status}**.")
                    st.rerun()

            with c_let:
                st.markdown("**Quick Letter**")
                if st.button("Generate Rejection Letter", key=f"rej_btn_{selected_id}"):
                    letter = lg.generate_rejection_letter(
                        applicant_name=applicant["name"],
                        applicant_email=applicant["email"],
                        rank=rank if rank > 0 else 999,
                        wait_years=wait_years,
                    )
                    st.session_state.generated_letter = letter
                    st.session_state.selected_applicant_id = selected_id
                    st.success("Letter generated! See Letter Generator page.")

    st.markdown(
        '<div class="footer">WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — '
        'All rejections are final and binding under Swiss Civil Code Art. 271.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — APARTMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[2]:
    st.markdown('<div class="main-title">🏢 Apartments</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Our portfolio. Each unit is a small miracle.</div>', unsafe_allow_html=True)
    st.markdown("---")

    apartments = db.get_all_apartments()
    if not apartments:
        no_data_warning()
        st.stop()

    # ── Sidebar filters ────────────────────────────────────────────────────────
    st.sidebar.markdown("### Apartment Filters")

    all_kreise = sorted(list({a["kreis"] for a in apartments}))
    sel_kreise = st.sidebar.multiselect("Kreis", all_kreise, default=all_kreise)

    all_rooms = sorted(list({a["rooms"] for a in apartments}))
    sel_rooms = st.sidebar.multiselect("Rooms", all_rooms, default=all_rooms)

    rents = [a["rent_chf"] for a in apartments]
    rent_min, rent_max = st.sidebar.slider(
        "Rent range (CHF/month)",
        min_value=min(rents),
        max_value=max(rents),
        value=(min(rents), max(rents)),
    )

    avail_only = st.sidebar.checkbox("Available only", value=False)

    # Apply filters
    filtered_apts = apartments
    if sel_kreise:
        filtered_apts = [a for a in filtered_apts if a["kreis"] in sel_kreise]
    if sel_rooms:
        filtered_apts = [a for a in filtered_apts if a["rooms"] in sel_rooms]
    filtered_apts = [a for a in filtered_apts if rent_min <= a["rent_chf"] <= rent_max]
    if avail_only:
        filtered_apts = [a for a in filtered_apts if a["status"] == "available"]

    st.write(f"Showing **{len(filtered_apts)}** of {len(apartments)} apartments")

    if not filtered_apts:
        st.info("No apartments match the current filters.")
        st.stop()

    # ── Card grid ─────────────────────────────────────────────────────────────
    COLS = 3
    for row_start in range(0, len(filtered_apts), COLS):
        row_apts = filtered_apts[row_start: row_start + COLS]
        cols = st.columns(COLS)
        for col, apt in zip(cols, row_apts):
            with col:
                status_color = {
                    "available": "#d4edda",
                    "reserved": "#fff3cd",
                    "occupied": "#f8d7da",
                }.get(apt["status"], "#eee")

                balcony = "🌿 Balcony" if apt["has_balcony"] else ""
                pets = "🐾 Pet-friendly" if apt["pet_friendly"] else ""
                extras = "  ".join(filter(None, [balcony, pets])) or "No extras"

                st.markdown(
                    f"""
                    <div class="apt-card" style="border-top: 4px solid {'#28a745' if apt['status']=='available' else '#ffc107' if apt['status']=='reserved' else '#dc3545'}">
                        <div style="display:flex;align-items:center;margin-bottom:8px;">
                            <span class="kreis-chip">{apt['kreis']}</span>
                            <strong style="font-size:0.95rem">{apt['address']}</strong>
                        </div>
                        <div style="font-size:1.4rem;font-weight:800;color:#CC0000;">CHF {apt['rent_chf']:,}/mo</div>
                        <div style="color:#555;margin:4px 0;">{apt['rooms']} rooms &nbsp;·&nbsp; {apt['size_m2']} m²</div>
                        <div style="font-size:0.8rem;color:#777;margin-bottom:8px;">{extras}</div>
                        <span class="badge badge-{apt['status']}">{apt['status'].title()}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(f"Details & Match", key=f"apt_detail_{apt['id']}"):
                    st.session_state.selected_apartment_id = apt["id"]

    # ── Detail & Matching panel ────────────────────────────────────────────────
    if st.session_state.selected_apartment_id:
        apt_id = st.session_state.selected_apartment_id
        apt = db.get_apartment(apt_id)
        if apt:
            st.markdown("---")
            st.subheader(f"Detail: {apt['address']}")
            dc1, dc2 = st.columns(2)
            with dc1:
                st.markdown(f"**Address:** {apt['address']}, Zürich")
                st.markdown(f"**Kreis:** {apt['kreis']}")
                st.markdown(f"**Rooms:** {apt['rooms']}")
                st.markdown(f"**Size:** {apt['size_m2']} m²")
            with dc2:
                st.markdown(f"**Rent:** CHF {apt['rent_chf']:,}/month")
                st.markdown(f"**Balcony:** {'Yes' if apt['has_balcony'] else 'No'}")
                st.markdown(f"**Pet-friendly:** {'Yes' if apt['pet_friendly'] else 'No'}")
                st.markdown(
                    f"**Status:** {status_badge(apt['status'])}",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.subheader("Top 5 Eligible Applicants")
            st.caption("Eligibility: rent ≤ 1/3 of monthly income · sorted by score")

            if st.button("Run Matching Algorithm", type="primary", key="run_match"):
                all_applicants = db.get_all_applicants()
                monthly_income_threshold = apt["rent_chf"] * 3 * 12  # annual income needed
                eligible = [
                    a for a in all_applicants
                    if a["income_chf"] >= monthly_income_threshold
                    and a["status"] in ("pending", "under_review")
                ]
                eligible_sorted = sorted(eligible, key=lambda x: x["score"], reverse=True)[:5]

                if not eligible_sorted:
                    st.warning("No eligible applicants found for this apartment. Either everyone is too poor or too rejected.")
                else:
                    for i, a in enumerate(eligible_sorted, 1):
                        rank = sc.get_waitlist_rank(a["id"], all_applicants)
                        wait = sc.estimate_wait_years(rank)
                        with st.container():
                            mc1, mc2, mc3 = st.columns([3, 2, 2])
                            with mc1:
                                st.markdown(f"**#{i} {a['name']}**")
                                st.caption(a["email"])
                            with mc2:
                                st.markdown(f"Score: **{a['score']:.1f}**")
                                st.markdown(f"Income: CHF {a['income_chf']:,}/yr")
                            with mc3:
                                st.markdown(f"Rank: **#{rank}**")
                                st.markdown(f"Wait: **{wait} yrs**")
                            st.markdown("---")

    st.markdown(
        '<div class="footer">WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — '
        'All rejections are final and binding under Swiss Civil Code Art. 271.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — LETTER GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[3]:
    st.markdown('<div class="main-title">✉️ Letter Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">'
        'Crafting official correspondence with Swiss precision since 1987. '
        'Our rejections are works of art.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    applicants = db.get_all_applicants()
    apartments = db.get_all_apartments()

    if not applicants:
        no_data_warning()
        st.stop()

    col_form, col_preview = st.columns([1, 2])

    with col_form:
        st.subheader("Configure Letter")

        applicant_map = {a["id"]: f"{a['name']} ({a['status']})" for a in applicants}

        # Pre-select from session state (if navigated from Applicants page)
        default_idx = 0
        if st.session_state.selected_applicant_id in applicant_map:
            default_idx = list(applicant_map.keys()).index(
                st.session_state.selected_applicant_id
            )

        sel_app_id = st.selectbox(
            "Select Applicant",
            options=list(applicant_map.keys()),
            format_func=lambda x: applicant_map[x],
            index=default_idx,
            key="letter_applicant",
        )

        letter_type = st.radio(
            "Letter Type",
            ["Rejection (Standard)", "Rare Approval (Handle with Care)"],
            key="letter_type",
        )

        sel_apt_id = None
        if "Approval" in letter_type:
            apt_map = {
                a["id"]: f"{a['address']} (CHF {a['rent_chf']:,}/mo)"
                for a in apartments
                if a["status"] == "available"
            }
            if not apt_map:
                st.warning("No available apartments for approval letters. The irony is not lost on us.")
            else:
                sel_apt_id = st.selectbox(
                    "Select Apartment",
                    options=list(apt_map.keys()),
                    format_func=lambda x: apt_map[x],
                    key="letter_apartment",
                )

        st.markdown("---")

        if st.button("Generate Letter", type="primary", use_container_width=True):
            applicant = db.get_applicant(sel_app_id)
            all_applicants = db.get_all_applicants()
            rank = sc.get_waitlist_rank(sel_app_id, all_applicants)
            wait_years = sc.estimate_wait_years(rank if rank > 0 else 999)

            if "Rejection" in letter_type:
                letter = lg.generate_rejection_letter(
                    applicant_name=applicant["name"],
                    applicant_email=applicant["email"],
                    rank=rank if rank > 0 else 999,
                    wait_years=wait_years,
                )
            else:
                if not sel_apt_id:
                    st.error("Please select an available apartment.")
                    st.stop()
                apartment = db.get_apartment(sel_apt_id)
                letter = lg.generate_approval_letter(
                    applicant_name=applicant["name"],
                    applicant_email=applicant["email"],
                    apartment_address=apartment["address"],
                    apartment_kreis=apartment["kreis"],
                    rent_chf=apartment["rent_chf"],
                    zurisack_compliant=bool(applicant["zurisack_compliant"]),
                )

            st.session_state.generated_letter = letter
            st.success("Letter generated successfully.")

    with col_preview:
        st.subheader("Letter Preview")

        if st.session_state.generated_letter:
            st.markdown(
                f'<div class="letter-box">{st.session_state.generated_letter}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")
            # Copy to clipboard via text_area trick
            st.text_area(
                "Copy to clipboard (select all → Ctrl+C / Cmd+C)",
                value=st.session_state.generated_letter,
                height=120,
                key="letter_copy_area",
            )
        else:
            st.info("Configure and generate a letter using the form on the left.")
            st.markdown(
                """
                > *"The art of the rejection letter lies in making the recipient feel almost grateful
                > for the clarity of their misfortune."*
                > — Excerpt from the WohnTraum Zürich Staff Handbook, Chapter 7
                """
            )

    st.markdown(
        '<div class="footer">WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — '
        'All rejections are final and binding under Swiss Civil Code Art. 271.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — ADD APPLICANT
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGES[4]:
    st.markdown('<div class="main-title">➕ New Applicant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">'
        'Welcome to the queue. Please take a number. '
        'And then take a deep breath.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("new_applicant_form", clear_on_submit=True):
        st.subheader("Personal Information")
        fc1, fc2 = st.columns(2)
        with fc1:
            name = st.text_input("Full Name *", placeholder="e.g. Hans Müller")
            email = st.text_input("Email Address *", placeholder="hans.mueller@bluewin.ch")
            income_chf = st.number_input(
                "Annual Income (CHF) *",
                min_value=10_000,
                max_value=1_000_000,
                value=75_000,
                step=1_000,
                help="Gross annual income in Swiss Francs",
            )
            family_size = st.slider("Family Size", 1, 8, 2)

        with fc2:
            years_in_zurich = st.slider("Years Living in Zürich", 0, 50, 5)
            german_level = st.selectbox(
                "German Language Level",
                ["A1", "A2", "B1", "B2", "C1", "C2"],
                index=3,
                help="B2 and above scores bonus points",
            )
            registered_at = st.date_input(
                "Application Date",
                value=date.today(),
                max_value=date.today(),
            )
            zurisack_compliant = st.checkbox(
                "Züri-Sack Compliant ✓",
                value=True,
                help="I confirm that I use the official Züri-Sack for waste disposal. This is serious.",
            )

        st.markdown("---")
        submitted = st.form_submit_button(
            "Submit Application 🏔️",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip():
            st.error("Name is required.")
        elif not email.strip() or "@" not in email:
            st.error("A valid email address is required.")
        else:
            score = sc.compute_score(
                registered_at=registered_at,
                years_in_zurich=years_in_zurich,
                income_chf=income_chf,
                family_size=family_size,
                german_level=german_level,
                zurisack_compliant=zurisack_compliant,
            )

            new_id = db.insert_applicant({
                "name": name.strip(),
                "email": email.strip().lower(),
                "income_chf": income_chf,
                "family_size": family_size,
                "years_in_zurich": years_in_zurich,
                "german_level": german_level,
                "registered_at": registered_at.isoformat(),
                "status": "pending",
                "score": score,
                "zurisack_compliant": zurisack_compliant,
            })

            all_applicants = db.get_all_applicants()
            rank = sc.get_waitlist_rank(new_id, all_applicants)
            wait_years = sc.estimate_wait_years(rank)
            wait_msg = sc.sarcastic_wait_message(wait_years)

            st.balloons()

            st.success(f"Application submitted successfully! Welcome to the queue, {name.split()[0]}.")

            st.markdown("---")
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("Your Score", f"{score:.2f} pts")
            with rc2:
                st.metric("Waitlist Rank", f"#{rank}")
            with rc3:
                st.metric("Estimated Wait", f"{wait_years} years")

            st.info(f"⏳ {wait_msg}")

            if not zurisack_compliant:
                st.warning(
                    "⚠️ You have not confirmed Züri-Sack compliance. "
                    "This has been noted. It will be mentioned at every subsequent interaction."
                )

            st.markdown(
                f"""
                ---
                **Reference Number:** WT-{new_id:05d}-{registered_at.year}

                Please keep this reference number for your records.
                You will need it in approximately {wait_years} years.
                """
            )

    st.markdown(
        '<div class="footer">WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — '
        'All rejections are final and binding under Swiss Civil Code Art. 271.</div>',
        unsafe_allow_html=True,
    )
