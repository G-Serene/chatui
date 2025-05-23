# Web Search AI Chatbot

## Description
A command-line chatbot that performs a web search based on user input, navigates to the first Google search result, extracts the main content from the webpage, and provides a summary (currently using a mock summarizer).

## Prerequisites
Before you begin, ensure you have the following installed:
*   Python 3.x
*   Google Chrome browser installed.
*   ChromeDriver installed and available in your system's PATH.

## Setup Instructions for ChromeDriver

ChromeDriver is essential for automating and controlling the Google Chrome browser, which this chatbot uses for web navigation.

1.  **Identify your Chrome Version**:
    *   Open Google Chrome.
    *   Go to `Settings` (click the three vertical dots in the top-right corner).
    *   Click on "About Chrome". Note down the version number (e.g., Version 96.x.xxxx.xx).

2.  **Download ChromeDriver**:
    *   Go to the official ChromeDriver downloads page: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
    *   Download the ChromeDriver version that **matches your Google Chrome browser version**. If an exact match isn't available, choose the closest one available for your major version.

3.  **Install ChromeDriver (Make it available in PATH)**:
    *   Unzip the downloaded file to get the `chromedriver` executable.
    *   Move this `chromedriver` executable to a directory that is part of your system's PATH environment variable. This allows the system to find the executable when called by scripts.
        *   **macOS/Linux**:
            *   Common directories include `/usr/local/bin/` or `~/bin/`.
            *   Example command: `sudo mv chromedriver /usr/local/bin/` (you might need administrator privileges).
            *   Ensure the file is executable: `sudo chmod +x /usr/local/bin/chromedriver`.
        *   **Windows**:
            *   Create a specific folder for it if you like (e.g., `C:\WebDriver\bin`).
            *   Add this folder to your system's `Path` environment variable:
                1.  Search for "environment variables" in the Windows search bar and select "Edit the system environment variables".
                2.  Click the "Environment Variables..." button.
                3.  Under "System variables", find the variable named `Path` and select it.
                4.  Click "Edit...".
                5.  Click "New" and add the path to the directory where you placed `chromedriver.exe` (e.g., `C:\WebDriver\bin`).
                6.  Click "OK" on all dialogs to save the changes.
            *   Alternatively, you can place `chromedriver.exe` in a directory that is already in the PATH, such as `C:\Windows\System32\` (though placing it in a dedicated WebDriver directory is often preferred for organization).

4.  **Verify Installation (Optional but Recommended)**:
    *   Open a new terminal or command prompt window (important for PATH changes to take effect).
    *   Type `chromedriver --version` and press Enter.
    *   If it's set up correctly, you should see the ChromeDriver version printed. If you get an error, double-check your PATH configuration.

## Installation (Python Packages)
Once the prerequisites are met, install the necessary Python packages:

1.  Clone this repository or download the source code.
2.  Navigate to the project directory in your terminal.
3.  Install the dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Chatbot
To run the chatbot:

1.  Ensure your terminal is in the project's root directory.
2.  Execute the main script:
    ```bash
    python chatbot.py
    ```
3.  The chatbot will greet you and prompt for your web search query. Type 'exit' or 'quit' to end the session.

## Troubleshooting
*   **`SessionNotCreatedException` or browser version mismatch errors**: This usually means the version of ChromeDriver does not match your installed Google Chrome browser version. Please re-download the correct ChromeDriver.
*   **`chromedriver` executable needs to be in PATH**: If you see this error, ensure that the directory containing the `chromedriver` executable is correctly added to your system's PATH environment variable and that you've opened a new terminal/CMD window after making PATH changes.
