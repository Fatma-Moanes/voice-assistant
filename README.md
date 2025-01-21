# Voice Assistant for a Clinic

🎙️ A *bilingual, AI-powered voice assistant** designed to simplify doctor appointment bookings at a Clinic. This solution combines **speech-to-text (STT)**, **text-to-speech (TTS)**, and **large language models (LLMs)** to deliver intuitive and efficient interactions.


---

## 🌟 Key Features

### 🗣️ Speech-to-Text (STT)
- **Real-Time Transcription**:
  - Powered by **Whisper Streaming** and **AWS Transcribe**.
  - Supports **Deepgram** for prerecorded audio files.
  - Multilingual capability: **English** and **Arabic**.
  - Real-time **partial transcription** for better interactivity.
  
### 🔊 Text-to-Speech (TTS)
- Natural voice responses using **AWS Polly**.
- Supports high-quality voices for both **English** and **Arabic**.

### 🤖 AI-Powered Conversations
- **Context-Aware Dialogues**:
    A ReAct LLM agent that can:
  - Collect patient details like name, age, and insurance status.
  - Suggest available clinic locations and doctor specialties.
  - Schedule and book appointments with MongoDB integration.
- Powered by **GROQ** or **OpenAI GPT**, offering flexible LLM backends.

### 🎨 Intuitive User Interface
- Built with **Streamlit** for a clean and responsive design.
- Sidebar for language selection and session management.
- Real-time chat display with user-friendly message bubbles.
- **Debug Mode**:
  - View intermediate tool outputs and chat history.
  - Separate debug panel for tracing.

### 📊 Data Integration
- **MongoDB** as the database for managing:
  - Patient records.
  - Doctor information (schedules, specialties, locations).
  - Appointment bookings.
- Ready-to-use database seeding script with dummy data for testing.

---

## 🛠️ Tech Stack

### Core Components
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **Database**: MongoDB
- **LLM**: [GROQ](https://www.groq.com/) or [OpenAI GPT](https://openai.com/)
- **Speech Processing**:
  - **Whisper** [WhisperStreaming](https://github.com/ufal/whisper_streaming)
  - AWS Transcribe
  - Deepgram (prerecorded audio)
- **Text-to-Speech**: AWS Polly

### Libraries & Tools
- **LangChain**: Manages LLM conversation workflows and tools.
- **LangSmith**: For tracing and debugging LLMs.
- **Boto3**: AWS SDK for Polly and Transcribe integrations.
- **Librosa** & **SoundDevice**: Audio handling and preprocessing.
- **Pymongo**: MongoDB integration.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.10+**
2. **MongoDB** (Ensure it’s running locally or on the cloud).
3. **API Keys**:
   - **AWS Polly & Transcribe** (or use Whisper Streaming).
   - **GROQ** or **OpenAI**
   - **Deepgram** (optional for prerecorded audio).

---

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Fatma-Moanes/voice-assistant.git
   cd voice-assistant
   ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Set Up Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Fill in your API keys and database credentials in the `.env` file.

4. **Seed the Database**:
   Populate the database with dummy data:
   ```bash
   python utils/create_db.py
   ```

5. **Run the Application**:
   Start the Streamlit app for live audio:
   ```bash
   poetry run streamlit run app/streamlit_app_streaming.py
   ```

---

## 🎨 UI Overview

### Chat Interface
- **Dynamic Conversation**: User and assistant messages are displayed in visually distinct bubbles.
- **Audio Input**:
  - Live microphone recording.
- **Error Handling**:
  - Clear notifications for failed transcription or processing.

### Sidebar Settings
- **Language Selection**:
  - Choose between **English**, **Arabic**, or **Auto Detect**.
- **Session Controls**:
  - Clear chat history.
  - Toggle Debug Mode.

### Debug Panel
- Real-time insight into:
  - Chat history used by the LLM.
  - Intermediate tool calls and responses.

---

## 🧰 Configuration

All application settings are managed through:
1. **`config.yml`**:
   - **Speech-to-Text** model selection (`WhisperStreaming`, `AWSStreaming`, or `Deepgram`).
   - Language preferences and model-specific configurations.
   - **Text-to-Speech** (AWS Polly voices and region).
   - **LLM** provider (GROQ or OpenAI).

2. **`.env`**:
   - Store sensitive credentials such as API keys and database connection strings.  Use `.env.example` as a template.

---

## 🌐 Environment Variables

Below is a summary of required `.env` variables:

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

## ✅ Completed Milestones

- **Speech-to-Text Enhancements**:
  - Real-time and partial transcription.
  - Improved error handling for silent inputs.
- **Streamlined Conversations**:
  - Context-aware doctor booking logic.
  - Integration with MongoDB for data persistence.
- **Debug Mode**:
  - Displays:
    - Intermediate steps (tool calls).
    - Processed chat history used by the AI agent.
- **Extensible Configuration**:
  - Support for multiple STT and LLM models.


---

## ✨ Acknowledgments

- **LangChain** for managing LLM integrations.
- **Amazon Polly** for high-quality voice synthesis.
- **Whisper Streaming** and **Deepgram** for advanced transcription.
- **Streamlit** for the responsive and interactive UI.
- **GROQ** and **OpenAI GPT** for powering the conversational AI.

---

## 💬 Support

If you have any questions or encounter issues, feel free to open an [issue](https://github.com/Fatma-Moanes/voice-assistant/issues) or reach out via email at fmoanesnoureldin@gmail.com

---
Enjoy using the **Voice Assistant for FM-Clinic**! 🚀
