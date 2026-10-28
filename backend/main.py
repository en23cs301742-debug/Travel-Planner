import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Personalized Travel Itinerary Planner", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ItineraryRequest(BaseModel):
    destination: str = Field(..., min_length=2, max_length=100)
    days: int = Field(..., ge=1, le=14)
    budget: str = Field(..., min_length=1, max_length=20)
    interests: List[str] = Field(default_factory=list, max_length=5)


class Activity(BaseModel):
    title: str
    location: str
    description: str


class DailyPlan(BaseModel):
    day: int
    morning: Activity
    afternoon: Activity
    evening: Activity


class ItineraryResponse(BaseModel):
    trip_summary: str
    daily_plan: List[DailyPlan]
    budget_tips: List[str]


def activity(title: str, location: str, description: str) -> Activity:
    return Activity(title=title, location=location, description=description)


def generate_fallback(request: ItineraryRequest) -> ItineraryResponse:
    destination = request.destination.strip()
    interests = request.interests or ["Culture", "Food"]
    interest_text = ", ".join(interests[:-1]) + (
        f" and {interests[-1]}" if len(interests) > 1 else interests[0]
    )
    templates = [
        (
            activity("Start with a local breakfast", f"{destination} neighborhood café", "Ease into the day with a regional specialty and a short walk."),
            activity(f"Explore {destination}'s highlights", "Historic center and landmark district", f"Follow a flexible route shaped around {interest_text.lower()}."),
            activity("Dinner with a local perspective", "Recommended neighborhood restaurant", "Choose a well-reviewed local table, then enjoy an easy evening stroll."),
        ),
        (
            activity("Sunrise viewpoint and coffee", "A scenic city viewpoint", "Take in the city before the crowds arrive and make time for a slow coffee."),
            activity("Meet makers and local stories", "Market, museum, or creative quarter", "Browse independently, ask locals for recommendations, and keep the afternoon unhurried."),
            activity("Golden-hour experience", "Waterfront, plaza, or garden", "Wind down with a memorable sunset and a relaxed dinner nearby."),
        ),
        (
            activity("Neighborhood walk", "A residential or riverside district", "See everyday life beyond the main attractions with a self-guided walk."),
            activity("Choose-your-own adventure", "A day-trip or activity hub", f"Pick an experience aligned with your {interest_text.lower()} interests."),
            activity("Local flavors and live culture", "A lively dining district", "Sample a few small plates or find a low-key performance for your final outing."),
        ),
    ]
    daily_plan = []
    for index in range(request.days):
        morning, afternoon, evening = templates[index % len(templates)]
        daily_plan.append(
            DailyPlan(
                day=index + 1,
                morning=morning,
                afternoon=afternoon,
                evening=evening,
            )
        )
    tips_by_budget = {
        "Budget": [
            "Use public transit and walk between nearby neighborhoods.",
            "Book popular attractions online early and look for free museum days.",
            "Eat where locals eat: markets and lunch specials usually offer the best value.",
        ],
        "Luxury": [
            "Reserve signature restaurants and private experiences before arrival.",
            "Cluster premium activities together to reduce transfer time and cost.",
            "Ask hotels about member perks, airport transfers, and room upgrades.",
        ],
        "Moderate": [
            "Mix one memorable paid experience with free neighborhood exploration each day.",
            "Stay near a transit hub to save time and reduce ride-hailing costs.",
            "Plan a flexible lunch and reserve your budget for one excellent dinner.",
        ],
    }
    return ItineraryResponse(
        trip_summary=(
            f"A {request.days}-day {request.budget.lower()} trip to {destination} "
            f"with a focus on {interest_text.lower()}. This balanced plan leaves room "
            "for spontaneous discoveries while covering the destination's essential character."
        ),
        daily_plan=daily_plan,
        budget_tips=tips_by_budget.get(request.budget, tips_by_budget["Moderate"]),
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/generate-itinerary", response_model=ItineraryResponse)
def generate_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    # The deterministic planner is always available; an external AI provider can
    # be introduced later without making local development depend on an API key.
    return generate_fallback(request)

