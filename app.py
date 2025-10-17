import sys 
import subprocess
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

logging.info("Starting Agents")
agents = ["agents/web_agent/web_agent.py","agents/directory_agent/directory_agent.py","agents/test_agent/test_agent.py",]

python_executable = sys.executable


    
processes = [subprocess.Popen([python_executable, script]) for script in agents]

for process in processes:
    process.wait()

logging.info("All agents have finished")