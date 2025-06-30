import os
import json
import requests
import logging
from bs4 import BeautifulSoup
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# region Load environment variables

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_SEARCH_URL = os.getenv("GOOGLE_SEARCH_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_AI_MINI_MODEL = os.getenv("OPENAI_AI_MINI_MODEL")

# endregion

# region Clients setup

open_ai_client = OpenAI(api_key=OPENAI_API_KEY)

# endregion

# region Logging configuration

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# endregion


# Response schema for the RAG structured response
class RelevantPost(BaseModel):
    title: str
    link: str


class RAGResponse(BaseModel):
    analysis: str
    relevant_posts: list[RelevantPost]


def generate_search_term(query):
    """Generate a concise Google search term (3-5 words) based on the user's query."""
    try:
        response = open_ai_client.chat.completions.create(
            model=OPENAI_AI_MINI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Provide a Google search term (3-5 words) based on the user's query. Avoid including years unless specified.",
                },
                {"role": "user", "content": query},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating search term: {e}")
        return query


def google_search(query, search_depth=10, site_filter=None):
    """Perform a Google search and return the results."""
    service_url = GOOGLE_SEARCH_URL
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": search_depth,
    }

    try:
        response = requests.get(service_url, params=params)
        response.raise_for_status()
        results = response.json()

        if "items" in results:
            if site_filter:
                filtered_results = [
                    res for res in results["items"] if site_filter in res["link"]
                ]
                return filtered_results if filtered_results else []
            return results["items"]
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during search: {e}")
        return []


def fetch_page_content(url, max_tokens=50000):
    """Retrieve and clean web page content"""
    if url.endswith(".pdf"):
        logging.info(f"Skipping {url}: PDF files are not processed.")
        return None  # Ignore PDFs entirely

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[: max_tokens * 4]  # Approximate character limit for LLM input
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return None


def summarize_content(content, search_query, character_limit=700):
    """Generate a concise summary of extracted web content"""
    prompt = (
        f"You are an AI assistant summarizing content relevant to '{search_query}'. "
        f"Provide a concise summary within {character_limit} characters."
    )
    try:
        response = open_ai_client.chat.completions.create(
            model=OPENAI_AI_MINI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Summarization error: {e}")
        return None


def get_search_results(search_items, search_query, character_limit=700):
    """Fetch content, summarize it, and return structured search results"""
    results_list = []
    for idx, item in enumerate(search_items, start=1):
        url = item.get("link")
        snippet = item.get("snippet", "")
        web_content = fetch_page_content(url)

        if not web_content:
            logging.info(f"Skipping {url}")
            continue
        else:
            summary = summarize_content(web_content, search_query, character_limit)
            results_list.append(
                {"order": idx, "link": url, "title": snippet, "summary": summary}
            )

    return results_list


def generate_rag_response(search_query, results, problem_statement, target_audience):
    """Create a structured JSON response using GPT-4o-mini based on search results."""
    formatted_results = [
        {"title": item["title"], "link": item["link"], "summary": item["summary"]}
        for item in results
    ]

    try:
        response = open_ai_client.chat.completions.create(
            model=OPENAI_AI_MINI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI idea validator that helps users validate their ideas based on search results.\n"
                        "Analyze the findings to identify key insights, common challenges, and trends.\n"
                        "Your response must follow this JSON format:\n"
                        "{\n"
                        '  "analysis": "A well-structured, insightful summary of the key themes, pain points, and opportunities from the search results. '
                        'Provide context, highlight gaps, and suggest potential directions for validation. Start with explicitly mentioning the Problem Statement with Target Audience",\n'
                        '  "relevant_posts": [{"title": "Title of the article", "link": "URL"}]\n'
                        "}\n\n"
                        "Ensure to divide the 'analysis' into paragraphs (2-3, with new lines) and make 'analysis' go beyond summarization—identify industry trends, common challenges, and gaps in discussion. "
                        "Your goal is to help users assess the feasibility and market potential of their idea based on their Query."
                    ),
                },
                {
                    "role": "user",
                    "content": f"User's Query: {search_query}\nUser's Problem Statement: {problem_statement}\nTarget Audience: {target_audience}\nResults:\n{json.dumps(formatted_results, indent=2)}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        response_json = json.loads(response.choices[0].message.content)

        response_data = RAGResponse.model_validate(response_json)

        response_data_dict = response_data.model_dump()

        return (
            response_data_dict  # Returns the structured response with titles and links
        )

    except Exception as e:
        logging.error(f"Final RAG response error: {e}")
        return None


def perform_search_and_summarize(search_query, problem_statement, target_audience):
    refined_query = generate_search_term(search_query)

    logging.info(f"Generating the proper search term: {refined_query}")

    search_results = google_search(refined_query, search_depth=7)

    if not search_results:
        logging.info("No search results found.")
        return None

    structured_results = get_search_results(search_results, search_query)

    final_summary = generate_rag_response(
        search_query, structured_results, problem_statement, target_audience
    )

    output = {
        "query": search_query,
        "results": structured_results,
        "final_summary": final_summary,
    }
    return output
