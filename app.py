import streamlit as st
import requests
import json
import time
from datetime import datetime
import config
from chatbot_service import SECChatbot

# Page configuration
st.set_page_config(
    page_title="SEC Filing Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean black and white design
st.markdown("""
<style>
    /* Main app background - Pure white */
    .stApp {
        background-color: white;
    }
    
    /* Sidebar styling - Super light background */
    section[data-testid="stSidebar"] {
        background-color: #f0f0f0 !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #f0f0f0 !important;
    }
    
    section[data-testid="stSidebar"] .css-1d391kg {
        background-color: #f0f0f0 !important;
    }
    
    section[data-testid="stSidebar"] .css-1v0mbdj {
        background-color: #f0f0f0 !important;
    }
    
    /* Force all sidebar elements to be super light */
    section[data-testid="stSidebar"] * {
        background-color: #f0f0f0 !important;
    }
    
    /* Additional sidebar overrides */
    .css-1d391kg {
        background-color: #f0f0f0 !important;
    }
    
    .css-1v0mbdj {
        background-color: #f0f0f0 !important;
    }
    
    /* Nuclear option for sidebar */
    div[data-testid="stSidebar"] {
        background-color: #f0f0f0 !important;
    }
    
    div[data-testid="stSidebar"] * {
        background-color: #f0f0f0 !important;
    }
    
    /* Sidebar header - Match sidebar background */
    .sidebar-header {
        padding: 1rem;
        border-bottom: 2px solid #000000;
        margin-bottom: 1rem;
        background-color: #f0f0f0 !important;
    }
    
    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: bold;
        color: #000000;
        text-align: center;
    }
    
    /* Sidebar navigation - Clean black and white */
    .sidebar-nav {
        padding: 0.5rem 1rem;
    }
    
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        color: #000000;
        background-color: white;
        border: 1px solid #000000;
    }
    
    .nav-item:hover {
        background-color: #000000;
        color: white;
    }
    
    .nav-item.active {
        background-color: #000000;
        color: white;
    }
    
    /* Main content area - Clean white */
    .main .block-container {
        background-color: white;
        color: #000000;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #000000;
        margin: 1rem;
    }
    
    /* Headers - Pure black */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #000000;
    }
    
    /* Chat messages - Clean black and white */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #000000;
    }
    
    .user-message {
        background-color: white;
        border-left: 4px solid #000000;
        color: #000000;
    }
    
    .bot-message {
        background-color: white;
        border-left: 4px solid #000000;
        color: #000000;
        border: 2px solid #000000;
    }
    
    /* Buttons - Black and white */
    .stButton > button {
        background-color: #000000;
        color: white;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: white;
        color: #000000;
        border: 2px solid #000000;
    }
    
    /* Primary button (Send) - Match Test/Clear Chat style */
    .stButton > button[kind="primary"] {
        background-color: white !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: bold !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #000000 !important;
        color: white !important;
        border: 2px solid #000000 !important;
    }
    
    /* Example question buttons - Black and white */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: #000000;
        border: 2px solid #000000;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #000000;
        color: white;
    }
    
    /* Input fields - Clean black and white with visible cursor */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #000000;
        background-color: white;
        color: #000000;
        padding: 0.75rem;
        caret-color: #000000 !important;
    }
    
    /* Ensure cursor is visible */
    .stTextInput input {
        caret-color: #000000 !important;
    }
    
    /* Fix placeholder text color */
    .stTextInput input::placeholder {
        color: #666666 !important;
        opacity: 1;
    }
    
    /* Additional cursor fixes */
    input[type="text"] {
        caret-color: #000000 !important;
    }
    
    /* Force cursor visibility */
    .stTextInput > div > div > input:focus {
        caret-color: #000000 !important;
        outline: none;
        border: 2px solid #000000;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #000000;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div > div {
        color: #000000 !important;
        background-color: white !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #000000 !important;
        background-color: white !important;
    }
    
    /* Dropdown fix - Different approach */
    .stSelectbox {
        background-color: white !important;
    }
    
    .stSelectbox > div {
        background-color: white !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox > div > div > div > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Dropdown menu styling */
    .stSelectbox .css-1n76uvr {
        background-color: white !important;
        border: 2px solid #000000;
        border-radius: 8px;
    }
    
    .stSelectbox .css-1n76uvr > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Fix dropdown options visibility - New approach */
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] ul {
        background-color: white !important;
        border: 2px solid #000000 !important;
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] li {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] li:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Additional dropdown fixes */
    .stSelectbox .css-1n76uvr [role="listbox"] {
        background-color: white !important;
        border: 2px solid #000000 !important;
        color: #000000 !important;
    }
    
    .stSelectbox .css-1n76uvr [role="option"] {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox .css-1n76uvr [role="option"]:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Force dropdown menu visibility */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] ul {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] li {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Nuclear option - force everything white */
    .stSelectbox * {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Additional nuclear options */
    [data-baseweb="select"] {
        background-color: white !important;
        color: #000000 !important;
    }
    
    [data-baseweb="select"] * {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Text colors - Pure black */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    p, div, span {
        color: #000000 !important;
    }
    
    /* Status indicators - Black and white */
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 1rem 0;
        border: 2px solid #000000;
    }
    
    .status-success {
        background-color: white;
        color: #000000;
        border: 2px solid #000000;
    }
    
    .status-warning {
        background-color: white;
        color: #000000;
        border: 2px solid #000000;
    }
    
    /* Metrics styling */
    .metric-container {
        background-color: white;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit branding */
    .css-1rs6os {
        display: none;
    }
    
    /* Fix Streamlit's dark header bar - Make it super light gray */
    .css-1rs6os, .css-1rs6os * {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Target Streamlit's main header */
    header[data-testid="stHeader"] {
        background-color: #f0f0f0 !important;
    }
    
    header[data-testid="stHeader"] * {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Target the deploy button area */
    .css-1rs6os .css-1rs6os {
        background-color: #f0f0f0 !important;
    }
    
    /* Force all header elements to be light */
    .stApp > header {
        background-color: #f0f0f0 !important;
    }
    
    .stApp > header * {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Nuclear option for header */
    header {
        background-color: #f0f0f0 !important;
    }
    
    header * {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Make everything consistent black and white */
    .stMarkdown {
        color: #000000 !important;
    }
    
    .stMarkdown p {
        color: #000000 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg h3 {
        color: #000000 !important;
    }
    
    .css-1d391kg p {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

def simplify_response(response_text):
    """Simplify the AI response to be more concise and readable."""
    if not response_text:
        return "No response received"
    
    # If it's a JSON response, extract key information
    if "```json" in response_text:
        try:
            # Extract JSON content
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_content = response_text[json_start:json_end].strip()
            
            import json
            data = json.loads(json_content)
            
            # Create a complete response with all information
            simplified = []
            
            if 'executive_summary' in data:
                simplified.append(f"**Summary:** {data['executive_summary']}")
            
            if 'business_risks' in data and data['business_risks']:
                risks_text = ', '.join(data['business_risks'])
                simplified.append(f"**Key Risks:** {risks_text}")
            
            if 'growth_opportunities' in data and data['growth_opportunities']:
                opportunities_text = ', '.join(data['growth_opportunities'])
                simplified.append(f"**Growth Opportunities:** {opportunities_text}")
            
            if 'investment_recommendation' in data:
                simplified.append(f"**Investment Outlook:** {data['investment_recommendation']}")
            
            return "\n\n".join(simplified)
            
        except:
            # If JSON parsing fails, return original response
            pass
    
    # For non-JSON responses, return the full response
    return response_text

def call_chatbot_api(query, context=None):
    """Call the chatbot API endpoint."""
    try:
        # For local testing, use the chatbot service directly
        chatbot = SECChatbot()
        return chatbot.process_query(query, context or {})
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def display_message(message, is_user=False):
    """Display a chat message with appropriate styling."""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>SEC Bot:</strong> {message}
        </div>
        """, unsafe_allow_html=True)

def display_analysis_data(data):
    """Display structured analysis data in a nice format."""
    if not data:
        return
    
    # Company information
    if 'company' in data:
        company = data['company']
        st.markdown("### 📈 Company Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company", company.get('title', 'N/A'))
        with col2:
            st.metric("Ticker", company.get('ticker', 'N/A'))
        with col3:
            st.metric("CIK", company.get('cik', 'N/A'))
    
    # Filing information
    if 'filing' in data:
        filing = data['filing']
        st.markdown("### 📄 Filing Details")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Form Type", filing.get('form', 'N/A'))
        with col2:
            st.metric("Filing Date", filing.get('filingDate', 'N/A'))
    
    # Analysis results
    if 'analysis' in data:
        analysis = data['analysis']
        if isinstance(analysis, dict) and 'format' != 'text':
            st.markdown("### 🔍 Analysis Results")
            
            # Financial highlights
            if 'financial_highlights' in analysis:
                st.markdown("#### 💰 Financial Highlights")
                financial = analysis['financial_highlights']
                if isinstance(financial, dict):
                    for key, value in financial.items():
                        if key != 'key_metrics':
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    if 'key_metrics' in financial:
                        st.write(f"**Key Metrics:** {', '.join(financial['key_metrics'])}")
            
            # Risks and opportunities
            col1, col2 = st.columns(2)
            with col1:
                if 'business_risks' in analysis:
                    st.markdown("#### ⚠️ Key Risks")
                    for risk in analysis['business_risks'][:3]:
                        st.write(f"• {risk}")
            
            with col2:
                if 'growth_opportunities' in analysis:
                    st.markdown("#### 🚀 Growth Opportunities")
                    for opp in analysis['growth_opportunities'][:3]:
                        st.write(f"• {opp}")
            
            # Investment recommendation
            if 'investment_recommendation' in analysis:
                st.markdown("#### 💡 Investment Outlook")
                st.info(analysis['investment_recommendation'])
            
            # Confidence score
            if 'confidence_score' in analysis:
                st.markdown(f"**Analysis Confidence:** {analysis['confidence_score']}%")

def main():
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'context' not in st.session_state:
        st.session_state.context = {}
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""
    if 'last_response_time' not in st.session_state:
        st.session_state.last_response_time = 0
    if 'last_response_content' not in st.session_state:
        st.session_state.last_response_content = ""
    if 'response_count' not in st.session_state:
        st.session_state.response_count = 0
    if 'stopped' not in st.session_state:
        st.session_state.stopped = False
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><div class="sidebar-logo">📊 SEC Bot</div></div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### Navigation")
        nav_options = ["Home", "Analysis", "History", "Settings"]
        selected_nav = st.selectbox("", nav_options, index=0, label_visibility="collapsed")
        
        st.markdown("---")
        
        # Example Questions
        st.markdown("### 💡 Example Questions")
        example_questions = [
            "Analyze Apple Inc's latest 10-K",
            "What are Tesla's main business risks?",
            "Compare Microsoft and Google's revenue",
            "Summarize Amazon's financial performance",
            "Find companies in the tech sector",
            "What is NVIDIA's growth strategy?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}", use_container_width=True):
                st.session_state.chat_input = question
                st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        st.metric("Questions Asked", st.session_state.response_count)
        st.metric("Messages", len(st.session_state.messages))
        
        # Status
        st.markdown("### 🔧 Status")
        try:
            chatbot = SECChatbot()
            if chatbot.llm_analyzer:
                st.markdown('<div class="status-indicator status-success">✅ AI Active</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-indicator status-warning">⚠️ Demo Mode</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown('<div class="status-indicator status-warning">❌ Error</div>', unsafe_allow_html=True)
    
    # Main content area
    st.markdown('<h1 class="main-header">📊 SEC Filing Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Analysis of SEC 10-K and 10-Q Filings")
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(message['content'], message['is_user'])
    
    # Chat input
    user_input = st.text_input(
        "Ask me about SEC filings...",
        value="" if st.session_state.clear_input else st.session_state.get('chat_input', ''),
        key="chat_input",
        placeholder="Try: 'Analyze Apple Inc's latest 10-K' or 'What are Tesla's main business risks?' or 'Compare Microsoft and Google's revenue'"
    )
    
    # Reset clear_input flag after using it
    if st.session_state.clear_input:
        st.session_state.clear_input = False
    
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        send_button = st.button("Send", type="primary", disabled=st.session_state.processing)
    with col_btn2:
        test_button = st.button("Test", disabled=st.session_state.processing)
    with col_btn3:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.context = {}
            st.session_state.processing = False
            st.session_state.last_query = ""
            st.session_state.last_response_time = 0
            st.session_state.last_response_content = ""
            st.session_state.response_count = 0
            st.session_state.clear_input = True
            st.rerun()
    
    # Process test button
    if test_button:
        user_input = "Search for Apple Inc"
    
    # Process user input - only if not already processing and not duplicate query
    if (send_button and user_input) or test_button:
        import time
        current_time = time.time()
        
        # Check if this is a duplicate query within 5 seconds
        is_duplicate = (user_input == st.session_state.last_query and 
                       current_time - st.session_state.last_response_time < 5)
        
        if not st.session_state.processing and not is_duplicate:
            # Set processing state immediately
            st.session_state.processing = True
            st.session_state.last_query = user_input
            
            # Add user message to history
            st.session_state.messages.append({
                'content': user_input,
                'is_user': True,
                'timestamp': datetime.now()
            })
            
            # Show loading spinner with nice message and delay
            with st.spinner("🤖 Analyzing SEC filing..."):
                try:
                    # Add a small delay to make it feel more realistic
                    time.sleep(2)  # 2 second delay for better UX
                    
                    # Call chatbot API
                    response = call_chatbot_api(user_input, st.session_state.context)
                    
                except Exception as e:
                    response = {"error": f"Failed to process query: {str(e)}"}
            
            # Simplify bot response
            if response.get('error'):
                bot_message = f"❌ Error: {response['error']}"
            else:
                bot_message = simplify_response(response.get('response', 'No response received'))
            
            # Check if this response is the same as the last one
            if bot_message == st.session_state.last_response_content:
                # Same response - don't add it, just stop
                st.session_state.processing = False
                st.session_state.last_response_time = current_time
                
                # Clear the input textbox
                st.session_state.clear_input = True
                
                st.rerun()
                return
            
            # Add bot response to history
            st.session_state.messages.append({
                'content': bot_message,
                'is_user': False,
                'timestamp': datetime.now()
            })
            
            # Add a prompt for the next question
            next_question_prompt = "\n\n---\n\n**💬 Ready for your next question!** Ask me anything about SEC filings, company analysis, or financial data."
            st.session_state.messages.append({
                'content': next_question_prompt,
                'is_user': False,
                'timestamp': datetime.now()
            })
            
            # Update context for follow-up questions
            if 'data' in response:
                st.session_state.context.update(response['data'])
            
            # Reset processing state and update timing
            st.session_state.processing = False
            st.session_state.last_response_time = current_time
            st.session_state.last_response_content = bot_message
            st.session_state.response_count += 1
            
            # Clear the input textbox
            st.session_state.clear_input = True
            
            # Complete stop - rerun to show final state
            st.rerun()

if __name__ == "__main__":
    main()
