import asyncio
from playwright.async_api import async_playwright
from agent import create_graph, update_scratchpad, select_tool, call_agent

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.google.com")

        # Graph creation inside main ensures all dependencies are available
        graph = create_graph(update_scratchpad, select_tool)

        # Call the agent with your specific question
        question = "Can you search up the rickroll video on youtube?"
        response = await call_agent(graph, question, page)
        print(f"Final response: {response}")

        await browser.close()

# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())