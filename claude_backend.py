import os
import anthropic

# ---- Pricing table (USD per 1M tokens) ----
PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00
    }
}


class ClaudeBackend:
    def __init__(self, model="claude-sonnet-4-20250514", max_tokens=1500):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

        # ---- B10: Usage tracking ----
        self.last_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0
        }

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = PRICING.get(self.model)
        if not pricing:
            return 0.0

        cost = (
            (input_tokens / 1_000_000) * pricing["input"] +
            (output_tokens / 1_000_000) * pricing["output"]
        )
        return round(cost, 6)

    def judge(self, system_prompt: str, user_prompt: str) -> str:
        messages = [{"role": "user", "content": user_prompt}]

        msg = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0,  # deterministic
            system=system_prompt,
            messages=messages
        )

        # ---- Extract usage from API ----
        usage = msg.usage
        input_tokens = usage.input_tokens or 0
        output_tokens = usage.output_tokens or 0
        total_tokens = input_tokens + output_tokens

        estimated_cost = self._estimate_cost(input_tokens, output_tokens)

        self.last_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost
        }

        return msg.content[0].text.strip()


if __name__ == "__main__":
    backend = ClaudeBackend()
    out = backend.judge("You are helpful.", "What is 2+2?")
    print(out)
    print("USAGE:", backend.last_usage)
