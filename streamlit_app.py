import streamlit as st

from backend.main import ItineraryRequest, generate_fallback

st.set_page_config(
    page_title="Personalized AI Travel Planner",
    page_icon="✈️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #f7f8f3; color: #23352e; }
    .hero { background: #173c34; border-radius: 0 0 24px 24px; color: #f7f8f3;
            margin: -4rem -4rem 2rem; padding: 4rem max(2rem, calc((100% - 1100px) / 2)) 3rem; }
    .hero h1 { font-family: Georgia, serif; font-size: clamp(2.6rem, 6vw, 5rem);
               line-height: .98; margin: 1rem 0; }
    .hero em { color: #e7b66b; }
    .hero p { color: #c1d3c9; font-size: 1.1rem; max-width: 500px; }
    .eyebrow { color: #d3a762; font-size: .75rem; font-weight: 700;
               letter-spacing: .14rem; text-transform: uppercase; }
    .card { background: white; border: 1px solid #e6e9e1; border-radius: 14px;
            box-shadow: 0 12px 30px #173c3411; margin: 1rem 0; padding: 1.2rem; }
    .activity { border-left: 3px solid #d3a762; margin: .7rem 0; padding: .2rem .8rem; }
    .activity small { color: #54826e; font-weight: 700; text-transform: uppercase; }
    .activity p { color: #66776d; margin: .25rem 0 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="eyebrow">✦ Your next story starts here</div>'
    "<h1>Personalized <em>AI</em><br>Travel Planner</h1>"
    "<p>Turn your travel dreams into a day-by-day adventure, tailored to your pace, interests, and budget.</p></div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Tell us about your trip")
    destination = st.text_input("Where are you going?", placeholder="e.g. Kyoto, Japan")
    days = st.number_input("How long?", min_value=1, max_value=14, value=4, step=1)
    budget = st.selectbox("Travel style", ["Budget", "Moderate", "Luxury"])
    selected_interests = st.multiselect(
        "What are you into?",
        ["Culture", "Food", "Adventure", "Shopping", "Relaxation"],
        default=["Culture", "Food"],
    )
    generate = st.button("Generate itinerary  →", type="primary", use_container_width=True)

if generate:
    if not destination.strip():
        st.error("Please enter a destination.")
    else:
        request = ItineraryRequest(
            destination=destination,
            days=int(days),
            budget=budget,
            interests=selected_interests,
        )
        st.session_state["itinerary"] = generate_fallback(request)
        st.session_state["destination"] = destination

itinerary = st.session_state.get("itinerary")
if itinerary is None:
    st.info("Fill in your trip details in the sidebar and generate your personalized itinerary.")
else:
    destination = st.session_state["destination"]
    header_col, copy_col = st.columns([4, 1])
    with header_col:
        st.markdown('<div class="eyebrow">Your itinerary is ready</div>', unsafe_allow_html=True)
        st.title(f"{destination} · {len(itinerary.daily_plan)} days")
    with copy_col:
        st.download_button(
            "Download plan",
            data=f"{destination}\n\n{itinerary.trip_summary}\n\n"
            + "\n\n".join(
                f"Day {day.day}\n"
                f"Morning: {day.morning.title} — {day.morning.description}\n"
                f"Afternoon: {day.afternoon.title} — {day.afternoon.description}\n"
                f"Evening: {day.evening.title} — {day.evening.description}"
                for day in itinerary.daily_plan
            ),
            file_name="travel-itinerary.txt",
            mime="text/plain",
        )

    st.markdown(
        f'<div class="card"><div class="eyebrow">The big picture</div>'
        f"<p>{itinerary.trip_summary}</p></div>",
        unsafe_allow_html=True,
    )
    for day in itinerary.daily_plan:
        with st.container():
            st.markdown(f'<div class="card"><h3>DAY {day.day:02d}</h3>', unsafe_allow_html=True)
            columns = st.columns(3)
            for column, label, activity in zip(
                columns,
                ["Morning", "Afternoon", "Evening"],
                [day.morning, day.afternoon, day.evening],
            ):
                with column:
                    st.markdown(
                        f'<div class="activity"><small>{label}</small>'
                        f"<strong>{activity.title}</strong><br>"
                        f"<span>📍 {activity.location}</span>"
                        f"<p>{activity.description}</p></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>💰 Smart ways to spend less</h3>', unsafe_allow_html=True)
    for tip in itinerary.budget_tips:
        st.markdown(f"- {tip}")
    st.markdown("</div>", unsafe_allow_html=True)
