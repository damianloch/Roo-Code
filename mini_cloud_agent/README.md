# mini_cloud_agent/README.md

# Mini Cloud Agent Simulation

This is a simplified simulation of an intelligent agentic system capable of managing cloud infrastructure through a natural language interface. It demonstrates how an AI agent can interpret natural language prompts, select appropriate tools, execute them, and incorporate the results into its ongoing reasoning.

## Project Structure

- `main.py`: The main script to start the simulation. It initializes the agent and provides a command-line interface for user interaction.
- `agent.py`: Defines the `CloudAgent` class, which orchestrates the agentic loop. This includes:
    - Maintaining conversation history.
    - Calling a simulated LLM (for tool selection and reasoning).
    - Parsing tool calls from the LLM's response.
    - Executing the simulated cloud tools.
- `tools.py`: Contains Python functions that simulate the interaction with various cloud management tools. These functions do not connect to actual cloud providers but rather simulate responses from an internal LLM based on the tool's parameters.
- `prompts.py`: Defines the system prompt that guides the simulated LLM. This prompt includes:
    - The agent's role as an expert cloud engineer.
    - Detailed descriptions and usage examples for each available tool.
    - General guidelines for tool use (e.g., iterative steps, information gathering, error handling).

## Simulated Cloud Tools

The following tools are simulated:

- `cloud_query(selector)`: Returns canonical JSON describing the state of all resources that match selector.
- `iac_write(path, content)`: Creates or overwrites an Infrastructure-as-Code manifest.
- `iac_plan(directory, vars?)`: Runs an IaC engine's plan/preview step, returning a diff.
- `iac_apply(directory, auto_approve)`: Executes a previously generated IaC plan.
- `cloud_exec(provider, command)`: Runs an arbitrary CLI/kubectl/helm/SSH command.
- `monitor_fetch(resource_id, metric, window)`: Retrieves time-series or latest datapoint for a metric.
- `incident_action(runbook_yaml, target)`: Executes a predefined remediation or rollback recipe.
- `notify(message, channel)`: Sends a message to a specified channel for alerts or approvals.

## How to Run the Simulation

1.  **Navigate to the directory:**

    ```bash
    cd mini_cloud_agent
    ```

2.  **Install dependencies (if any, currently none specific, but good practice):**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the main script:**
    ```bash
    python main.py
    ```

## Interacting with the Agent

Once the simulation starts, you will see a `User:` prompt. You can type natural language requests, and the agent will simulate its reasoning process and tool calls. The output will show:

- The prompt sent to the internal LLM.
- The LLM's simulated response (which should ideally contain a tool call).
- The execution of the simulated tool and its output.

**Example Interaction:**

```
User: List all running EC2 instances.
```

The agent's simulated LLM might respond with a `cloud_query` tool call, and then the simulation will show the output of that simulated `cloud_query` call.

To exit the simulation, type `exit` at the `User:` prompt.
