from langchain.agents.openai_assistant import OpenAIAssistantRunnable
# from langchain_openai import ChatOpenAI
import os


import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

agent = OpenAIAssistantRunnable(assistant_id="asst_wt0En1rUOLgpmer0jZhX6pV6", as_agent=True)


