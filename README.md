# Sports News Summarizer

A Python project that scrapes the latest sports news articles, summarizes them using Google Gemini AI, and displays the results in a beautifully formatted markdown report via Streamlit.

## Features
- Scrapes top 5 sports news articles from [sportingnews.com]
- Extracts article content, tables, author, and date
- Summarizes the news using Google Gemini (Generative AI)
- Outputs the summary in markdown format
- Displays the summary interactively using Streamlit

## Requirements
- Python 3.8+
- [Google Gemini API key](https://aistudio.google.com/app/apikey)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/Gopika-3747/AI-News-Report-Summarizer.git
   cd SportsNewsSummarizer
   ```
2. Install dependencies:

   ```
   pip install playwright beautifulsoup4 python-dotenv google-generativeai streamlit
   playwright install
   ```
3. Set up your `.env` file with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage
1. **Scrape and Summarize News:**
   ```sh
   python one.py
   ```
   This will scrape articles, generate a markdown summary, and save it as `summary.md`.

2. **View the Summary in Streamlit:**
   ```sh
   streamlit run app.py
   ```
   This will open a browser window displaying the formatted summary.

## Project Structure
```
SportsNewsSummarizer/
├── app.py           # Streamlit app for displaying the summary
├── one.py           # Main script for scraping and summarizing
├── scraped_articles.csv  # Raw scraped articles (auto-generated)
├── summary.md       # Markdown summary (auto-generated)
└── .env             # Your API key (not included in repo)
```

## License
MIT License

## Credits
- [Google Gemini](https://aistudio.google.com/)
- [Sporting News](https://www.sportingnews.com/in/news)
- [Streamlit](https://streamlit.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Playwright](https://playwright.dev/python/)

---

Feel free to contribute or open issues for improvements!