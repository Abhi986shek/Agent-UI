import boto3
import json
import re
import uuid
import streamlit as st
from botocore.config import Config
from datetime import datetime
import logging

# --------------------------
# Configuration and Setup
# --------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure longer timeouts for the boto3 client
boto_config = Config(
    connect_timeout=10000,
    read_timeout=10000,
    retries={'max_attempts': 3}
)

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client('bedrock-agent-runtime', config=boto_config, region_name='us-east-1')

# Replace with your actual agent ID
AGENT_ID = 'DFFR1BHXBX'


# --------------------------
# Utility Classes & Functions
# --------------------------

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def interact_with_agent(user_input, session_id):
    """
    Sends user input to the Bedrock agent and returns the AI response and trace events.

    Args:
        user_input (str): The user's input message.
        session_id (str): The session ID for maintaining chat context.

    Returns:
        Tuple[str, list]: The cleaned agent response and list of trace events.
    """
    try:
        response = bedrock_runtime.invoke_agent(
            agentId='JXVQQ8YSXA',
            agentAliasId='WXP6RZCUVX',
            sessionId=session_id,
            inputText=user_input,
            enableTrace=True
        )

        full_response = ""
        trace_events = []

        for event in response['completion']:
            if 'chunk' in event:
                chunk_text = event['chunk']['bytes'].decode('utf-8')
                full_response += chunk_text

            if 'trace' in event:
                trace_events.append(event['trace'])

        full_response = re.sub(r'<sources>.*?</sources>', '', full_response, flags=re.DOTALL)
        full_response = full_response.replace('<REDACTED>', 'pan')

        return full_response.strip(), trace_events

    except Exception as e:
        logger.exception("Error communicating with the Bedrock agent")
        st.error("An error occurred while connecting to the AI service. Please try again.")
        return "I'm having trouble connecting to the AI service right now. Please try again in a moment.", []

def format_trace_event(trace_event):
    """
    Format a trace event dictionary into a displayable markdown format.

    Args:
        trace_event (dict): The trace event from the agent.

    Returns:
        str: Markdown-formatted string representing the trace event.
    """
    try:
        if isinstance(trace_event, dict):
            if 'agentName' in trace_event:
                return f"**Agent:** {trace_event.get('agentName')}\n\n```json\n{json.dumps(trace_event, indent=2, cls=DateTimeEncoder)}\n```"
            elif 'type' in trace_event:
                return f"**{trace_event.get('type')}**\n\n```json\n{json.dumps(trace_event, indent=2, cls=DateTimeEncoder)}\n```"

        return f"```json\n{json.dumps(trace_event, indent=2, cls=DateTimeEncoder)}\n```"

    except Exception as e:
        logger.warning("Failed to format trace event")
        return f"Error formatting trace: {str(e)}\n{str(trace_event)[:500]}"


# --------------------------
# Streamlit App
# --------------------------

def main():
    """Main function to render the Streamlit app."""
    st.set_page_config(page_title="Rectification Agent", layout="wide")

    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'trace_history' not in st.session_state:
        st.session_state.trace_history = []
    if 'selected_request' not in st.session_state:
        st.session_state.selected_request = None

    # Layout setup
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("Rectification Agent")

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Log user message
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Process response
            ai_response, trace_events = interact_with_agent(user_input, st.session_state.session_id)

            request_id = str(uuid.uuid4())[:8]
            st.session_state.trace_history.append({
                "id": request_id,
                "user_input": user_input,
                "trace_events": trace_events
            })
            st.session_state.selected_request = request_id

            # Display agent response
            with st.chat_message("assistant"):
                st.markdown(ai_response)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    # Sidebar content
    with st.sidebar:
        st.title("Agent Traces")

        if st.button("New Chat"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.session_state.trace_history = []
            st.session_state.selected_request = None
            st.rerun()

        if st.session_state.trace_history:
            request_options = {
                f"Request {item['id']}: {item['user_input'][:20]}..." if len(item['user_input']) > 20 
                else f"Request {item['id']}: {item['user_input']}": item['id']
                for item in st.session_state.trace_history
            }
            selected_label = st.selectbox("Select Request", list(request_options.keys()), index=len(request_options)-1)
            st.session_state.selected_request = request_options[selected_label]

            for item in st.session_state.trace_history:
                if item['id'] == st.session_state.selected_request:
                    if item['trace_events']:
                        st.markdown("## Trace Events")
                        for i, event in enumerate(item['trace_events']):
                            with st.expander(f"Trace Event {i+1}"):
                                st.markdown(format_trace_event(event))
                    else:
                        st.info("No trace events available for this request.")
        else:
            st.info("No trace history available yet.")


if __name__ == "__main__":
    main()
