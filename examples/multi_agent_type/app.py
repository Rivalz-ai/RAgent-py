import uuid
import chainlit as cl
from backend.agents import create_tech_agent, create_travel_agent, create_health_agent,create_X_agent
from rAgent.orchestrator import SwarmOrchestrator, OrchestratorConfig
from rAgent.classifiers import OpenAIClassifier, OpenAIClassifierOptions
from rAgent.types import ConversationMessage
from rAgent.agents import AgentResponse
import os
from dotenv import load_dotenv
from rAgent.utils import Logger
load_dotenv()

# Initialize the orchestrator
Logger.info("Creating classifier")
custom_openai_classifier = OpenAIClassifier(OpenAIClassifierOptions(
    api_key=os.getenv('OPENAI_API_KEY'),
    model_id='gpt-4o',
    inference_config={
                    'maxTokens': 500,
                    'temperature': 0.5,
                    'topP': 0.8,
                    'stopSequences': []
                }
    ))
Logger.info("Creating orchestrator")
orchestrator = SwarmOrchestrator(options=OrchestratorConfig(
        LOG_AGENT_CHAT=True,
        LOG_CLASSIFIER_CHAT=True,
        LOG_CLASSIFIER_RAW_OUTPUT=True,
        LOG_CLASSIFIER_OUTPUT=True,
        LOG_EXECUTION_TIMES=True,
        MAX_RETRIES=3,
        USE_DEFAULT_AGENT_IF_NONE_IDENTIFIED=False,
        MAX_MESSAGE_PAIRS_PER_AGENT=10
    ),
    classifier=custom_openai_classifier
)

# Add agents to the orchestrator
orchestrator.add_agent(create_tech_agent())
orchestrator.add_agent(create_travel_agent())
orchestrator.add_agent(create_health_agent())
orchestrator.add_agent(create_X_agent("R1hwM3RjenJrMkh2cDNyZ2pLMFZwdUttV0pFMVF3WWRzcEFESlBrMlFiajJkOjE3NDE5ODY3MzE2MDY6MTowOmF0OjE"))
@cl.on_chat_start
async def start():
    cl.user_session.set("user_id", str(uuid.uuid4()))
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("chat_history", [])



@cl.on_message
async def main(message: cl.Message):
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")

    msg = cl.Message(content="")

    await msg.send()  # Send the message immediately to start streaming
    cl.user_session.set("current_msg", msg)

    response:AgentResponse = await orchestrator.route_request(message.content, user_id, session_id, {})


    # Handle non-streaming responses
    if isinstance(response, AgentResponse) and response.streaming is False:
        # Handle regular response
        if isinstance(response.output, str):
            await msg.stream_token(response.output)
        elif isinstance(response.output, ConversationMessage):
                await msg.stream_token(response.output.content[0].get('text'))
    await msg.update()


if __name__ == "__main__":
    cl.run()