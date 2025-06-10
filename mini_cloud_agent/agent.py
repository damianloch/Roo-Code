# agent.py

import re
import json
from prompts import get_system_prompt

class CloudAgent:
    def __init__(self, llm_for_tools):
        self.conversation_history = []
        self.llm_for_tools = llm_for_tools
        self.tools = self._initialize_tools()

    def _initialize_tools(self):
        # In a real system, these would be actual cloud API integrations.
        # For simulation, these will call functions in tools.py that simulate LLM responses.
        from tools import (
            cloud_query, iac_write, iac_plan, iac_apply,
            cloud_exec, monitor_fetch, incident_action, notify
        )
        return {
            "cloud_query": cloud_query,
            "iac_write": iac_write,
            "iac_plan": iac_plan,
            "iac_apply": iac_apply,
            "cloud_exec": cloud_exec,
            "monitor_fetch": monitor_fetch,
            "incident_action": incident_action,
            "notify": notify,
        }

    def _call_llm(self, prompt: str) -> str:
        """Calls the LLM with the given prompt."""
        return self.llm_for_tools(prompt)

    def run_task(self, user_query: str) -> list[dict]:
        # Each item in `response_steps` will be a dictionary representing a message
        # to be sent to the frontend (user, agent_text, tool_call, tool_output, error)
        response_steps = []

        # Append the initial user query to the history and response steps
        self.conversation_history.append({"role": "user", "content": user_query})
        response_steps.append({"type": "user", "content": user_query})

        max_steps = 5  # Limit the number of agent steps to prevent infinite loops
        step_count = 0
        
        # Loop until the agent responds with direct text or max_steps is reached
        while step_count < max_steps:
            step_count += 1

            system_prompt = get_system_prompt()
            
            # Combine system prompt, conversation history, and current user query
            full_prompt = system_prompt
            for message in self.conversation_history:
                if message["role"] == "user":
                    full_prompt += f"\nUser: {message['content']}"
                elif message["role"] == "assistant":
                    full_prompt += f"\nAssistant: {message['content']}"
                elif message["role"] == "tool_output":
                    full_prompt += f"\nTool Output: {message['content']}"

            print("\n--- Agent's Full Prompt to LLM ---")
            print(full_prompt)
            print("----------------------------------")

            llm_response = self._call_llm(full_prompt)
            self.conversation_history.append({"role": "assistant", "content": llm_response})

            # --- NEW: Extract Thought and Tool Call Separately ---
            thought_match = re.search(r"<thought>(.*?)</thought>", llm_response, re.DOTALL)
            agent_thought_content = thought_match.group(1).strip() if thought_match else None

            if agent_thought_content:
                response_steps.append({"type": "agent_thought", "content": agent_thought_content})
                print(f"\nAgent Thought: {agent_thought_content}")

            tool_call_match = re.search(r"<tool_code>\s*<(\w+?)>(.*?)</\1>\s*</tool_code>", llm_response, re.DOTALL)

            if tool_call_match:
                tool_name = tool_call_match.group(1)
                tool_args_str = tool_call_match.group(2)

                # The agent_message_text for console printing can still include the tool call for context
                # but the frontend component will handle it separately.
                agent_message_for_console = f"Agent wants to use tool: {tool_name} with arguments: {tool_args_str}"
                if not agent_thought_content: # Only print if there wasn't a separate thought
                     print(f"\n{agent_message_for_console}")
                
                # Extract arguments. This is a simple regex-based parser. 
                args = {}
                arg_matches = re.findall(r"<(\w+?)>\s*(.*?)\s*<\/\1>", tool_args_str, re.DOTALL)
                for arg_name, arg_value in arg_matches:
                    args[arg_name] = arg_value

                if tool_name in self.tools:
                    try:
                        # Execute the tool and get its output
                        tool_output = self.tools[tool_name](**args)
                        tool_output_message = f"Tool ({tool_name}) Output:\n{tool_output}"
                        response_steps.append({
                            "type": "tool_call",
                            "tool_name": tool_name,
                            "tool_args": args,
                            "tool_output": tool_output
                        })
                        print(f"\n{tool_output_message}")
                        self.conversation_history.append({"role": "tool_output", "content": tool_output})
                    except TypeError as e:
                        error_message = f"Error calling tool {tool_name} with args {args}: {e}"
                        print(f"\n{error_message}")
                        self.conversation_history.append({"role": "tool_output", "content": error_message})
                        response_steps.append({"type": "error", "content": error_message})
                        break # Stop if tool call fails critically
                    except Exception as e:
                        error_message = f"An unexpected error occurred during tool execution: {e}"
                        print(f"\n{error_message}")
                        self.conversation_history.append({"role": "tool_output", "content": error_message})
                        response_steps.append({"type": "error", "content": error_message})
                        break # Stop if tool execution fails critically
                else:
                    error_message = f"Error: Unknown tool requested by LLM: {tool_name}"
                    print(f"\n{error_message}")
                    self.conversation_history.append({"role": "tool_output", "content": error_message})
                    response_steps.append({"type": "error", "content": error_message})
                    break # Stop if unknown tool is requested
            else:
                # If no tool call, it's a direct text response, which means the agent is done
                # If there was a thought, but no tool call, the thought was the final response.
                if not agent_thought_content:
                    print("\nAgent's direct response (no tool call detected):")
                    print(llm_response)
                    response_steps.append({"type": "agent_text", "content": llm_response})
                break # Agent is done, exit loop

        return response_steps 