import os
import argparse
import sqlite3
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Set environment variables for the tools (replace with your actual API keys)
os.environ["SERPER_API_KEY"] = "Your Serper API Key"
os.environ["OPENAI_API_KEY"] = "Your OpenAI API Key"

# Initialize the SerperDevTool for web search
search_tool = SerperDevTool()

# Define a function to create a SQLite database and table if they don't exist
def init_db():
    conn = sqlite3.connect('network_info.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS network_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT,
                    output TEXT
                 )''')
    conn.commit()
    conn.close()

# Call the init_db function to ensure the database and table are created
init_db()

# Define a function to log findings to the SQLite database
def log_to_db(command, output):
    conn = sqlite3.connect('network_info.db')
    c = conn.cursor()
    c.execute("INSERT INTO network_info (command, output) VALUES (?, ?)", (command, output))
    conn.commit()
    conn.close()

# Define a function to read network data from the SQLite database
def read_network_data():
    conn = sqlite3.connect('network_info.db')
    c = conn.cursor()
    c.execute("SELECT command, output FROM network_info")
    data = c.fetchall()
    conn.close()
    return data

# Define a function to craft CTF challenges based on network data
def craft_ctf_challenges(network_data):
    challenges = []
    for command, output in network_data:
        if "ifconfig" in command:
            challenges.append(f"Analyze the following ifconfig output and identify the IP address:\n{output}")
        elif "netstat" in command:
            challenges.append(f"Examine the netstat output and determine the active connections:\n{output}")
        elif "hostname" in command:
            challenges.append(f"Given the hostname output, find the machine's name:\n{output}")
    return challenges

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
        " Log the findings to a SQLite database."
    ),
    expected_output='A detailed report containing the network configuration and host information.',
    tools=[search_tool],
    agent=operator,
    actions=[
        {
            "action": "execute",
            "command": "ifconfig",
            "log_to_db": True
        },
        {
            "action": "execute",
            "command": "netstat",
            "log_to_db": True
        },
        {
            "action": "execute",
            "command": "hostname",
            "log_to_db": True
        }
    ]
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

# Define the CLI interface
def main():
    parser = argparse.ArgumentParser(description="Manage the crew for digital twin network recreation")
    parser.add_argument('--craft-ctf', action='store_true', help="Craft CTF challenges from network data")

    args = parser.parse_args()

    if args.craft_ctf:
        # Read network data from the database
        network_data = read_network_data()
        # Craft CTF challenges based on the data
        challenges = craft_ctf_challenges(network_data)
        for idx, challenge in enumerate(challenges, 1):
            print(f"Challenge {idx}: {challenge}")
    else:
        # Kickoff the crew process
        result = crew.kickoff(inputs={'topic': 'Digital Twin Network Recreation'})
        print(result)

if __name__ == "__main__":
    main()
