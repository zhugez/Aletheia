---
name: chatgpt-app-builder
description: >
  Build applications powered by ChatGPT and OpenAI APIs. Covers the Assistants API,
  function calling, structured outputs, streaming, and best practices for building reliable
  GPT-powered products.
  Use when: chatgpt app, openai assistant, gpt app builder, ai chatbot, openai api.
---

# ChatGPT App Builder Skill

> Build production-ready applications powered by OpenAI's ChatGPT and Assistants API.

## When to Use

- Building chatbot applications with OpenAI's API
- Creating AI assistants with custom tools and function calling
- Implementing streaming chat interfaces
- Building products that leverage GPT-4o, GPT-4.1, or other OpenAI models
- Integrating ChatGPT capabilities into existing applications

## SDK Setup

### Python

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY env var

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
print(response.choices[0].message.content)
```

### Node.js / TypeScript

```bash
npm install openai
```

```typescript
import OpenAI from "openai";

const openai = new OpenAI();

const completion = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" },
  ],
});

console.log(completion.choices[0].message.content);
```

## Key Patterns

### 1. Function Calling (Tool Use)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                },
                "required": ["location"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
```

### 2. Structured Outputs

```python
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract event information."},
        {"role": "user", "content": "Team lunch next Friday with Alice and Bob"},
    ],
    response_format=CalendarEvent,
)

event = completion.choices[0].message.parsed
```

### 3. Streaming

```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 4. Assistants API

```python
# Create an assistant
assistant = client.beta.assistants.create(
    name="Data Analyst",
    instructions="You analyze CSV data and provide insights.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)

# Create a thread and run
thread = client.beta.threads.create()
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze the trends in this data...",
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
```

## Best Practices

1. **Use structured outputs** — Enforce response format with Pydantic models or JSON schema
2. **Implement retry logic** — Handle rate limits with exponential backoff
3. **Stream responses** — Better UX for chat interfaces
4. **Cache responses** — Reduce costs for repeated queries
5. **Set max_tokens** — Prevent unexpectedly long (and expensive) responses
6. **Use system prompts effectively** — Clear, specific instructions improve output quality
7. **Monitor token usage** — Track costs with `usage` field in API responses

## Cost Optimization

- Use `gpt-4o-mini` for simple tasks, `gpt-4o` for complex reasoning
- Implement prompt caching for repeated system prompts
- Batch API for non-real-time workloads (50% cheaper)
- Trim conversation history to reduce input tokens

## References

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [OpenAI Cookbook](https://cookbook.openai.com)
- [Assistants API Guide](https://platform.openai.com/docs/assistants)
