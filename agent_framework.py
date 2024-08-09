from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

# Technical Director (Operations Overseer)
technical_director = Agent(
    role='',
    goal='',
    verbose=True,
    memory=True,
    backstory=(
        ""
    ),
    tools=[search_tool]
)

# Vulnerability Researcher (GapScanner)
vulnerability_researcher = Agent(
    role='',
    goal='',
    verbose=True,
    memory=True,
    backstory=(
        ""
    ),
    tools=[search_tool]
)

# Network Penetration Tester (InfilTrace)
network_penetration_tester = Agent(
    role='',
    goal='',
    verbose=True,
    memory=True,
    backstory=(
        ""

    ),
    tools=[search_tool]
)
