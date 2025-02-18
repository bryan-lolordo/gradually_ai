import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

@CrewBase
class GraduallyAICrew:
    """Gradually AI crew for optimizing and enhancing FastAPI endpoints"""

    # ✅ Agents & Tasks YAML Configuration Paths
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ✅ Define Agents
    @agent
    def code_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["code_analyzer"], verbose=True)

    @agent
    def optimization_engineer(self) -> Agent:
        return Agent(config=self.agents_config["optimization_engineer"], verbose=True)

    @agent
    def habit_analyst(self) -> Agent:
        return Agent(config=self.agents_config["habit_analyst"], verbose=True)

    @agent
    def security_agent(self) -> Agent:
        return Agent(config=self.agents_config["security_agent"], verbose=True)

    @agent
    def api_extender(self) -> Agent:
        return Agent(config=self.agents_config["api_extender"], verbose=True)

    # ✅ Define Tasks
    @task
    def extract_api_endpoints(self) -> Task:
        return Task(config=self.tasks_config["extract_api_endpoints"])

    @task
    def optimize_endpoints(self) -> Task:
        return Task(config=self.tasks_config["optimize_endpoints"])

    @task
    def analyze_habit_ai(self) -> Task:
        return Task(config=self.tasks_config["analyze_habit_ai"])

    @task
    def enhance_security(self) -> Task:
        return Task(config=self.tasks_config["enhance_security"])

    @task
    def add_new_endpoints(self) -> Task:
        return Task(config=self.tasks_config["add_new_endpoints"])

    # ✅ Crew Execution
    @crew
    def crew(self) -> Crew:
        """Creates and runs the Gradually AI crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,  # Runs in order: Analyze → Optimize → Secure → Extend API
            verbose=True,
        )
