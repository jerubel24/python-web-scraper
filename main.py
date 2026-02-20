import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from google import genai

# --- 2026 CONFIG ---
API_KEY = "AIzaSyB5w323b0LvgTjovvHxGTlZV_rIGS8mWHM"
# We use 2.5 Flash-Lite because it's the "Free Tier King" in 2026
MODEL_ID = "gemini-2.5-flash-lite" 

client = genai.Client(api_key=API_KEY)

async def ai_extract_data(html_text):
    """Sends clean text to Gemini to pull out the data."""
    print("🤖 AI is processing the page...")
    
    # We trim the text to 2000 chars to avoid "Token Limit" errors on free tier
    clean_text = html_text[:2000]
    
    prompt = (
        "Extract all book titles and their prices from this text. "
        "Format exactly like this: Title | Price. "
        "Text to analyze: " + clean_text
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return []

async def main():
    all_books = []
    
    async with async_playwright() as p:
        print("🌐 Launching Browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # URL for testing
        await page.goto("http://books.toscrape.com/")

        for i in range(1, 4): # Let's do 3 pages
            print(f"📄 Scraping Page {i}...")
            
            # Get the text directly from the page
            page_content = await page.evaluate("() => document.body.innerText")
            
            # Get data from AI
            data_lines = await ai_extract_data(page_content)
            
            for line in data_lines:
                if "|" in line:
                    all_books.append(line.split("|"))

            # Pacing: Free tier hates rapid requests. We wait 4 seconds.
            await asyncio.sleep(4)

            # Find and click "Next"
            next_button = page.get_by_text("next", exact=False)
            if await next_button.is_visible():
                await next_button.click()
                await page.wait_for_load_state("networkidle")
            else:
                break

        await browser.close()

    # Save to CSV
    if all_books:
        df = pd.DataFrame(all_books, columns=["Book Title", "Price"])
        df.to_csv("mac_scraped_data.csv", index=False)
        print(f"✅ DONE! Saved {len(df)} items to mac_scraped_data.csv")
    else:
        print("⚠️ No data was extracted. Check your API key status.")

if __name__ == "__main__":
    asyncio.run(main())