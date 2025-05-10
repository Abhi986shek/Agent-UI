# Rectification Agent

The Rectification Agent is a Streamlit-based web application designed for secure and interactive communication with an Amazon Bedrock agent. It enables users to send queries, receive AI-generated responses, and inspect detailed execution traces in real-time.

---

## Overview

This application provides a minimal, efficient frontend to interact with Bedrock agents through the `bedrock-agent-runtime` Boto3 client. It is suited for developers, data scientists, and support engineers who need visibility into agent reasoning and API flows.

---

## Features

- Streamlit-powered chat interface for real-time interaction
- Integration with Amazon Bedrock agents (via Boto3)
- Support for response streaming and trace capture
- Session management and in-app chat history
- Trace inspection panel for debugging and transparency
- Secure handling of sensitive data in agent output
- Error handling with visible traceback information

---

## Architecture



\[User Input] → \[Streamlit Frontend] → \[Amazon Bedrock Agent Runtime]
↓                                         ↑
\[Chat History]                        \[Trace Events with Metadata]



---

## Prerequisites

- Python 3.8+
- An active AWS account with Bedrock access
- AWS credentials configured locally (`~/.aws/credentials` or environment variables)

---

## Installation

1. **Clone the repository**


git clone https://github.com/your-org/rectification-agent.git
cd rectification-agent


2. **Install dependencies**


pip install -r requirements.txt


3. **Configure AWS credentials**

Using environment variables:


export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1


Or use the AWS CLI to configure:


aws configure


---

## Usage

Run the application locally:


streamlit run agent_app.py


The application will launch in your default browser at `http://localhost:8501`.

---

## Configuration

Edit `agent_app.py` to specify your agent parameters:


AGENT_ID = 'your-agent-id'
AGENT_ALIAS_ID = 'your-alias-id'
REGION = 'us-east-1'



