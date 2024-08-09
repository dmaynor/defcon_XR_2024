import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Set environment variables for the tools (replace with your actual API keys)
os.environ["SERPER_API_KEY"] = "Your Serper API Key"
os.environ["OPENAI_API_KEY"] = "Your OpenAI API Key"

# Initialize the SerperDevTool for web search
search_tool = SerperDevTool()

# Define the operator agent
operator = Agent(
    role='Network and Host Information Collector',
    goal='Execute commands to gather network and host information for a digital twin',
    verbose=True,
    memory=True,
    backstory=(
        "You are skilled in using various command-line tools to collect network and host information efficiently."
    ),
    tools=[search_tool]
)

# Define the technical director agent
technical_director = Agent(
    role='Technical Director and Human Proxy',
    goal='Serve as the team leader and decompose complex tasks for delegation',
    verbose=True,
    memory=True,
    backstory=(
        "You have expertise in leading technical projects and are proficient in breaking down complex tasks for efficient execution."
    ),
    tools=[search_tool],
    human_in_the_loop=True
)

# Define the docker expert agent
docker_expert = Agent(
    role='Docker Network Recreator',
    goal='Recreate the target network in Docker using the collected data',
    verbose=True,
    memory=True,
    backstory=(
        "You have extensive experience in using Docker to create and manage containerized networks."
    ),
    tools=[search_tool]
)

# Define the critic agent
critic = Agent(
    role='Task Critic',
    goal='Review and provide feedback on the tasks to ensure accuracy and efficiency',
    verbose=True,
    memory=True,
    backstory=(
        "You have a keen eye for detail and are proficient in analyzing tasks to improve their execution."
    ),
    tools=[search_tool]
)

# Define the task for collecting network information
collect_network_info = Task(
    description=(
        "Execute commands to gather network and host information."
        " Use tools like `ifconfig`, `netstat`, and `hostname` to collect the necessary data."
    ),
    expected_output='A detailed report containing the network configuration and host information.',
    tools=[search_tool],
    agent=operator,
)

# Define the task for decomposing tasks
decompose_tasks = Task(
    description=(
        "Decompose the complex task of recreating the network in Docker into smaller, manageable tasks and delegate them accordingly."
    ),
    expected_output='A set of clearly defined tasks for recreating the network in Docker.',
    tools=[search_tool],
    agent=technical_director,
)

# Define the task for recreating the network in Docker
recreate_network_docker = Task(
    description=(
        "Use the collected network and host information to recreate the target network in Docker."
        " Ensure that all configurations are accurately replicated."
    ),
    expected_output='A Docker Compose file and any necessary scripts to recreate the network.',
    tools=[search_tool],
    agent=docker_expert,
)

# Define the task for reviewing and critiquing
review_and_critique = Task(
    description=(
        "Review the tasks and provide feedback to ensure accuracy and efficiency."
        " Help the agents think through any challenges they face."
    ),
    expected_output='A report with feedback and suggestions for improvement.',
    tools=[search_tool],
    agent=critic,
)

# Form the crew
crew = Crew(
    agents=[operator, technical_director, docker_expert, critic],
    tasks=[collect_network_info, decompose_tasks, recreate_network_docker, review_and_critique],
    process=Process.sequential
)

# Kickoff the crew process
result = crew.kickoff(inputs={'topic': 'Digital Twin Network Recreation'})
print(result)
