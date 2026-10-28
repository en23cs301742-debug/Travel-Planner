import { FormEvent, useState } from "react";
import {
  ArrowRight,
  Check,
  Clock3,
  Coffee,
  Compass,
  Copy,
  LoaderCircle,
  MapPin,
  Moon,
  Sparkles,
  Sun,
  Wallet,
} from "lucide-react";

type Activity = { title: string; location: string; description: string };
type DayPlan = { day: number; morning: Activity; afternoon: Activity; evening: Activity };
type Itinerary = { trip_summary: string; daily_plan: DayPlan[]; budget_tips: string[] };

const interests = ["Culture", "Food", "Adventure", "Shopping", "Relaxation"];
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState(4);
  const [budget, setBudget] = useState("Moderate");
  const [selectedInterests, setSelectedInterests] = useState<string[]>(["Culture", "Food"]);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const toggleInterest = (interest: string) => {
    setSelectedInterests((current) =>
      current.includes(interest) ? current.filter((item) => item !== interest) : [...current, interest],
    );
  };

  const generateItinerary = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setCopied(false);
    try {
      const response = await fetch(`${API_URL}/api/generate-itinerary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination, days, budget, interests: selectedInterests }),
      });
      if (!response.ok) throw new Error("The planner could not create your itinerary.");
      setItinerary((await response.json()) as Itinerary);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyItinerary = async () => {
    if (!itinerary) return;
    const text = `${destination} itinerary\n\n${itinerary.trip_summary}\n\n${itinerary.daily_plan
      .map((day) => `Day ${day.day}\nMorning: ${day.morning.title} — ${day.morning.description}\nAfternoon: ${day.afternoon.title} — ${day.afternoon.description}\nEvening: ${day.evening.title} — ${day.evening.description}`)
      .join("\n\n")}\n\nBudget tips:\n${itinerary.budget_tips.map((tip) => `• ${tip}`).join("\n")}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2200);
  };

  return (
    <main>
      <section className="hero">
        <nav className="nav"><a className="brand" href="/"><Compass size={22} /> Roamly</a><span className="nav-note">Travel, thoughtfully planned.</span></nav>
        <div className="hero-content">
          <div className="eyebrow"><Sparkles size={16} /> Your next story starts here</div>
          <h1>Personalized <em>AI</em><br />Travel Planner</h1>
          <p>Turn your travel dreams into a day-by-day adventure, tailored to your pace, interests, and budget.</p>
        </div>
        <div className="hero-shape shape-one" /><div className="hero-shape shape-two" />
      </section>

      <section className="workspace">
        <form className="planner-card" onSubmit={generateItinerary}>
          <div className="section-heading"><span className="step">01</span><div><h2>Tell us about your trip</h2><p>A few details are all we need to get started.</p></div></div>
          <label>Where are you going?<div className="input-wrap"><MapPin size={19} /><input required value={destination} onChange={(event) => setDestination(event.target.value)} placeholder="e.g. Kyoto, Japan" /></div></label>
          <div className="form-grid">
            <label>How long?<div className="input-wrap"><Clock3 size={19} /><input required type="number" min="1" max="14" value={days} onChange={(event) => setDays(Number(event.target.value))} /><span className="suffix">days</span></div></label>
            <label>Travel style<select value={budget} onChange={(event) => setBudget(event.target.value)}><option>Budget</option><option>Moderate</option><option>Luxury</option></select></label>
          </div>
          <fieldset><legend>What are you into?</legend><div className="interest-list">{interests.map((interest) => <button type="button" className={`interest ${selectedInterests.includes(interest) ? "selected" : ""}`} onClick={() => toggleInterest(interest)} key={interest}>{selectedInterests.includes(interest) && <Check size={15} />}{interest}</button>)}</div></fieldset>
          <button className="primary-button" disabled={loading} type="submit">{loading ? <><LoaderCircle className="spin" size={19} /> Crafting your trip...</> : <>Generate itinerary <ArrowRight size={19} /></>}</button>
          {error && <p className="error">{error}</p>}
        </form>

        <div className="results">
          {!itinerary && <div className="empty-state"><div className="empty-icon"><Compass size={33} /></div><h2>Your adventure awaits</h2><p>Fill in your trip details and we’ll map out something wonderful.</p></div>}
          {itinerary && <><div className="results-header"><div><div className="eyebrow">Your itinerary is ready</div><h2>{destination} <span>·</span> {days} days</h2></div><button className="copy-button" onClick={copyItinerary} type="button">{copied ? <Check size={17} /> : <Copy size={17} />}{copied ? "Copied" : "Copy plan"}</button></div><div className="summary-card"><div className="summary-icon"><Sparkles size={20} /></div><div><h3>The big picture</h3><p>{itinerary.trip_summary}</p></div></div><div className="days">{itinerary.daily_plan.map((day) => <DayCard key={day.day} plan={day} />)}</div><div className="tips-card"><div className="tips-title"><Wallet size={19} /><h3>Smart ways to spend less</h3></div><ul>{itinerary.budget_tips.map((tip) => <li key={tip}>{tip}</li>)}</ul></div></>}
        </div>
      </section>
      <footer>Built for curious travelers <span>✦</span> Have a beautiful journey.</footer>
    </main>
  );
}

function DayCard({ plan }: { plan: DayPlan }) {
  const slots = [{ label: "Morning", icon: <Sun size={18} />, activity: plan.morning }, { label: "Afternoon", icon: <Coffee size={18} />, activity: plan.afternoon }, { label: "Evening", icon: <Moon size={18} />, activity: plan.evening }];
  return <article className="day-card"><div className="day-label">DAY {String(plan.day).padStart(2, "0")}</div><div className="activities">{slots.map((slot) => <div className="activity" key={slot.label}><div className="activity-icon">{slot.icon}</div><div><span className="activity-time">{slot.label}</span><h3>{slot.activity.title}</h3><p className="location"><MapPin size={13} /> {slot.activity.location}</p><p>{slot.activity.description}</p></div></div>)}</div></article>;
}

export default App;

