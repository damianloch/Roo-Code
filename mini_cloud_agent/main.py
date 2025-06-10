# main.py

import os
from flask import Flask, request, jsonify, render_template
from agent import CloudAgent
from tools import init_llm_for_tools
import re

app = Flask(__name__)

# Initialize LLM for tools. This will be done once when the app starts.
llm_for_tools = init_llm_for_tools()
agent = CloudAgent(llm_for_tools=llm_for_tools)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json.get('prompt')
    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Run the agent task. The agent.run_task will now return a list of structured responses.
    response_steps = agent.run_task(user_prompt)
    
    # Return the list of response steps to the frontend
    return jsonify({'response_steps': response_steps})

if __name__ == "__main__":
    print("Starting Cloud Agent Web Simulation...")
    # Ensure the static and templates folders exist for Flask to find them
    os.makedirs('mini_cloud_agent/templates', exist_ok=True)
    os.makedirs('mini_cloud_agent/static', exist_ok=True)
    app.run(debug=True, port=5000) 