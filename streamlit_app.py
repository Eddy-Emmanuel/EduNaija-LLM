import os
import streamlit as st
from datetime import datetime
from openai import OpenAI
from app.agents.multiagent import agent
from app.agents.rag import set_pdf_path
from app.configurations.accesskeys import accesskeys_config
import base64

# Page configuration
st.set_page_config(
    page_title="EduNaija AI Tutor",
    page_icon="📚",
    layout="wide"
)

st.title("📚 EduNaija AI Tutor")
st.write("Ask questions in Yoruba, Hausa, Igbo, or English.")

# Set API key
os.environ["OPENAI_API_KEY"] = accesskeys_config.OPENAI_API_KEY
client = OpenAI(api_key=accesskeys_config.OPENAI_API_KEY)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_path" not in st.session_state:
    st.session_state.temp_path = None
if "temp_image_path" not in st.session_state:
    st.session_state.temp_image_path = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None

# Language configuration
LANGUAGES = {
    "English": "en",
    "Yoruba": "yo",
    "Hausa": "ha",
    "Igbo": "ig"
}

# UI Text translations
TRANSLATIONS = {
    "placeholder": {
        "en": "Type your question here...",
        "yo": "Kọ ìbéèrè rẹ síbí...",
        "ha": "Rubuta tambayarka a nan...",
        "ig": "Dee ajụjụ gị ebe a..."
    },
    "button": {
        "en": "Get Response",
        "yo": "Gba Ìdáhùn",
        "ha": "Sami Amsa",
        "ig": "Nweta Nzaghachi"
    },
    "response_label": {
        "en": "Agent Response:",
        "yo": "Ìdáhùn Agenti:",
        "ha": "Amsar Wakili:",
        "ig": "Nzaghachi Onye Nnọchiteanya:"
    },
    "no_answer": {
        "en": "No answer returned",
        "yo": "Kò sí ìdáhùn tí ó padà",
        "ha": "Babu amsar da aka dawo",
        "ig": "Enweghị nzaghachi alọghachiri"
    },
    "error": {
        "en": "Error getting response",
        "yo": "Àṣìṣe nínú gbígba ìdáhùn",
        "ha": "Kuskure wajen samun amsa",
        "ig": "Njehie n'inweta nzaghachi"
    },
    "upload_success": {
        "en": "PDF uploaded successfully!",
        "yo": "PDF ti gba àṣeyọrí!",
        "ha": "An loda PDF cikin nasara!",
        "ig": "Ebulitere PDF nke ọma!"
    },
    "image_upload_success": {
        "en": "Image uploaded successfully! Extracting content...",
        "yo": "Àwòrán ti gba àṣeyọrí! Ń yọ àkóónú jáde...",
        "ha": "An loda hoto cikin nasara! Ana ciro abun ciki...",
        "ig": "Ebulitere foto nke ọma! Na-ewepụta ọdịnaya..."
    },
    "extracting_text": {
        "en": "Analyzing image content...",
        "yo": "Ń ṣe ìtúpalẹ̀ àkóónú àwòrán...",
        "ha": "Ana nazarin abun cikin hoto...",
        "ig": "Na-enyocha ọdịnaya foto..."
    },
    "extraction_complete": {
        "en": "Content extracted successfully!",
        "yo": "Àkóónú ti yọ jáde pẹ̀lú àṣeyọrí!",
        "ha": "An ciro abun ciki cikin nasara!",
        "ig": "Ewepụtara ọdịnaya nke ọma!"
    },
    "no_text_found": {
        "en": "No content found in image",
        "yo": "Kò sí àkóónú tí a rí nínú àwòrán",
        "ha": "Ba a sami abun ciki a cikin hoto ba",
        "ig": "Enweghị ọdịnaya achọtara na foto"
    },
    "clear_chat": {
        "en": "Clear Chat History",
        "yo": "Pa Ìtàn Ìfọ̀rọ̀wérọ̀ Rẹ́",
        "ha": "Share Tarihin Hira",
        "ig": "Hichapụ Akụkọ Mkparịta Ụka"
    }
}

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def cleanup_temp_files():
    """Clean up temporary files"""
    import os
    if st.session_state.temp_path and os.path.exists(st.session_state.temp_path):
        try:
            os.remove(st.session_state.temp_path)
        except:
            pass
    if st.session_state.temp_image_path and os.path.exists(st.session_state.temp_image_path):
        try:
            os.remove(st.session_state.temp_image_path)
        except:
            pass
    st.session_state.temp_path = None
    st.session_state.temp_image_path = None
    st.session_state.extracted_text = None

def extract_content_from_image(image_path):
    """Extract content from image using OpenAI Vision API"""
    try:
        # Convert image to base64
        image_base64 = encode_image_to_base64(image_path)
        
        # Determine image mime type based on file extension
        extension = image_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
        mime_type = mime_types.get(extension, 'image/jpeg')
        
        # Create data URL with base64 encoded image
        data_url = f"data:{mime_type};base64,{image_base64}"
        
        response = client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Please extract and describe all text, diagrams, charts, formulas, and any educational content from this image. Provide a detailed description of everything visible in the image that could be relevant for answering questions about it."
                        },
                        {
                            "type": "input_image",
                            "image_url": data_url
                        }
                    ]
                }
            ]
        )
        
        return response.output_text
    except Exception as e:
        st.error(f"Error extracting content from image: {str(e)}")
        return None

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    selected_language = st.selectbox(
        "Select your language / Yan zaɓin harshenku / Yan họrọ asụsụ gị / Yan fẹ́ èdè rẹ:",
        list(LANGUAGES.keys())
    )
    
    language_code = LANGUAGES[selected_language]
    
    st.divider()
    
    # PDF Upload
    st.subheader("📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a PDF for context-based questions", 
        type="pdf",
        help="Upload educational materials for RAG-based questioning"
    )
    
    if uploaded_file:
        # Create temp file with proper cleanup
        import tempfile
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_pdf.write(uploaded_file.getbuffer())
        temp_pdf.close()
        
        st.session_state.temp_path = temp_pdf.name
        set_pdf_path(temp_pdf.name)
        st.success(TRANSLATIONS["upload_success"].get(language_code, "PDF uploaded successfully!"))
    
    st.divider()
    
    # Image Upload
    st.subheader("🖼️ Upload Image")
    uploaded_image = st.file_uploader(
        "Upload an image for visual questions",
        type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
        help="Upload diagrams, charts, textbooks, or educational images. AI will extract and analyze the content."
    )
    
    if uploaded_image:
        # Create temp file with proper cleanup
        import tempfile
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_image.type.split('/')[-1]}")
        temp_img.write(uploaded_image.getbuffer())
        temp_img.close()
        
        st.session_state.temp_image_path = temp_img.name
        
        # Display the uploaded image
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        
        # Extract content from image using OpenAI Vision
        with st.spinner(TRANSLATIONS["extracting_text"].get(language_code, "Analyzing image content...")):
            extracted_content = extract_content_from_image(temp_img.name)
            st.session_state.extracted_text = extracted_content
            
            if extracted_content:
                st.success(TRANSLATIONS["extraction_complete"].get(language_code, "Content extracted successfully!"))
                
                # Show extracted content in an expander
                with st.expander("📝 Extracted Content Preview"):
                    st.text_area(
                        "Content from image:",
                        value=extracted_content,
                        height=200,
                        disabled=True
                    )
            else:
                st.warning(TRANSLATIONS["no_text_found"].get(language_code, "No content found in image"))
    
    st.divider()
    
    # Clear chat button
    if st.button(TRANSLATIONS["clear_chat"].get(language_code, "Clear Chat History")):
        st.session_state.messages = []
        # Clean up temp files
        cleanup_temp_files()
        st.rerun()
    
    # Display chat count
    st.caption(f"Messages: {len(st.session_state.messages)}")

# Main chat interface
st.subheader("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display image if present in message
        if "image_path" in message:
            st.image(message["image_path"], caption="Reference Image", width=300)

# Chat input
user_input = st.chat_input(
    TRANSLATIONS["placeholder"].get(language_code, "Type your question here...")
)

# Process user input
if user_input:
    # Add user message to chat history
    user_message = {"role": "user", "content": user_input}
    if st.session_state.temp_image_path:
        user_message["image_path"] = st.session_state.temp_image_path
    st.session_state.messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
        if st.session_state.temp_image_path:
            st.image(st.session_state.temp_image_path, caption="Reference Image", width=300)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Build the query with context
            query_with_context = (
                f"[Your Name: EduNaija AI Tutor] "
                f"[Your Creator: Eddy and Israel Odeajo] "
                f"[Selected Response Language: {selected_language}] "
                f"[Current time: {datetime.now().isoformat()}] "
            )
            
            # Add PDF context if available
            if st.session_state.temp_path:
                query_with_context += "[PDF Document Available for RAG] "
            
            # Add extracted content from image if available
            if st.session_state.extracted_text:
                query_with_context += (
                    f"\n\n[CONTENT EXTRACTED FROM UPLOADED IMAGE]:\n"
                    f"{st.session_state.extracted_text}\n"
                    f"[END OF EXTRACTED CONTENT]\n\n"
                )
                
                # If both PDF and image are available
                if st.session_state.temp_path:
                    query_with_context += "[NOTE: Both PDF document and image content are available for answering this question. Use both sources as needed.]\n\n"
            
            # Add user input
            query_with_context += f"User Question: {user_input}"
            
            # Stream the response from the agent
            for chunk in agent.stream(
                {
                    "messages": [
                        ("user", query_with_context)
                    ]
                },
                stream_mode="messages",
            ):
                # Extract content from stream chunks
                if isinstance(chunk, tuple) and len(chunk) >= 1:
                    msg_chunk = chunk[0]
                    
                    if hasattr(msg_chunk, 'content') and msg_chunk.content:
                        full_response += msg_chunk.content
                        # Update display with streaming cursor
                        response_placeholder.markdown(full_response + "▌")
            
            # Final response
            if full_response:
                response_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
            else:
                no_answer_msg = TRANSLATIONS["no_answer"].get(
                    language_code, 
                    "No answer returned"
                )
                response_placeholder.warning(no_answer_msg)
                
        except Exception as e:
            error_prefix = TRANSLATIONS["error"].get(language_code, "Error getting response")
            error_message = f"{error_prefix}: {str(e)}"
            response_placeholder.error(error_message)
            st.session_state.messages.append(
                {"role": "assistant", "content": f"⚠️ {error_message}"}
            )

# Footer
st.divider()
st.caption("🇳🇬 EduNaija AI Tutor - Empowering education across Nigeria")