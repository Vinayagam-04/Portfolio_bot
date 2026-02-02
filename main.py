# File: main.py
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from gtts import gTTS
import google.generativeai as genai
import os

# Load Gemini API key from environment variable for security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY)

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) 

# Create a directory to store temporary audio files
if not os.path.exists("audio_responses"):
    os.makedirs("audio_responses")

# --- Resume Data and System Prompt ---
resume = """
Vinayagam M

+91-6382401069
vinayagamv398@gmail.com
linkedin
github.com/Vinayagam-04
potfolio

OBJECTIVE

Dedicated and innovative student specializing in Artificial Intelligence & Machine Learning, aiming to apply
technical expertise in AI, automation and robotics to drive impactful solutions in real-world environments.

EDUCATION

B.E. in Computer Science & Engineering (AI & ML)
2022 – 2026
K.S. Rangasamy College of Technology, Namakkal
CGPA: 8.34/10

SKILLS & INTERESTS

Programming: Python, Java
AI/ML: TensorFlow, Keras, OpenCV, NLP, RAG
Web Development: HTML, CSS, JavaScript, Flask, Streamlit, django
Database: MySQL, (Vector DB) ChromaDB, Pinecone
Deployment: Firebase, Render, Netilify
Tools: XAMPP, TeamViewer, AnyDesk, Unity
Interests: Robotics, Web Development, Sustainable Farming, Chatbots
Additional: Data Labeling, Computer Vision, Deep Learning

PROJECTS

AGNI: Tamil Chatbot with Gemini API
· Developed a Telegram chatbot in Tamil using Gemini API, designed for intuitive, culturally relevant interactions
and programming query support.

Eco Weed AI: Automated Weed Removal
· Built an AI-powered robotic system using deep learning and Raspberry Pi for sustainable, chemical-free farming
with mobile-based emergency control.

RPA-Based Attendance Management System
· Designed a Robotic Process Automation system integrated with computer vision for efficient attendance tracking.

EduBot: Multi-Language Educational Chatbot
· Created an educational chatbot supporting multiple languages using Flask, Gemini API, and deployed on Render.

INTERNSHIPS

AI Dataset Labeling Intern at Alfa TKG Integrated Solutions
· Labeled datasets and performed computer vision tasks for robotic welding; used TeamViewer and AnyDesk.
· Received stipend of 10,000.

RAG-Based AI Intern at Certainty.ai
· Worked on Retrieval-Augmented Generation systems; optimized retrieval processes using vector databases like
ChromaDB, Pinecone.
· Received stipend of 15,000.
"""

system_prompt = f"""
You are Vinayagam's virtual assistant, integrated into his personal portfolio website. Your personality should be professional, friendly, and helpful. Your goal is to represent Vinayagam accurately and positively to potential employers, collaborators, or anyone curious about his work.

You must adhere to these rules:
1.  **Embody Vinayagam:** Answer in the first person, as if you are Vinayagam. For example, instead of "Vinayagam's skills are...", say "My skills include...".
2.  **Use the Resume:** Base all your answers strictly on the provided resume content below. Do not invent information.
3.  **Handle Hiring Questions:** For questions like "Why should I hire you?", synthesize information from the resume to create a compelling, concise pitch. Highlight key skills (like AI/ML, Full Stack), innovative projects (like Eco Weed AI, AGNI chatbot), and practical internship experience.
4.  **Keep it Concise:** Provide short, clear, and direct answers. Avoid long paragraphs.
5.  **Stay on Topic:** If asked a question that cannot be answered from the resume or is unrelated to Vinayagam's professional profile, politely decline by saying: "As Vinayagam's AI assistant, I can only answer questions related to his professional skills and experience. How else can I help you regarding his profile?"

Here is the resume you must use:
---
{resume}
---
"""

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=system_prompt)
chat = model.start_chat(history=[])

# --- Main Page Route ---
@app.route('/')
def home():
    # Correctly renders the index.html file from the 'templates' folder
    return render_template('index.html')

# --- API Endpoints ---
@app.route('/chat', methods=['POST'])
def chat_handler():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Get response from Gemini
        response = chat.send_message(user_message)
        bot_reply_text = response.text

        # Generate Text-to-Speech audio
        tts = gTTS(bot_reply_text, lang='en', tld='co.in')  # Using Indian English accent

        # Save audio file with a unique name
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join("audio_responses", audio_filename)
        tts.save(audio_path)

        # Create a URL to access the audio file
        audio_url = request.host_url + f"audio/{audio_filename}"

        return jsonify({
            "reply_text": bot_reply_text,
            "reply_audio_url": audio_url
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# Endpoint to serve the generated audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('audio_responses', filename)

# --- Run the App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
