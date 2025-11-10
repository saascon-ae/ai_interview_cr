import openai
from flask import current_app
import PyPDF2
import os
import re
import json
import traceback
from app.models import AIPrompt

def get_openai_client():
    """Get configured OpenAI client"""
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

def get_prompt(key, **kwargs):
    """
    Get AI prompt from database and format with provided kwargs
    Falls back to default if prompt not found in database
    """
    from app import db
    
    try:
        prompt_config = AIPrompt.query.filter_by(key=key, is_active=True).first()
    except Exception as exc:
        current_app.logger.warning("Unable to load AI prompt '%s': %s", key, exc)
        db.session.rollback()
        return None
    
    if not prompt_config:
        # Return None if not found - caller will handle fallback
        return None
    
    # Format the prompt template with provided variables
    try:
        prompt = prompt_config.prompt_template.format(**kwargs)
    except KeyError as e:
        print(f"Error formatting prompt {key}: missing variable {e}")
        return None
    
    return {
        'system_message': prompt_config.system_message,
        'prompt': prompt,
        'model': prompt_config.model,
        'temperature': prompt_config.temperature
    }

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
    
    # Try to get prompt from database
    prompt_config = get_prompt('generate_questions', job_description=job_description)
    
    # Fallback to default prompt if not in database
    if not prompt_config:
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
        system_message = "You are an expert HR interviewer who creates insightful pre-screening questions."
        model = "gpt-3.5-turbo"
        temperature = 0.7
    else:
        prompt = prompt_config['prompt']
        system_message = prompt_config['system_message']
        model = prompt_config['model']
        temperature = prompt_config['temperature']
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
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
    try:
        client = get_openai_client()
    except Exception as e:
        print(f"AI analysis unavailable: {e}")
        return {
            'summary': 'Analysis pending',
            'matching_percentage': 0.0
        }
    
    # Extract CV text
    cv_text = extract_text_from_pdf(cv_path)
    
    if not cv_text:
        return {
            'summary': 'Unable to extract CV content',
            'matching_percentage': 0.0
        }
    
    # Try to get prompt from database
    prompt_config = get_prompt('analyze_cv', job_description=job_description, cv_text=cv_text[:3000])
    
    # Fallback to default prompt if not in database
    if not prompt_config:
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
        system_message = "You are an expert HR recruiter analyzing candidate CVs."
        model = "gpt-3.5-turbo"
        temperature = 0.5
    else:
        prompt = prompt_config['prompt']
        system_message = prompt_config['system_message']
        model = prompt_config['model']
        temperature = prompt_config['temperature']
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
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
    
    # Try to get prompt from database
    prompt_config = get_prompt('evaluate_answer', question_text=question_text, answer_text=answer_text, question_weightage=question_weightage)
    
    # Fallback to default prompt if not in database
    if not prompt_config:
        prompt = f"""You are an expert HR interviewer evaluating a candidate's interview answer. Analyze the question type and provide fair, context-aware scoring.

Question: {question_text}
Answer: {answer_text}
Maximum Score: {question_weightage}

IMPORTANT SCORING GUIDELINES:

1. IDENTIFY THE QUESTION TYPE:
   - Yes/No Questions: Simple "yes" or "no" with confirmation should score highly if correct
   - Factual Questions: Direct, accurate answers deserve high scores even if brief
   - Experience Questions: Require elaboration and examples for high scores
   - Behavioral Questions: Need detailed responses with context

2. SCORING CRITERIA BY TYPE:
   
   For Yes/No or Simple Factual Questions:
   - If answer correctly addresses the question → 80-100% of max score
   - If answer is correct but unclear → 60-80% of max score
   - If answer is partially correct → 40-60% of max score
   - If answer is incorrect or contradictory → 20-40% of max score
   - If answer is completely wrong or irrelevant → 0-20% of max score
   
   For Complex/Behavioral Questions:
   - Consider depth, detail, relevance, and professionalism
   - Brief answers should score lower (30-60%)
   - Detailed, relevant answers score higher (60-100%)

3. KEY RULES:
   - A short but CORRECT answer to a simple question deserves a HIGH score
   - Don't penalize brevity if the question only requires a brief answer
   - Focus on whether the answer is CORRECT and RELEVANT, not just length
   - Consider if the candidate understood and answered what was asked

Example:
Q: "Are you available to join in 30 days?"
A: "Yes, I can join in 30 days, yes."
→ This should score 85-95% because it directly and correctly answers the question

Q: "Tell me about your leadership experience"
A: "Yes, I have some experience."
→ This should score 30-40% because it lacks necessary detail

Return ONLY a valid JSON object with:
{{
    "score": <number between 0 and {question_weightage}>,
    "feedback": "Brief feedback explaining the score"
}}
"""
        system_message = "You are an expert HR interviewer with strong contextual understanding. You evaluate answers fairly based on question type and provide appropriate scores. You understand that simple questions deserve high scores for correct simple answers."
        model = "gpt-4o-mini"
        temperature = 0.3
    else:
        prompt = prompt_config['prompt']
        system_message = prompt_config['system_message']
        model = prompt_config['model']
        temperature = prompt_config['temperature']
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
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
    
    # Try to get prompt from database
    prompt_config = get_prompt('personality_profile', cv_summary=cv_summary, answers_text=answers_text)
    
    # Fallback to default prompt if not in database
    if not prompt_config:
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
        system_message = "You are an expert HR psychologist creating candidate personality profiles."
        model = "gpt-3.5-turbo"
        temperature = 0.6
    else:
        prompt = prompt_config['prompt']
        system_message = prompt_config['system_message']
        model = prompt_config['model']
        temperature = prompt_config['temperature']
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
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

