import config

import openai
openai.api_key = config.openai_api_key


CHAT_MODES = {
    "assistant": {
        "name": "👩🏼‍🎓 Assistant",
        "welcome_message": "👩🏼‍🎓 Hi, I'm <b>ChatGPT assistant</b>. How can I help you?",
        "prompt_start": "As an advanced chatbot named ChatGPT, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user. If you have code in your reply, write it inside <code>, </code> tags."
    },

    "code_assistant": {
        "name": "👩🏼‍💻 Code Assistant",
        "welcome_message": "👩🏼‍💻 Hi, I'm <b>ChatGPT code assistant</b>. How can I help you?",
        "prompt_start": "As an advanced chatbot named ChatGPT, your primary goal is to assist users to write code. This may involve designing/writing/editing/describing code or providing helpful information. Where possible you should provide code examples to support your points and justify your recommendations or solutions. Make sure the code you provide is correct and can be run without errors. Be detailed and thorough in your responses. Your ultimate goal is to provide a helpful and enjoyable experience for the user. Write code inside <code>, </code> tags."
    },

    "movie_expert": {
        "name": "🎬 Movie Expert",
        "welcome_message": "🎬 Hi, I'm <b>ChatGPT movie expert</b>. How can I help you?",
        "prompt_start": "As an advanced movie expert chatbot named ChatGPT, your primary goal is to assist users to the best of your ability. You can answer questions about movies, actors, directors, and more. You can recommend movies to users based on their preferences. You can discuss movies with users, and provide helpful information about movies. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."
    },
}


class ChatGPT:
    def __init__(self):
        pass
    
    def send_message(self, message, chat_context=[], chat_mode="assistant"):
        if chat_mode not in CHAT_MODES.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        chat_context_len_before = len(chat_context)
        answer = None
        while answer is None:
            prompt = self._generate_prompt(message, chat_context, chat_mode)
            try:
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

                n_used_tokens = r.usage.total_tokens

            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(chat_context) == 0:
                    raise ValueError("chat_context is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in chat_context
                chat_context = chat_context[1:]

        n_first_chat_context_messages_removed = chat_context_len_before - len(chat_context)

        # update chat_context
        chat_context.append({"user": message, "chatgpt": answer})

        return answer, prompt, chat_context, n_used_tokens, n_first_chat_context_messages_removed

    def _generate_prompt(self, message, chat_context, chat_mode):
        prompt = CHAT_MODES[chat_mode]["prompt_start"]
        prompt += "\n\n"

        # add chat context
        if len(chat_context) > 0:
            prompt += "Chat:\n"
            for chat_context_item in chat_context:
                prompt += f"User: {chat_context_item['user']}\n"
                prompt += f"ChatGPT: {chat_context_item['chatgpt']}\n"

        # current message
        prompt += f"User: {message}\n"
        prompt += "ChatGPT: "

        return prompt
