# Article Summarizer

This is a Streamlit-based web application that uses Google's Gemini AI to summarize articles. Users can input any article, adjust the AI's temperature setting, and receive a concise summary.

## Features

- Article input via text area
- Adjustable AI temperature for controlling creativity
- One-click summary generation
- Reset functionality
- Export option for saving conversations

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/article-summarizer.git
   cd article-summarizer
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google Gemini API key:
   - Go to the Google AI Studio (https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Replace the `GOOGLE_API_KEY` value in `main.py` with your actual API key

## Usage

To run the application:

1. Open a terminal and navigate to the project directory.

2. Run the following command:
   ```
   streamlit run main.py
   ```

3. Your default web browser should open automatically with the application. If not, you can manually open a browser and go to the URL shown in the terminal (usually `http://localhost:8501`).

4. Use the application by following these steps:
   - Paste your article into the text area
   - Adjust the temperature slider if desired
   - Click "Generate Summary" to get your summary
   - Use "Reset" to clear the input and output
   - Click "Export" to save your conversation

## Contributing

Contributions to this project are welcome. Please feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions or feedback, please contact [Your Name] at [your.email@example.com].