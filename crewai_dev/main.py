import os
from crew import GraduallyAICrew  # ✅ Import the CrewAI setup
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing. Set it in your .env file.")

# ✅ Define the correct paths to backend/api.py and backend/models.py
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Move up one level from `crewai_dev`
API_FILE_PATH = os.path.join(BASE_DIR, "backend", "api.py")  # Target backend/api.py
MODELS_FILE_PATH = os.path.join(BASE_DIR, "backend", "models.py")  # Target backend/models.py

def run():
    """
    Run the CrewAI process, collecting recommendations from each agent and appending them to backend/api.py.
    """
    try:
        # ✅ Read the database structure from models.py
        if os.path.exists(MODELS_FILE_PATH):
            with open(MODELS_FILE_PATH, "r", encoding="utf-8") as models_file:
                models_content = models_file.read()
        else:
            models_content = "No models.py file found."

        # ✅ Initialize CrewAI
        crew_instance = GraduallyAICrew()
        crew = crew_instance.crew()
        result = crew.kickoff()  # ✅ Run the CrewAI process

        if not result:
            raise ValueError("❌ CrewAI did not generate any output.")

        # ✅ Convert CrewOutput to a string
        generated_code = result.raw_output if hasattr(result, "raw_output") else str(result)

        # ✅ Separate output by agent to append each recommendation clearly
        agent_outputs = generated_code.split("\n\n")  # Split output by double line break

        # ✅ Ensure backend/api.py exists before writing
        if not os.path.exists(API_FILE_PATH):
            raise FileNotFoundError(f"❌ The file {API_FILE_PATH} does not exist. Ensure the backend folder and api.py are set up correctly.")

        print(f"📌 Writing AI-generated improvements to {API_FILE_PATH}...")

        with open(API_FILE_PATH, "a", encoding="utf-8") as api_file:
            api_file.write("\n\n# ✅ CrewAI-Generated Improvements\n")
            for idx, agent_output in enumerate(agent_outputs, start=1):
                api_file.write(f"\n\n# 🔹 Recommendation from Agent {idx}\n")
                api_file.write(agent_output)

        print("\n🔥 AI-Generated FastAPI Code Successfully Written to `backend/api.py`! 🚀")

    except Exception as e:
        print(f"❌ Error running CrewAI: {e}")

if __name__ == "__main__":
    run()
