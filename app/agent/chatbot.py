from agent.agent_tools import query_doctors_data
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    MessagesPlaceholder)
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from utils.prompts import SYSTEM_PROMPT
from core.config import settings
import logging

logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file


# Get Groq API key
groq_api_key = settings.GROQ_API_KEY
model = 'llama3-8b-8192'  # "mixtral-8x7b-32768"


llm = ChatGroq(
    model=model,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


# Create the prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        # Placeholders fill up a **list** of messages
        ("placeholder", "{agent_scratchpad}"),
    ]
)


# Initialize MemorySaver for managing conversation state
memory = MemorySaver()
tools = [query_doctors_data]

# Create the ReAct agent
agent_executor = create_react_agent(llm, tools, checkpointer=memory, state_modifier=SYSTEM_PROMPT)


# Use the agent
def generate_response(chat_history):

    # Define the configuration for the agent
    config = {"configurable": {"thread_id": "abc123"}}
    
    # Invoke the agent with the updated messages & Return the content of the last message from the agent's response
    # Invoke the agent
    result = agent_executor.invoke({"messages": chat_history}, config)
    
    # Extract messages
    messages = result["messages"]
    
    # Extract intermediate steps
    intermediate_steps = []
    for msg in messages:
        if "tool_calls" in msg.additional_kwargs:
            for tool_call in msg.additional_kwargs["tool_calls"]:
                tool_name = tool_call.get("function", {}).get("name", "Unknown Tool")
                tool_input = tool_call.get("function", {}).get("arguments", "{}")
                intermediate_steps.append((tool_name, tool_input))
                logger.info(f"Tool: {tool_name} | Input: {tool_input}")
    
    # Return the assistant's final response and intermediate steps
    final_response = messages[-1].content
    return final_response, intermediate_steps

