import os
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
import openai

# OpenAI API Key
OPENAI_API_KEY = "openai_api_key"
openai.api_key = OPENAI_API_KEY

# personas using TinyTroupe
def create_tech_savvy_user():
    user = TinyPerson("Alex")
    user.define("age", 30)
    user.define("occupation", "Software Developer")
    user.define("interests", ["technology", "gadgets", "programming"])
    user.define("personality", "early adopter, analytical")
    user.define("goals", ["stay updated with tech trends", "optimize workflows"])
    return user

def create_budget_conscious_buyer():
    user = TinyPerson("Jamie")
    user.define("age", 45)
    user.define("occupation", "Teacher")
    user.define("interests", ["education", "budgeting", "family activities"])
    user.define("personality", "practical, value-oriented")
    user.define("goals", ["find cost-effective solutions", "ensure product reliability"])
    return user

def create_casual_consumer():
    user = TinyPerson("Taylor")
    user.define("age", 35)
    user.define("occupation", "Marketing Specialist")
    user.define("interests", ["trends", "social media", "entertainment"])
    user.define("personality", "impulsive, trend-follower")
    user.define("goals", ["stay trendy", "share experiences"])
    return user

# Initialization
tech_savvy_user = create_tech_savvy_user()
budget_conscious_buyer = create_budget_conscious_buyer()
casual_consumer = create_casual_consumer()

# Create a TinyWorld environment
world = TinyWorld("Product Feedback Session", [tech_savvy_user, budget_conscious_buyer, casual_consumer])
world.make_everyone_accessible()

def simulate_feedback(feature_description):
    
    # Prompt each persona with the feature description
    tech_savvy_user.listen(f"Please provide your thoughts on the following product feature: {feature_description}")
    budget_conscious_buyer.listen(f"Please share your feedback on this product feature: {feature_description}")
    casual_consumer.listen(f"What are your impressions of this product feature: {feature_description}")

    # simulating
    world.run(3)

    # display feedback from each persona
    print("\n--- Persona Feedback ---\n")
    print("Tech-Savvy User Feedback:")
    print(tech_savvy_user.pp_current_interactions())

    print("\nBudget-Conscious Buyer Feedback:")
    print(budget_conscious_buyer.pp_current_interactions())

    print("\nCasual Consumer Feedback:")
    print(casual_consumer.pp_current_interactions())

if __name__ == "__main__":
    # feature description
    feature_desc = input("Enter product feature description: ")
    simulate_feedback(feature_desc)
