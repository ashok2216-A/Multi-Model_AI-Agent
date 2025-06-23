# PDF Chatbot FastAPI with Mistral AI

This project is an intelligent chatbot system that allows users to interact with the content of PDF documents using natural language. It leverages Mistral AI for both text-based chat and vision (image) analysis, providing context-aware answers and displaying relevant images from the PDF. The system also supports custom agents for advanced document reasoning and tool use.

## Key Features

- **PDF Text & Image Extraction:** Extracts both text and images from uploaded PDF files, mapping images to their nearby text for context.
- **AI-Powered Chat:** Uses Mistral AI to answer user questions about the PDF, referencing both text and images.
- **Image-Text Mapping:** Associates each extracted image with the most relevant nearby text, enabling image retrieval based on user queries.
- **Vision AI Integration:** Analyzes images using Mistral's vision API to provide descriptions or answer questions about images.
- **Semantic Search:** Uses Mistral embeddings for advanced semantic search and context retrieval.
- **Hybrid Search Algorithm:** Combines text similarity, semantic similarity, and image metadata for accurate image relevance.
- **Custom Agents:** Integrates custom agents and tools for enhanced document reasoning, search, and automation.
- **Modern UI:** Streamlit frontend for easy PDF upload, chat, and image exploration.

## System Architecture

- **Frontend:** Streamlit app for PDF upload, chat, and image display.
- **Backend:** FastAPI server for handling API requests, PDF processing, and Mistral AI integration.
- **AI Integration:** Mistral API for chat, embeddings, and vision analysis.
- **Agents:** Custom agents and tools for advanced document tasks (see `custom_agents/`).

## About Agents

Agents in this project are intelligent components that can use a variety of tools to enhance the chatbot's capabilities. They can:
- Perform advanced reasoning over PDF content
- Use external tools (e.g., Wikipedia search, translation, web search)
- Chain multiple actions to answer complex queries
- Automate document-related tasks

Agents are implemented in the `custom_agents/` directory:
- `agent.py`: Contains the logic for agent behavior, decision-making, and tool selection
- `tools.py`: Implements the actual tools that agents can use (e.g., search, translation)

**Example Use Cases:**
- "Translate the summary on page 2 to French."
- "Find recent Wikipedia information about a topic mentioned in the PDF."
- "Summarize all images related to 'machine learning' in this document."

Agents make the chatbot more flexible and powerful, allowing it to go beyond simple Q&A and perform multi-step, tool-augmented reasoning.

## How It Works

1. **Upload PDF:** User uploads a PDF via the Streamlit interface.
2. **Extraction:** The backend extracts all text and images, mapping each image to its nearby text.
3. **Embedding:** Text and image contexts are embedded using Mistral's embedding API for semantic search.
4. **Chat:** User asks questions; the system retrieves relevant context and images, then queries Mistral AI for an answer.
5. **Image Display:** If the answer references an image, it is displayed alongside the response. Users can also request vision analysis of any image.
6. **Agents:** For advanced queries, custom agents can use tools (e.g., search, translation, Wikipedia) to enhance responses.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pdf_chatbot_fastapi
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Unix/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Create a `.env` file in the root directory
   - Add your Mistral API key:
     ```env
     MISTRAL_API_KEY=your_api_key_here
     ```

## Running the Application

1. **Start the FastAPI backend:**
   ```bash
   uvicorn api:app --reload --port 8000
   ```
2. **Start the Streamlit frontend (in a new terminal):**
   ```bash
   streamlit run frontend.py
   ```
3. **Access the app:**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Usage

- **Upload a PDF** to begin.
- **Ask questions** about the document in natural language.
- **View relevant images** and their context in the chat.
- **Click images** for vision-based analysis.
- **Use agent-powered tools** for advanced document queries (e.g., translation, Wikipedia search).

## Project Structure

```
pdf_chatbot_fastapi/
├── api.py            # FastAPI backend
├── frontend.py       # Streamlit UI
├── utils.py          # Utility functions
├── custom_agents/    # Custom AI agents/tools
│   ├── agent.py      # Agent logic
│   └── tools.py      # Tool implementations
├── src/              # Source files (PDFs, images, etc.)
├── requirements.txt  # Dependencies
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

## Acknowledgments

- Mistral AI for chat and vision APIs
- FastAPI and Streamlit for the framework
- All contributors and maintainers
- Open-source libraries and agent tool providers
