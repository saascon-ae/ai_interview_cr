import openai
from flask import current_app
import PyPDF2
import os
import re
import json
import traceback

def get_openai_client():
    """Get configured OpenAI client"""
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        # Construct full path
        full_path = os.path.join(current_app.root_path, 'static', pdf_path)
        
        with open(full_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def generate_questions_from_description(job_description):
    """Generate interview questions from job description using AI"""
    client = get_openai_client()
    
    prompt = f"""Based on the following job description, generate 5-8 relevant pre-screening interview questions. 
For each question, assign a weightage (importance score) from 1-20, where higher numbers indicate more important questions.

Job Description:
{job_description}

Return the response as a JSON array in this exact format:
[
    {{"text": "Question text here?", "weightage": 15}},
    {{"text": "Another question?", "weightage": 10}}
]

Make sure questions are:
1. Relevant to the job requirements
2. Open-ended to allow detailed responses
3. Assess key skills and experience
4. Clear and professional
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR interviewer who creates insightful pre-screening questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
            return questions_data
        else:
            # Fallback if JSON not found
            return [
                {"text": "What experience do you have related to this role?", "weightage": 15},
                {"text": "What are your key strengths for this position?", "weightage": 12}
            ]
            
    except Exception as e:
        print(f"Error generating questions: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        # Return fallback questions
        return [
            {"text": "What relevant experience do you have for this position?", "weightage": 15},
            {"text": "What are your key strengths?", "weightage": 12},
            {"text": "Why are you interested in this role?", "weightage": 10}
        ]

def analyze_cv(cv_path, job_description):
    """Analyze CV and match with job description"""
    client = get_openai_client()
    
    # Extract CV text
    cv_text = extract_text_from_pdf(cv_path)
    
    if not cv_text:
        return {
            'summary': 'Unable to extract CV content',
            'matching_percentage': 0.0
        }
    
    prompt = f"""Analyze the following CV and compare it with the job description. 
Provide:
1. A concise summary of the candidate's experience and expertise (2-3 sentences)
2. A matching percentage (0-100) indicating how well the candidate fits the job

Job Description:
{job_description}

Candidate CV:
{cv_text[:3000]}  # Limit to avoid token limits

Return response as JSON:
{{
    "summary": "Brief summary here",
    "matching_percentage": 75.5
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR recruiter analyzing candidate CVs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {
                'summary': 'Analysis completed',
                'matching_percentage': 50.0
            }
            
    except Exception as e:
        print(f"Error analyzing CV: {e}")
        return {
            'summary': 'Error during analysis',
            'matching_percentage': 0.0
        }

def evaluate_answer(question_text, answer_text, question_weightage):
    """Evaluate a candidate's answer and assign score"""
    client = get_openai_client()
    
    prompt = f"""Evaluate this interview answer on a scale relative to the question's weightage of {question_weightage}.

Question: {question_text}
Answer: {answer_text}

Consider:
1. Relevance to the question
2. Depth and detail
3. Clarity and communication
4. Professional presentation

Return a JSON with:
{{
    "score": <number between 0 and {question_weightage}>,
    "feedback": "Brief feedback on the answer"
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR interviewer evaluating candidate responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result.get('score', question_weightage * 0.5)
        else:
            return question_weightage * 0.6  # Default score
            
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return question_weightage * 0.5  # Return 50% of weightage as default

def generate_personality_profile(cv_summary, answers_data):
    """Generate personality profile based on CV and interview answers"""
    client = get_openai_client()
    
    answers_text = "\n".join([f"Q: {a['question']}\nA: {a['answer']}" for a in answers_data])
    
    prompt = f"""Based on the candidate's CV summary and interview answers, create a brief personality profile (3-4 sentences).

CV Summary:
{cv_summary}

Interview Answers:
{answers_text}

Focus on:
1. Communication style
2. Problem-solving approach
3. Professional demeanor
4. Key personality traits relevant to workplace
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR psychologist creating candidate personality profiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating personality profile: {e}")
        return "Personality profile analysis pending."

def transcribe_audio(audio_path):
    """Transcribe audio file using OpenAI Whisper"""
    client = get_openai_client()
    
    try:
        full_path = os.path.join(current_app.root_path, 'static', audio_path)
        
        with open(full_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return transcript.text
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def generate_speech(text):
    """Generate speech from text using OpenAI TTS with natural female voice"""
    client = get_openai_client()
    
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",  # High quality, more natural
            voice="nova",  # Natural, human-like female voice
            input=text
        )
        
        return response.content
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

