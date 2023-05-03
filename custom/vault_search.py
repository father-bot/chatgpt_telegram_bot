# vault_search.py

import os
import glob
import mistune
from whoosh.index import create_in
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.qparser import QueryParser
from whoosh import scoring
from bs4 import BeautifulSoup
import re
from os.path import dirname, abspath

def process_file_path(file_path: str) -> str:
    relevant_parts = file_path.split("/")[3:]  # Keep only the relevant parts of the path
    return " / ".join(relevant_parts)

def search_vault(vault_instance, query_str: str, max_content_size: int = 1000, max_results: int = 5) -> str:
    # Step 1: Traverse Obsidian vault and read .md files
    vault_path = vault_instance.local_path
    full_vault_path = os.path.join(vault_path, "**/*.md")
    md_files = glob.glob(full_vault_path, recursive=True)

    # Create the index directory if it does not exist
    index_directory = os.path.join(dirname(dirname(abspath(__file__))), "data", "index")
    if not os.path.exists(index_directory):
        os.makedirs(index_directory)

    # Step 2: Parse Markdown content
    markdown = mistune.create_markdown()

    # Step 3: Create search index with Whoosh
    schema = Schema(path=ID(stored=True, unique=True),
                    title=TEXT(stored=True),
                    content=TEXT(stored=True),
                    backlinks=KEYWORD,
                    emphasized=TEXT,
                    filepath=TEXT(stored=True))

    index = create_in(index_directory, schema)
    writer = index.writer()

    for md_file in md_files:
        with open(md_file, "r") as f:
            content = f.read()
            html = markdown(content)
            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = soup.h1.get_text() if soup.h1 else ""

            # Extract backlinks
            backlinks = set()
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and href.startswith("#"):
                    backlinks.add(href[1:])

            # Extract emphasized text
            emphasized = set()
            for em in soup.find_all("em"):
                emphasized.add(em.get_text())

            # Add them to the index
            processed_path = process_file_path(md_file)
            writer.add_document(
                path=md_file,
                title=title,
                content=content,
                backlinks=" ".join(backlinks),
                emphasized=" ".join(emphasized),
                filepath=processed_path
            )

    writer.commit()

    # Step 4: Ranking search results using BM25F
    searcher = index.searcher(
        weighting=scoring.BM25F(
            B=0.75,
            content_B=1.0,
            backlinks_B=1.5,
            emphasized_B=2.0,
            filepath_B=1.0
        )
    )

    query = QueryParser("content", index.schema).parse(query_str)
    results = searcher.search(query, limit=max_results)
    responses = []

    for hit in results:
        highlights = hit.highlights("content", top=3)
        highlights_clean = re.sub(r'<.*?>', '', highlights).strip()  # Remove HTML tags and extra spaces
        content = hit["content"][:max_content_size].strip() + "..." if len(hit["content"]) > max_content_size else hit["content"].strip()
        response = f"Title: {hit['title']}\nFile Path: {hit['filepath']}\n\nContent:\n{re.sub(' +', ' ', content)}\n\nHighlights:\n{re.sub(' +', ' ', highlights_clean)}"
        responses.append(response)

    return "\n\n---\n\n".join(responses)

def custom_score(searcher, fieldnum, textreader, docnum, weight):
    # Extract folder number from the file path
    filepath = searcher.stored_fields(docnum)["filepath"]
    folder_number = int(filepath.split(" / ")[0][0])
    # Calculate the custom score
    score = weight * (1 / (1 + folder_number))
    return score

