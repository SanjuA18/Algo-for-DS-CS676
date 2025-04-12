import streamlit as st
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
import openai
import io
import sys
import json
import base64
from typing import List

# OpenAI API Key
OPENAI_API_KEY = "openai_api_key"
openai.api_key = OPENAI_API_KEY

# saved personas and feedback
SAVED_PERSONAS_FILE = "personas.json"


def create_persona(name, age, occupation, interests, personality, goals):
    user = TinyPerson(name)
    user.define("age", int(age))
    user.define("occupation", occupation)
    user.define("interests", interests.split(", "))
    user.define("personality", personality.split(", "))
    user.define("goals", goals.split(", "))
    return user

def simulate_feedback(feature_description, personas):
    world = TinyWorld("Product Feedback Session", personas)
    world.make_everyone_accessible()

    for persona in personas:
        persona.listen(f"Please provide your thoughts on the following product feature: {feature_description}")

    world.run(3)

    feedback = {}
    for persona in personas:
        captured_output = io.StringIO()
        sys.stdout = captured_output
        persona.pp_current_interactions()
        sys.stdout = sys.__stdout__
        feedback[persona.name] = captured_output.getvalue()
    return feedback

def save_personas(personas):
    data = []
    for p in personas:
        data.append({
            "name": p.name,
            "age": p.traits["age"],
            "occupation": p.traits["occupation"],
            "interests": ", ".join(p.traits["interests"]),
            "personality": ", ".join(p.traits["personality"]),
            "goals": ", ".join(p.traits["goals"]),
        })
    with open(SAVED_PERSONAS_FILE, "w") as f:
        json.dump(data, f)

def load_saved_personas():
    try:
        with open(SAVED_PERSONAS_FILE, "r") as f:
            data = json.load(f)
            return [create_persona(**p) for p in data]
    except FileNotFoundError:
        return []

def get_text_download_link(text, filename, label):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    return href

def predefined_personas():
    return [
        create_persona("Alex", 30, "Software Developer", "technology, gadgets, programming", "early adopter, analytical", "stay updated with tech trends, optimize workflows"),
        create_persona("Jamie", 45, "Teacher", "education, budgeting, family activities", "practical, value-oriented", "find cost-effective solutions, ensure product reliability"),
        create_persona("Taylor", 35, "Marketing Specialist", "trends, social media, entertainment", "impulsive, trend-follower", "stay trendy, share experiences")
    ]

# ---------- Streamlit UI ----------
def main():
    st.title("Persona Feedback Simulator")

    if 'personas' not in st.session_state:
        st.session_state.personas = []

    st.sidebar.title("Persona Options")
    if st.sidebar.button("Load Saved Personas"):
        st.session_state.personas = load_saved_personas()
        st.sidebar.success("Saved personas loaded!")

    if st.sidebar.button("Add Predefined Personas"):
        st.session_state.personas.extend(predefined_personas())
        st.sidebar.success("Predefined personas added!")

    if st.sidebar.button("Clear All Personas"):
        st.session_state.personas = []
        st.sidebar.warning("Personas cleared.")

    st.sidebar.markdown("---")
    if st.sidebar.button("Save Current Personas"):
        save_personas(st.session_state.personas)
        st.sidebar.success("Personas saved.")

    num_personas = st.number_input("Number of New Personas to Add", min_value=1, value=1, step=1)

    for i in range(num_personas):
        st.header(f"Add Persona {i + 1}")
        name = st.text_input("Name", key=f"name_{i}")
        age = st.text_input("Age", key=f"age_{i}")
        occupation = st.text_input("Occupation", key=f"occupation_{i}")
        interests = st.text_input("Interests (comma-separated)", key=f"interests_{i}")
        personality = st.text_input("Personality Traits (comma-separated)", key=f"personality_{i}")
        goals = st.text_input("Goals (comma-separated)", key=f"goals_{i}")

        if st.button("Add Persona", key=f"add_{i}"):
            if name and age and occupation and interests and personality and goals:
                st.session_state.personas.append(create_persona(name, age, occupation, interests, personality, goals))
                st.success(f"Persona '{name}' added successfully!")
            else:
                st.warning("Please fill in all fields for the persona.")

    feature_desc = st.text_area("Enter Product Feature Description")

    if st.button("Simulate Feedback"):
        if not st.session_state.personas:
            st.warning("Please add at least one persona.")
        elif not feature_desc.strip():
            st.warning("Please enter a product feature description.")
        else:
            feedback = simulate_feedback(feature_desc, st.session_state.personas)
            st.header("Feedback Results")
            combined_feedback = ""
            for name, fb in feedback.items():
                st.subheader(name)
                st.text(fb)
                combined_feedback += f"--- {name} ---\n{fb}\n"

            st.markdown(get_text_download_link(combined_feedback, "feedback_report.txt", "📥 Download Full Feedback Report"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
