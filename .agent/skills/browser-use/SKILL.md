---
name: browser-use
description: >
  AI-powered browser automation using Browser-Use library. Build agents that can navigate,
  interact with, and extract data from web pages autonomously using LLMs and Chrome DevTools Protocol.
  Use when: browser automation, web scraping agent, AI browser agent, browser-use, CDP automation.
---

# Browser-Use Skill

> Build AI agents that autonomously browse the web using LLMs and the Chrome DevTools Protocol.

## When to Use

- Building AI agents that need to interact with web pages
- Automating web tasks (form filling, data extraction, navigation)
- Creating autonomous web research agents
- Testing web applications with AI-driven exploration
- Scraping dynamic content that requires JavaScript execution

## Core Concepts

### Architecture

```
User Task → LLM (Claude/GPT) → Browser-Use Controller → Chrome CDP → Web Page
                ↑                        ↓
                └──── Page State (HTML/Screenshot) ────┘
```

### Installation

```bash
pip install browser-use
playwright install chromium
```

### Basic Agent

```python
from browser_use import Agent
from langchain_anthropic import ChatAnthropic

agent = Agent(
    task="Find the latest Python release version on python.org",
    llm=ChatAnthropic(model="claude-sonnet-4-20250514"),
)

result = await agent.run()
print(result)
```

### Advanced Configuration

```python
from browser_use import Agent, Browser, BrowserConfig

browser = Browser(
    config=BrowserConfig(
        headless=True,
        disable_security=False,
        extra_chromium_args=["--no-sandbox"],
    )
)

agent = Agent(
    task="Navigate to example.com and extract all links",
    llm=llm,
    browser=browser,
    max_actions_per_step=5,
    use_vision=True,  # Use screenshots for better understanding
)
```

## Key Patterns

### 1. Multi-Step Task Automation

```python
agent = Agent(
    task="""
    1. Go to github.com
    2. Search for 'browser-use'
    3. Click on the first repository result
    4. Extract the star count and description
    """,
    llm=llm,
)
```

### 2. Data Extraction

```python
agent = Agent(
    task="Go to news.ycombinator.com and extract the top 10 story titles with their URLs",
    llm=llm,
    max_actions_per_step=3,
)
```

### 3. Form Interaction

```python
agent = Agent(
    task="""
    Go to the contact form at example.com/contact
    Fill in: Name='Test User', Email='test@example.com', Message='Hello'
    Submit the form
    """,
    llm=llm,
)
```

## Best Practices

1. **Be specific in task descriptions** — Clear, step-by-step instructions yield better results
2. **Use vision mode** for complex UIs — `use_vision=True` sends screenshots to the LLM
3. **Set reasonable action limits** — Prevent infinite loops with `max_actions_per_step`
4. **Handle authentication carefully** — Never hardcode credentials in task descriptions
5. **Use headless mode in production** — `headless=True` for server deployments
6. **Implement error handling** — Wrap agent runs in try/except for graceful failures

## Common Pitfalls

- **CAPTCHAs**: Browser-Use cannot solve CAPTCHAs; use authenticated sessions instead
- **Rate limiting**: Add delays between actions for sensitive websites
- **Dynamic content**: Use `use_vision=True` for SPAs with heavy JavaScript
- **Memory usage**: Close browser instances after use to prevent memory leaks

## References

- [Browser-Use GitHub](https://github.com/browser-use/browser-use)
- [Browser-Use Documentation](https://docs.browser-use.com)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
