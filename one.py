from playwright.sync_api import sync_playwright
import os
from bs4 import BeautifulSoup
import time
import csv
import sys
import asyncio

import google.generativeai as genai 
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from IPython.display import Markdown , display

#load environment variables
load_dotenv()

def extract_tables(soup):
    """Extract and format tables from soup"""
    tables = []
    for i, table in enumerate(soup.find_all('table'), 1):
        # Get headers
        header_row = table.find('thead') or table.find('tr')
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])] if header_row else []
        
        # Get rows
        rows = []
        for tr in table.find_all('tr')[1:] if headers else table.find_all('tr'):
            row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if row and row != headers:
                rows.append(row)
        
        if headers or rows:
            # Format table
            formatted = f"\n--- TABLE {i} ---\n"
            if headers:
                formatted += " | ".join(headers) + "\n" + "-" * len(" | ".join(headers)) + "\n"
            for row in rows:
                formatted += " | ".join(row) + "\n"
            formatted += f"--- END TABLE {i} ---\n"
            tables.append(formatted)
    
    return tables

def extract_content(soup, selectors):
    """Extract content using multiple selectors"""
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            content = []
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 20:
                    content.append(text)
            if content:
                return '\n\n'.join(content) 
    return ''

def extract_single_field(soup, selectors):
    """Extract single field using multiple selectors"""
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text:
                return text
            
            if element.get('datetime'):
                return element.get('datetime')
    return ''

def scrape_article(page, url):
    """Extract content from a single article"""
    try:
        print(f"\n--- Extracting: {url} ---")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(2)  
        
        soup = BeautifulSoup(page.content(), "html.parser")
        
        # Extract tables first
        tables = extract_tables(soup)
        
        # Remove tables from soup to avoid duplication in content
        for table in soup.find_all('table'):
            table.extract()
        
        return {
            'url': url,
            'title': extract_single_field(soup, ['h1', 'h1[class*="headline"]']),
            'author': extract_single_field(soup, ['.author', '[class*="author"]', '.byline']),
            'date': extract_single_field(soup, ['.date', '[class*="date"]', 'time', '[datetime]']),
            'content': extract_content(soup, ['.article-content', '.article-body', '[class*="content"]', 'article p', 'main p', 'p']),
            'tables': '\n'.join(tables) if tables else '',  
            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None

def save_to_csv(articles, filename='scraped_articles.csv'):
    """Save articles to CSV file"""
    if not articles:
        print("No articles to save.")
        return
    
    # Define CSV columns
    fieldnames = ['scraped_at', 'title', 'author', 'date', 'url', 'content', 'tables']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write articles
        for article in articles:
            writer.writerow(article)
    
    print(f"\nSuccessfully saved {len(articles)} articles to '{filename}'")

def scrape_sportingnews():
    """Main scraping function"""
    # Ensure proper event loop policy on Windows for subprocess support used by Playwright
    if sys.platform.startswith('win'):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, slow_mo=0)
            page = browser.new_page()
            time.sleep(1)  
            
            page.set_default_timeout(30000)
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            # Get article links
            print("Loading main page...")
            page.goto("https://www.sportingnews.com/in/news", wait_until="domcontentloaded")
            time.sleep(2)  
            
            soup = BeautifulSoup(page.content(), "html.parser")
            links = soup.select("a[class*='group']")
            
            # Get unique article URLs
            urls = set()
            for link in links[:5]:
                href = link.get('href')
                if href and '/news/' in href:
                    url = href if href.startswith('http') else f"https://www.sportingnews.com{href}"
                    text = link.get_text(strip=True).lower()
                    if not any(skip in text for skip in ['read more', 'more>', 'view all']):
                        urls.add(url)
            
            urls = list(urls)[:5]  # Limit to 5 articles
            print(f"Found {len(urls)} articles to scrape")
            
            # Scrape articles
            all_articles = []
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*60}\nARTICLE {i}/{len(urls)}\n{'='*60}")
                
                article = scrape_article(page, url)
                if article:
                    all_articles.append(article)
                    print(f"Successfully scraped: {article['title'][:50]}...")
                else:
                    print(f"Failed to extract article {i}")
                
                time.sleep(3)
            
            if all_articles:
                save_to_csv(all_articles)
                print(f"\nScraping completed! Check 'scraped_articles.csv' for results.")
            else:
                print("\nNo articles were successfully scraped.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                browser.close()
                print("Browser closed.")
            except:
                pass

def summarize(content):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')

    user_prompt = f"""
You are a helpful assistant who updates the user with the latest news in the sports world. Focus on extracting the most important information and key points.Give output in markdown format. only include the genereated content in the markdown format, do not include any other text or comments.

User: Please provide a concise summary on these top 5 sports news in the world. Focus on the key points and main information; Also give the output in a report format with tables (if needed).
Summarization content: {content} - each item in this list is a news article.
Assistant:
    """
    response = model.generate_content(user_prompt)
    summary = response.text
    return summary

def prepare_data(csv_file):
    content = []
    with open(csv_file,'r',encoding = 'utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            content.append(row)
    return content


        
if __name__ == "__main__":
    scrape_sportingnews()
    content = prepare_data('scraped_articles.csv')
    summary = summarize(content)
    with open ("summary.md","w",encoding='utf-8') as f:
        f.write(summary)
    print("Markdown summary saved")