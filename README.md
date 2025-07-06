# Syncoria Odoo Assistant

An intelligent AI-powered business data analysis assistant built with Streamlit. This application provides a ChatGPT-like interface for analyzing business data, generating insights, and creating visualizations specifically designed for Odoo users.

![Syncoria Logo](images/logo.png)

## 🚀 Features

### Core Functionality
- **Interactive Chat Interface**: Modern, ChatGPT-inspired UI with real-time conversations
- **Business Data Analysis**: Analyze your Odoo business data with natural language queries
- **Chart Generation**: Automatically creates visualizations based on your data requests
- **Session Management**: Multiple chat sessions with persistent conversation history
- **Real-time Responses**: Stream responses with thinking indicators for better user experience

### User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Theme**: Professional color scheme with Syncoria branding
- **Chat History**: Persistent conversation history across sessions
- **Session Switching**: Easy navigation between different chat sessions
- **Markdown Support**: Rich text formatting including code blocks, lists, and links

### Technical Features
- **API Integration**: Connects to backend AI service for data processing
- **Chart Display**: Integrated chart viewing with S3 cloud storage
- **Error Handling**: Graceful error handling and user feedback
- **Session Persistence**: Automatic session creation and management
- **Optimized Performance**: Efficient message handling and UI updates

## 📋 Prerequisites

- Python 3.7+
- pip package manager
- Active internet connection for API calls
- Access to Syncoria API endpoint

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd syncoria-assistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify required files:**
   - Ensure `images/logo.png` exists in the project directory
   - Check that `app.py` is in the root directory

## 🚀 Usage

### Starting the Application

1. **Run the Streamlit app:**
```bash
streamlit run app.py
```

2. **Open your browser:**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

### Using the Assistant

1. **New Chat Session:**
   - Click "➕ New Chat" to start a new conversation
   - Each session maintains its own conversation history

2. **Asking Questions:**
   - Type your business data questions in the input box
   - Examples:
     - "Show me sales trends for the last quarter"
     - "What are our top-performing products?"
     - "Generate a revenue analysis chart"

3. **Viewing Results:**
   - Responses appear in chat bubbles with timestamps
   - Charts are automatically generated and displayed when relevant
   - Click on generated charts to view them in full size

4. **Session Management:**
   - Switch between sessions using the sidebar
   - Session titles are automatically generated from first query
   - Chat history is preserved across sessions



### Available Endpoints
- `GET /session` - Create new chat session
- `POST /history` - Retrieve chat history
- `POST /query` - Send user queries for analysis

## 🎨 Customization

### Styling
The application uses extensive CSS customization for:
- ChatGPT-like interface design
- Responsive layout
- Professional color scheme
- Smooth animations and transitions

### Branding
- Logo: `images/logo.png`
- Color scheme: Purple/violet theme (#875A7B, #A0729A)
- Typography: Modern, readable fonts



## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Requests**: HTTP library for API calls
- **JSON**: Data parsing and handling
- **DateTime**: Timestamp management
- **UUID**: Session ID generation

### Key Functions
- `create_new_session()`: Initializes new chat sessions
- `get_chat_history()`: Retrieves conversation history
- `send_query()`: Sends user queries to AI backend
- `process_markdown()`: Converts markdown to HTML
- `format_timestamp()`: Formats timestamps for display

### State Management
- Session state maintains chat history, current session, and user sessions
- Automatic session creation on app startup
- Persistent conversation history across browser sessions

## 🌐 API Integration

The application integrates with the Syncoria backend API to:
- Process natural language queries
- Generate business insights
- Create data visualizations
- Manage chat sessions
- Store conversation history

### Request Format
```json
{
  "query": "user question",
  "session_id": "unique_session_id",
  "include_debug": false
}
```

### Response Format
```json
{
  "analysis": "AI response text",
  "chart_generated": true/false,
  "chart_s3_url": "chart_image_url",
  "chart_decision_reason": "explanation",
  "timestamp": "ISO_timestamp"
}
```

## 🔍 Features in Detail

### Chart Generation
- Automatically determines when visualizations would be helpful
- Generates charts using backend AI service
- Displays charts with explanations
- Stores charts in S3 for persistent access

### Session Management
- Unique session IDs for each conversation
- Automatic session creation
- Session history in sidebar
- Easy switching between conversations

### Message Processing
- Markdown support for rich text
- Code syntax highlighting
- Link handling
- List formatting
- Timestamp display

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Error:**
   - Check internet connection
   - Verify API endpoint is accessible
   - Ensure API service is running

2. **Chart Not Loading:**
   - Check S3 URL accessibility
   - Verify chart generation was successful
   - Try refreshing the page

3. **Session Not Creating:**
   - Clear browser cache
   - Restart the application
   - Check API endpoint status
