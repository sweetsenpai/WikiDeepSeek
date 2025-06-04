from openai import AsyncOpenAI, OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

completion = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",
    messages=[
        {
            "role": "user",
            "content": "What meaning of life?"
        }
    ],
    max_tokens=5
)

print(completion.choices[0].message.content)


