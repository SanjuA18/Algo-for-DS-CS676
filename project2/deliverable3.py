import streamlit as st
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
import openai
import io
import sys
import json
import base64
import uuid
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")
openai.api_key = OPENAI_API_KEY
SAVED_PERSONAS_FILE = "personas.json"
SAVED_CONVERSATIONS_FILE = "conversations.json"

# Enhanced Persona Class
class EnhancedPersona(TinyPerson):
    def __init__(self, name, **traits):
        super().__init__(name)
        self.avatar = "👤"  # Default avatar
        self.conversation_history = []
        for key, value in traits.items():
            self.define(key, value)
    
    def add_to_history(self, speaker, message):
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message
        })

# Simulation Manager
class SimulationManager:
    @staticmethod
    def run_feedback_session(feature_description: str, personas: List[EnhancedPersona], rounds: int = 3) -> Dict:
        world = TinyWorld("Product Feedback Session", personas)
        world.make_everyone_accessible()

        for persona in personas:
            prompt = f"Please provide your honest thoughts on: {feature_description}. Consider your traits: {persona.traits}"
            persona.listen(prompt)
            persona.add_to_history("System", prompt)

        world.run(rounds)

        feedback = {}
        for persona in personas:
            captured_output = io.StringIO()
            sys.stdout = captured_output
            persona.pp_current_interactions()
            sys.stdout = sys.__stdout__
            feedback[persona.name] = captured_output.getvalue()
            persona.add_to_history(persona.name, feedback[persona.name])
        
        return feedback

    @staticmethod
    def run_live_conversation(personas: List[EnhancedPersona], user_input: str) -> Dict:
        world = TinyWorld("Live Conversation", personas)
        world.make_everyone_accessible()

        # Add user input to all personas
        for persona in personas:
            persona.listen(f"User says: {user_input}")
            persona.add_to_history("User", user_input)

        # Run 1 round of conversation
        world.run(1)

        responses = {}
        for persona in personas:
            captured_output = io.StringIO()
            sys.stdout = captured_output
            persona.pp_current_interactions()
            sys.stdout = sys.__stdout__
            responses[persona.name] = captured_output.getvalue()
            persona.add_to_history(persona.name, responses[persona.name])
        
        return responses

# Data Persistence
def save_data(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

# UI Components
def persona_card(persona):
    traits = persona.traits
    with st.expander(f"{persona.avatar} {persona.name}"):
        cols = st.columns(2)
        cols[0].metric("Age", traits.get("age", "N/A"))
        cols[1].metric("Occupation", traits.get("occupation", "N/A"))
        
        st.caption("Personality")
        st.write(", ".join(traits.get("personality", [])))
        
        st.caption("Interests")
        st.write(", ".join(traits.get("interests", [])))
        
        st.caption("Goals")
        st.write(", ".join(traits.get("goals", [])))

# App Pages
def feedback_simulator_page():
    st.header("📊 Feedback Simulation")
    
    feature_desc = st.text_area("Product Feature Description", 
                               "A new mobile app feature that uses AI to...")
    
    if st.button("Run Simulation", help="Simulate feedback from all active personas"):
        if not st.session_state.personas:
            st.warning("Please add at least one persona")
        else:
            with st.spinner("Simulating feedback sessions..."):
                feedback = SimulationManager.run_feedback_session(
                    feature_desc, 
                    st.session_state.personas
                )
            
            st.header("Results")
            for name, response in feedback.items():
                with st.expander(f"Response from {name}"):
                    st.write(response)

def live_conversation_page():
    st.header("💬 Live Conversation")
    
    if not st.session_state.personas:
        st.warning("Please add personas first")
        return
    
    # Initialize conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    # Display conversation history
    for msg in st.session_state.conversation:
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            cols = st.columns([1, 4])
            cols[0].write(f"{msg['name']}:")
            cols[1].write(msg['content'])
    
    # User input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.conversation.append({
            'role': 'user',
            'content': prompt
        })
        
        with st.spinner("Getting responses..."):
            responses = SimulationManager.run_live_conversation(
                st.session_state.personas,
                prompt
            )
        
        for name, response in responses.items():
            st.session_state.conversation.append({
                'role': 'agent',
                'name': name,
                'content': response
            })
        
        st.experimental_rerun()

def persona_management_page():
    st.header("👥 Persona Management")
    
    # Create/Edit Persona
    with st.form("persona_form"):
        cols = st.columns(2)
        name = cols[0].text_input("Name", key="persona_name")
        age = cols[1].number_input("Age", min_value=1, max_value=120, value=30)
        
        occupation = st.text_input("Occupation")
        interests = st.text_input("Interests (comma separated)", "technology, sports")
        personality = st.text_input("Personality Traits (comma separated)", "curious, analytical")
        goals = st.text_input("Goals (comma separated)", "learn new things, help others")
        avatar = st.selectbox("Avatar", ["👤", "👨", "👩", "🧑", "👨‍💻", "👩‍🔬", "🤖"])
        
        submitted = st.form_submit_button("Save Persona")
        if submitted:
            try:
                persona = EnhancedPersona(
                    name,
                    age=age,
                    occupation=occupation,
                    interests=[i.strip() for i in interests.split(",")],
                    personality=[p.strip() for p in personality.split(",")],
                    goals=[g.strip() for g in goals.split(",")]
                )
                persona.avatar = avatar
                
                if 'personas' not in st.session_state:
                    st.session_state.personas = []
                
                st.session_state.personas.append(persona)
                save_data([p.__dict__ for p in st.session_state.personas], SAVED_PERSONAS_FILE)
                st.success(f"Persona {name} saved!")
            except Exception as e:
                st.error(f"Error creating persona: {e}")
    
    # Persona List
    st.subheader("Current Personas")
    if not st.session_state.get('personas', []):
        st.info("No personas created yet")
    else:
        for persona in st.session_state.personas:
            persona_card(persona)
            if st.button(f"Delete {persona.name}", key=f"del_{persona.name}"):
                st.session_state.personas = [p for p in st.session_state.personas if p.name != persona.name]
                save_data([p.__dict__ for p in st.session_state.personas], SAVED_PERSONAS_FILE)
                st.experimental_rerun()

# Main App
def main():
    st.set_page_config(page_title="Agentic AI Simulator", layout="wide")
    
    # Initialize session state
    if 'personas' not in st.session_state:
        st.session_state.personas = []
        saved = load_data(SAVED_PERSONAS_FILE)
        for p in saved:
            persona = EnhancedPersona(p['name'])
            for key, value in p.items():
                if key != 'name':
                    setattr(persona, key, value)
            st.session_state.personas.append(persona)
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Feedback Simulator", "Live Conversation", "Persona Management"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("Quick Actions")
    if st.sidebar.button("Load Sample Personas"):
        sample_personas = [
            EnhancedPersona("Alex", age=30, occupation="Developer", 
                           interests=["AI", "coding"], 
                           personality=["technical", "analytical"],
                           goals=["build cool apps"]),
            EnhancedPersona("Sam", age=45, occupation="Manager", 
                           interests=["leadership", "psychology"], 
                           personality=["empathetic", "strategic"],
                           goals=["build effective teams"])
        ]
        st.session_state.personas.extend(sample_personas)
        st.sidebar.success("Added sample personas!")
    
    if st.sidebar.button("Clear All Data"):
        st.session_state.personas = []
        save_data([], SAVED_PERSONAS_FILE)
        save_data([], SAVED_CONVERSATIONS_FILE)
        st.sidebar.warning("All data cleared")
    
    # Page routing
    if page == "Feedback Simulator":
        feedback_simulator_page()
    elif page == "Live Conversation":
        live_conversation_page()
    elif page == "Persona Management":
        persona_management_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Agentic AI Simulator v1.0")

if __name__ == "__main__":
    main()