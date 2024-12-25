from agent.agent_tools import (get_all_clinic_locations,
                               get_all_clinic_specialities,
                               get_doctors_by_filter,
                               write_appointment_details_to_db,
                               write_patient_information_to_db)
from agent.prompts import SYSTEM_PROMPT
from core.config import settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from utils.logger import get_logger

logger = get_logger()


llm_provider = settings.CONFIG["llm"]["llm_provider"]
llm_config = settings.CONFIG["llm"][llm_provider]

if llm_provider == "groq":
    # Get Groq API key
    groq_api_key = settings.GROQ_API_KEY
    llm = ChatGroq(
        model=llm_config["model"],
        temperature=llm_config["temperature"],
        max_tokens=llm_config["max_tokens"] if llm_config["max_tokens"] else None,
        timeout=llm_config["timeout"] if llm_config["timeout"] else None,
        )
    
elif llm_provider == "openai":
    # Get OpenAI API key
    openai_api_key = settings.OPENAI_API_KEY
    llm = ChatOpenAI(model=llm_config["model"],
                    temperature=llm_config["temperature"],
                    max_tokens=llm_config["max_tokens"] if llm_config["max_tokens"] else None,
                    timeout=llm_config["timeout"] if llm_config["timeout"] else None,
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
tools = [write_patient_information_to_db, get_all_clinic_specialities, get_all_clinic_locations,
          get_doctors_by_filter, write_appointment_details_to_db]

# Create the ReAct agent
agent_executor = create_react_agent(llm, tools, checkpointer=memory, state_modifier=SYSTEM_PROMPT)


# Use the agent
def generate_response(chat_history: list) -> tuple:
    """
    Generate a response from the agent based on the chat history.

    Args:
        chat_history (list): List of chat messages in the conversation.

    Returns:
        tuple: Tuple containing the final response from the agent and the intermediate tool calls.
    """

    logger.info(f"No. of messages in chat history: {len(chat_history)}")

    # Define the configuration for the agent
    config = {"configurable": {"thread_id": "abc123"}}
    
    # Invoke the agent with the updated messages & Return the content of the last message from the agent's response
    result = agent_executor.invoke({"messages": chat_history}, config)
    
    # Extract messages
    messages = result["messages"]
    
    # Extract intermediate tool calls
    tool_calls = []
    for msg in messages:
        if "tool_calls" in msg.additional_kwargs:
            for tool_call in msg.additional_kwargs["tool_calls"]:
                tool_name = tool_call.get("function", {}).get("name", "Unknown Tool")
                tool_input = tool_call.get("function", {}).get("arguments", "{}")
                tool_calls.append((tool_name, tool_input))
                logger.info(f"Tool: {tool_name} | Input: {tool_input}")
    
    # Return the assistant's final response and the tool calls
    final_response = messages[-1].content
    return final_response, tool_calls

