from web_navigator import initialize_driver, search_web, navigate_to_first_result
from content_extractor import extract_main_content
from ai_summarizer import summarize_text
import time

def chat():
    print("Chatbot: Hello! What web search task can I help you with today? (Type 'exit' to quit)")
    driver = None  # Initialize driver to None
    try:
        driver = initialize_driver()
        print("Chatbot: Browser initialized successfully.")
    except Exception as e:
        print(f"Chatbot: Critical error during browser initialization: {e}")
        print("Chatbot: Cannot proceed. Exiting.")
        return # Exit the chat function if driver initialization fails

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Chatbot: Goodbye!")
                break
            
            try:
                print(f"Chatbot: Processing your request for '{user_input}'...")
                
                search_web(driver, user_input)
                # Assuming search_web doesn't return a value but modifies driver state
                # No explicit confirmation here, relies on navigate_to_first_result for next step success
                
                print("Chatbot: Attempting to navigate to the first result...")
                url = navigate_to_first_result(driver)
                
                if url:
                    print(f"Chatbot: Successfully navigated to the first result: {url}")
                    print("Chatbot: Extracting content...")
                    extracted_text = extract_main_content(driver)

                    # Check for actual content vs. error messages from extractor
                    if extracted_text and extracted_text not in ["An error occurred while extracting content.", "No main content found on the page.", "Could not find body content."]:
                        print("Chatbot: Extracted content:")
                        if len(extracted_text) > 1000:
                            print(extracted_text[:1000] + "\n...")
                        else:
                            print(extracted_text)
                        
                        print("Chatbot: Summarizing content...")
                        summary = summarize_text(extracted_text)
                        # Check for actual summary vs. error messages from summarizer
                        if summary and summary not in ["Content too short to summarize.", "Could not generate a summary."]:
                            print("Chatbot: Summary:")
                            print(summary)
                        else:
                            # Print the specific message from summarize_text (e.g., "Content too short...")
                            print(f"Chatbot: {summary if summary else 'Could not generate a summary.'}")
                    else:
                        # Print the specific message from extract_main_content or a generic one
                        print(f"Chatbot: {extracted_text if extracted_text else 'No content could be extracted or an error occurred during extraction.'}")
                else:
                    print("Chatbot: Failed to navigate to the first result. This could be due to network issues, no results found, or unexpected search page structure. Please try another query.")

            except Exception as e:
                print(f"Chatbot: An unexpected error occurred while processing your request: {e}. Please try another query.")
                # The loop will continue for the next user input

    finally:
        if driver: # Check if driver was successfully initialized
            driver.quit()
            print("Chatbot: Browser closed.")
        else:
            print("Chatbot: Browser was not started or already closed.")

if __name__ == "__main__":
    chat()
