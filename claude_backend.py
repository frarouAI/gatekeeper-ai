import anthropic
import os


class ClaudeBackend:
    def __init__(self, model="claude-sonnet-4-20250514", max_tokens=1500):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def judge(self, system_prompt, user_prompt):
        messages = [{"role": "user", "content": user_prompt}]

        msg = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages
        )

        return msg.content[0].text.strip()


if __name__ == "__main__":
    backend = ClaudeBackend()

    SYSTEM_PROMPT = "You are a helpful AI assistant."
    USER_PROMPT = "What is 2+2?"

    out = backend.judge(SYSTEM_PROMPT, USER_PROMPT)
    print(out)
