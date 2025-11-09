#!/usr/bin/env python3
"""
Initialize AI Prompts Database
This script populates the database with default AI prompts used throughout the system.
Run this after creating the ai_prompts table in the database.
"""

from app import create_app, db
from app.models import AIPrompt

def init_prompts():
    """Initialize default AI prompts in the database"""
    app = create_app()
    
    with app.app_context():
        # Check if prompts already exist
        existing_count = AIPrompt.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing prompts in database.")
            response = input("Do you want to continue? This will add/update prompts. (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        prompts = [
            {
                'key': 'generate_questions',
                'name': 'Generate Interview Questions from Job Description',
                'description': 'Generates 5-8 relevant pre-screening interview questions based on a job description. Each question is assigned a weightage (importance score) from 1-20.',
                'category': 'Question Generation',
                'system_message': 'You are an expert HR interviewer who creates insightful pre-screening questions.',
                'prompt_template': '''Based on the following job description, generate 5-8 relevant pre-screening interview questions. 
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
4. Clear and professional''',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'is_active': True
            },
            {
                'key': 'analyze_cv',
                'name': 'Analyze CV and Match with Job Description',
                'description': 'Analyzes a candidate\'s CV and compares it with the job description. Provides a summary of the candidate\'s experience and a matching percentage (0-100).',
                'category': 'CV Analysis',
                'system_message': 'You are an expert HR recruiter analyzing candidate CVs.',
                'prompt_template': '''Analyze the following CV and compare it with the job description. 
Provide:
1. A concise summary of the candidate's experience and expertise (2-3 sentences)
2. A matching percentage (0-100) indicating how well the candidate fits the job

Job Description:
{job_description}

Candidate CV:
{cv_text}

Return response as JSON:
{{
    "summary": "Brief summary here",
    "matching_percentage": 75.5
}}''',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.5,
                'is_active': True
            },
            {
                'key': 'evaluate_answer',
                'name': 'Evaluate Interview Answer',
                'description': 'Evaluates a candidate\'s interview answer with context-aware scoring. Identifies question type (Yes/No, Factual, Experience, Behavioral) and scores accordingly. Simple correct answers get high scores, while complex questions require detailed responses.',
                'category': 'Answer Evaluation',
                'system_message': 'You are an expert HR interviewer with strong contextual understanding. You evaluate answers fairly based on question type and provide appropriate scores. You understand that simple questions deserve high scores for correct simple answers.',
                'prompt_template': '''You are an expert HR interviewer evaluating a candidate's interview answer. Analyze the question type and provide fair, context-aware scoring.

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
}}''',
                'model': 'gpt-4o-mini',
                'temperature': 0.3,
                'is_active': True
            },
            {
                'key': 'personality_profile',
                'name': 'Generate Candidate Personality Profile',
                'description': 'Creates a brief personality profile (3-4 sentences) based on the candidate\'s CV summary and interview answers. Focuses on communication style, problem-solving approach, professional demeanor, and workplace-relevant personality traits.',
                'category': 'Profile Generation',
                'system_message': 'You are an expert HR psychologist creating candidate personality profiles.',
                'prompt_template': '''Based on the candidate's CV summary and interview answers, create a brief personality profile (3-4 sentences).

CV Summary:
{cv_summary}

Interview Answers:
{answers_text}

Focus on:
1. Communication style
2. Problem-solving approach
3. Professional demeanor
4. Key personality traits relevant to workplace''',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.6,
                'is_active': True
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for prompt_data in prompts:
            # Check if prompt already exists
            existing_prompt = AIPrompt.query.filter_by(key=prompt_data['key']).first()
            
            if existing_prompt:
                # Update existing prompt
                for key, value in prompt_data.items():
                    if key != 'key':  # Don't update the key itself
                        setattr(existing_prompt, key, value)
                updated_count += 1
                print(f"✓ Updated prompt: {prompt_data['name']}")
            else:
                # Create new prompt
                new_prompt = AIPrompt(**prompt_data)
                db.session.add(new_prompt)
                added_count += 1
                print(f"✓ Added prompt: {prompt_data['name']}")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Initialization complete!")
        print(f"   Added: {added_count} prompts")
        print(f"   Updated: {updated_count} prompts")
        print(f"   Total prompts in database: {AIPrompt.query.count()}")
        print(f"{'='*60}")
        print("\n💡 You can now manage these prompts from the Super Admin dashboard.")
        print("   Navigate to: Super Admin → AI Prompts\n")

if __name__ == '__main__':
    init_prompts()

