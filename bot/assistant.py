from langchain.agents.openai_assistant import OpenAIAssistantRunnable

agent = OpenAIAssistantRunnable(assistant_id="asst_wt0En1rUOLgpmer0jZhX6pV6", as_agent=True)

output = agent.invoke({"content": "Что такое голова и плечи"})

print("Output: ", output)
