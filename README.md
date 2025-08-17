# --RecallAI--
An AI Chatbot which can simulate memory using technology like semantic searching using python and Openai API

# features:
1. Memory-Based Chat 🧠
  Stores chat history in SQLite (chatbot_memory.db).
  Stores vector embeddings of messages in ChromaDB, enabling retrieval of prominent message chunks for context-aware replies.
  Uses SentenceTransformer for embeddings, so it remembers semantic meaning, not just literal text.
2. Contextual AI Responses 🤖
  Uses an AI model (deepseek/deepseek-r1-0528:free by default) to generate responses.
  Incorporates recent chat history + prominent memory snippets to give smarter, coherent replies.
  Adjustable temperature for response creativity.
3. Advanced Memory Management 💾
  Can export and import chats + memory database.
  Can delete all chats/memories safely (with confirmation).
  Automatic chunking of messages for embeddings (chunk_size + chunk_overlap).
4. Interactive GUI 🖥️
  Built with DearPyGUI and uses Tkinter for screen info and file dialogs.
  Split layout: chat window + settings panel.
  Supports scrolling, send button, customizable appearance, themes, and fonts.
5. Customizable Settings Panel ⚙️
  Change number of prominent message chunks to retrieve.
  Adjust chunk size and overlap for memory embeddings.
  Configure max length of chat history considered for context.
  Switch AI model or change temperature.
6. Time-Stamped Messages ⏰
  Each message stored in the database is timestamped and displayed in the GUI.
7. Export / Import 📂
  Export SQLite + ChromaDB folder for backups.
  Import previous backup safely into the app.
8. User-Friendly Experience 😎
  Automatic scroll, alternating chat colors, nicely formatted timestamps.
  Pop-ups for deletion confirmation and import confirmation.

# Installation
1. clone the repository
  git clone https://github.com/your-username/your-repo.git
2. Go to project folder
  cd your-repo
3. Create virtual environment (optional but recommended)
  python -m venv venv
  source venv/bin/activate   # On Windows: venv\Scripts\activate
4. Install dependencies
  pip install -r requirements.txt

# How to use?
1. run the type2.py
  python type2.py
  or
  python3 type2.py
2. wail for few seconds the gui will pop up after connecting to database and openai client
3. continue using it in the UI
   <img width="1923" height="1203" alt="image" src="https://github.com/user-attachments/assets/00faa8ba-167a-43e2-b438-1d71ecc0e004" />
   https://github.com/user-attachments/assets/39280c96-4737-4749-a90d-a322785de4bb

# Project Structure
your-repo/
├── type2.py                 # Main chatbot program
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── chatbot_memory.db        # SQLite database for chat history (auto-created if not found)
├── db/                      # ChromaDB folder (auto-created if not found)
│   └── chroma.sqlite3       # Chroma vector database
└── importhelp.py            # Helper script for importing data

# Tech Stack
1. Python
2. LangChain
3. OpenAI API
4. SQLite
5. dearpygui
6. Tkinter
7. chromadb

# To-Do / Future Improvements
Message Controls:
   Max messages to consider (slider) — control how many previous messages the AI looks at.✅
   Summarization toggle — turn on/off summarizing long chat history.
   Summarization length — slider or dropdown (short/medium/long summary).
   Tag-based filtering toggle — filter memory recall by tags only.
   Date range filter — pick date/time range of messages AI should recall.
AI Behavior Controls:
   Creativity slider (temperature) — control randomness in AI responses.✅
   Response length slider — how long the AI replies (short, medium, long).
   Model selector dropdown — switch between Mistral, Gemini, DeepSeek, etc.✅
   Enable “Mega Mind Memory” toggle — the big memory mode you mentioned.
User Experience Toggles:
   Chat bubble style toggle — switch between left/right bubbles or single side with colors.
   Auto-scroll toggle — turn auto scroll on or off.
   Show timestamps toggle — show/hide message timestamps.✅
   Font size slider — for accessibility.
Debugging / Advanced Options:
   Show raw tags toggle — for debugging what tags AI uses.
   Enable logging toggle — save logs locally for testing.
   Reset conversation button — clear chat memory (with confirmation popup).✅
   Export chat history — save as .txt or JSON.✅
Voice & Input (Future-ready):
   Enable voice input toggle
   Enable speech output toggle
   Fun Extras:
   Theme selector — light, dark, or custom colors.
   “Jarvis Mode” toggle — extra fancy AI responses with personality.
   Easter egg button — trigger some quirky AI behavior or joke.

# Contributing
Pull requests are welcome.

# License
MIT
