# Voice Assistant for FM-Clinic

A **voice-enabled AI assistant** for booking doctor appointments seamlessly. This project leverages advanced **speech-to-text**, **text-to-speech**, and **large language models (LLMs)** to provide an intuitive and efficient interaction experience.

---

## 🌟 Features

- **Speech-to-Text (STT):**
  - Supports **Whisper Streaming** and **AWS Transcribe** for real-time transcription.
  - Optional **Deepgram** integration for prerecorded audio.
  - Multilingual support: **English** and **Arabic**.
  - Real-time partial transcription display.

- **Text-to-Speech (TTS):**
  - Uses **AWS Polly** for natural-sounding responses in **English** and **Arabic**.
  - Automatically detects language from the user's speech.

- **AI-Powered Conversation:**
  - Powered by **GROQ** and **OpenAI** for natural, contextual conversations.
  - Handles complex interactions like:
    - Collecting patient details.
    - Providing clinic locations and doctor specialties.
    - Suggesting and booking appointments.

- **Customizable UI:**
  - Built with **Streamlit**.
  - Beautiful, responsive, and intuitive interface.
  - Sidebar for configuration (language selection, session management).
  - Debug mode to view intermediate steps and tool usage.

- **Extensible Tools:**
  - Integration with MongoDB to manage:
    - Patients.
    - Doctors and their schedules.
    - Appointments.

---

## 🛠️ Tech Stack

### Core Technologies
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **Database**: MongoDB
- **LLM**: [GROQ](https://www.groq.com/) and [OpenAI GPT](https://openai.com/)
- **Speech Processing**:
  - Whisper (via [FasterWhisperASR](https://github.com/ufal/whisper_streaming))
  - AWS Transcribe
  - Deepgram (prerecorded audio)
- **Text-to-Speech**: AWS Polly

### Libraries & Frameworks
- **LangChain**: Manages conversation flows and tool integrations.
- **LangSmith**: Manages tracing and debugging for LLMs.
- **Boto3**: AWS SDK for Python.
- **Librosa** & **SoundDevice**: For audio processing.
- **Pymongo**: MongoDB integration.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.10+**
2. **MongoDB** (Ensure you have a running instance)
3. **AWS Polly and Transcribe** credentials.
4. **GROQ** or **OpenAI API keys**.
5. **Deepgram API Key** (optional, for prerecorded audio).

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Fatma-Moanes/voice-assistant.git
   cd voice-assistant
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`.
   - Fill in your API keys and MongoDB credentials.

4. **Create and seed the database:**
   ```bash
   python utils/create_db.py
   ```

5. **Run the application:**
   ```bash
   poetry run streamlit run app/streamlit_app_streaming.py
   ```

---

## 🧰 Configuration

All configurations are managed in `config.yml`. Key sections include:
- **Speech-to-Text**: Configure STT models (`WhisperStreaming`, `AWSStreaming`).
- **LLM**: Choose between **GROQ** and **OpenAI**.
- **Text-to-Speech**: Configure AWS Polly voices and languages.

---

## 🌐 API Keys and Environment Variables

Set the following in your `.env` file:
NOTE: You can use the `.env.example` file as a template.

```dotenv
# MongoDB
MONGODB_CONNECTION_STRING="your_connection_string"
DB_NAME="DoctorAppointmentDB"

# GROQ API
GROQ_API_KEY="your_groq_api_key"

# OpenAI API
OPENAI_API_KEY="your_openai_api_key"

# AWS Polly & Transcribe
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_key"

# Deepgram API (optional)
DEEPGRAM_API_KEY="your_deepgram_api_key"
```

---

## 🎨 UI Features

- **Interactive Chat Display**:
  - Chat bubbles for user and assistant messages.
  - Separate sections for error messages and debug information.

- **Audio Recording**:
  - Supports real-time and prerecorded audio inputs.
  - Partial transcription visible during recording.

- **Debug Mode**:
  - Displays:
    - Intermediate steps (tool calls).
    - Processed chat history used by the AI agent.

---

## ✨ Completed Milestones

- [x] Error handling for empty transcription.
- [x] Streamlined UI/UX improvements.
- [x] Language-specific transcription and response.
- [x] Streaming input and output.
- [x] Configurable STT and LLM integrations.
- [x] Debug mode for the LLM.
- [x] LangSmith Tracing.

---


## 🙋‍♂️ Support

If you encounter issues, please open an [issue](https://github.com/Fatma-Moanes/voice-assistant/issues)