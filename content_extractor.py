from bs4 import BeautifulSoup

def extract_main_content(driver):
    """Extracts the main textual content from the currently loaded page in the driver."""
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Attempt to find a main content area
        main_content_area = (soup.find('main') or 
                             soup.find('article') or 
                             soup.find(id='content') or 
                             soup.find(id='main-content') or 
                             soup.find(class_='post-content')) # Added common class

        if not main_content_area:
            main_content_area = soup.body # Fallback to whole body
        
        if not main_content_area: # If body is also None (very unlikely for valid HTML)
            return "Could not find body content."

        # Extract text from relevant tags
        texts = []
        # Added more tags like div, span for broader text capture, but this can be noisy
        # For now, sticking to the requested tags.
        for element in main_content_area.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
            texts.append(element.get_text(separator=' ', strip=True))
        
        full_text = '\n'.join(texts)

        if not full_text.strip():
            return "No main content found on the page."
            
        return full_text

    except Exception as e:
        print(f"Error during content extraction: {e}")
        return "An error occurred while extracting content."
