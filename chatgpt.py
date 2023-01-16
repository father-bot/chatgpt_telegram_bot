import openai


PROMPT_START = """As an advanced chatbot named ChatGPT, your primary goal is to assist users to the best of your ability.
This may involve answering questions, providing helpful information, or completing tasks based on user input.
In order to effectively assist users, it is important to be detailed and thorough in your responses.
Use examples and evidence to support your points and justify your recommendations or solutions.
Remember to always prioritize the needs and satisfaction of the user.
Your ultimate goal is to provide a helpful and enjoyable experience for the user.
If you have code in your reply, write it inside the <code>, </code> tags
"""

# TODO: add different chat modes: code writing helper, therapist, expert in X, etc.


class ChatGPT:
    def __init__(self, openai_api_key=""):
        self.openai_api_key = openai_api_key
        self.context = []
    
    def send_message(self, message):
        openai.api_key = self.openai_api_key

        # get answer
        prompt = self._generate_prompt(message)
        r = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        answer = r.choices[0].text
        answer = answer.strip()

        # update context
        self.context.append({"user": message, "chatgpt": answer})

        return answer, prompt

    def reset_context(self):
        self.context = []

    def _generate_prompt(self, message):
        prompt = PROMPT_START
        prompt += "\n"

        # chat history
        if len(self.context) > 0:
            prompt += "Chat:\n"
            for context_item in self.context:
                prompt += f"User: {context_item['user']}\n"
                prompt += f"ChatGPT: {context_item['chatgpt']}\n"

        # current message
        prompt += f"User: {message}\n"
        prompt += "ChatGPT: "

        return prompt