from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio, db
from app.models import Application, Answer, Question
from app.services.ai_service import transcribe_audio, evaluate_answer, generate_personality_profile, generate_speech
from app.services.email_service import send_interview_completion_email
from app.services.voice_service import save_audio_file
from datetime import datetime
import random
import base64

# Store active interview sessions
active_sessions = {}

@socketio.on('connect', namespace='/interview')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to interview server'})

@socketio.on('disconnect', namespace='/interview')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    if request.sid in active_sessions:
        del active_sessions[request.sid]

@socketio.on('start_interview', namespace='/interview')
def handle_start_interview(data):
    """Initialize interview session"""
    application_id = data.get('application_id')
    
    if not application_id:
        emit('error', {'message': 'Application ID required'})
        return
    
    # Get application and questions
    application = Application.query.get(application_id)
    if not application:
        emit('error', {'message': 'Application not found'})
        return
    
    questions = Question.query.filter_by(job_id=application.job_id).order_by(Question.order_index).all()
    
    if not questions:
        emit('error', {'message': 'No questions found for this job'})
        return
    
    # Randomize question order
    questions_list = list(questions)
    random.shuffle(questions_list)
    
    # Store session data
    active_sessions[request.sid] = {
        'application_id': application_id,
        'questions': [q.id for q in questions_list],
        'current_index': 0,
        'answers': []
    }
    
    # Join room for this application
    join_room(f'interview_{application_id}')
    
    # Send first question
    first_question = questions_list[0]
    emit('question', {
        'question_id': first_question.id,
        'text': first_question.text,
        'weightage': first_question.weightage,
        'question_number': 1,
        'total_questions': len(questions_list)
    })
    
    # Generate and send speech for the question
    try:
        audio_content = generate_speech(first_question.text)
        if audio_content:
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            emit('speech_generated', {'audio_data': audio_base64})
    except Exception as e:
        print(f"Error generating speech for question: {e}")

@socketio.on('answer_submitted', namespace='/interview')
def handle_answer_submitted(data):
    """Process submitted answer"""
    session_data = active_sessions.get(request.sid)
    
    if not session_data:
        emit('error', {'message': 'No active session'})
        return
    
    application_id = session_data['application_id']
    question_id = data.get('question_id')
    audio_data = data.get('audio_data')  # Base64 encoded audio
    answer_text = data.get('answer_text', '')
    duration = data.get('duration')  # Duration in seconds
    
    # Save audio file if provided
    audio_path = None
    if audio_data:
        audio_path = save_audio_file(audio_data, application_id, question_id)
        
        # Transcribe audio if no text provided
        if not answer_text and audio_path:
            try:
                answer_text = transcribe_audio(audio_path)
                # Emit transcribed text back to client
                emit('transcript_received', {
                    'question_id': question_id,
                    'transcript': answer_text
                })
            except Exception as e:
                print(f"Error transcribing audio: {e}")
                answer_text = "[Transcription failed]"
                emit('transcript_received', {
                    'question_id': question_id,
                    'transcript': answer_text
                })
    
    # Get question
    question = Question.query.get(question_id)
    if not question:
        emit('error', {'message': 'Question not found'})
        return
    
    # Evaluate answer using AI
    try:
        score = evaluate_answer(question.text, answer_text, question.weightage)
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        score = question.weightage * 0.5  # Default to 50%
    
    # Save answer to database
    answer = Answer(
        application_id=application_id,
        question_id=question_id,
        answer_text=answer_text,
        audio_path=audio_path,
        score=score,
        weightage=question.weightage,
        duration=duration
    )
    
    db.session.add(answer)
    
    # Update application score
    application = Application.query.get(application_id)
    application.total_score += score
    
    db.session.commit()
    
    # Store answer in session
    session_data['answers'].append({
        'question': question.text,
        'answer': answer_text,
        'score': score
    })
    
    # Move to next question
    session_data['current_index'] += 1
    current_index = session_data['current_index']
    
    if current_index < len(session_data['questions']):
        # Send next question
        next_question_id = session_data['questions'][current_index]
        next_question = Question.query.get(next_question_id)
        
        emit('question', {
            'question_id': next_question.id,
            'text': next_question.text,
            'weightage': next_question.weightage,
            'question_number': current_index + 1,
            'total_questions': len(session_data['questions'])
        })
        
        # Generate and send speech for the question
        try:
            audio_content = generate_speech(next_question.text)
            if audio_content:
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                emit('speech_generated', {'audio_data': audio_base64})
        except Exception as e:
            print(f"Error generating speech for question: {e}")
    else:
        application = Application.query.get(application_id)
        finalize_interview(application, session_data)

@socketio.on('skip_question', namespace='/interview')
def handle_skip_question(data):
    """Handle skipping the current question"""
    session_data = active_sessions.get(request.sid)
    
    if not session_data:
        emit('error', {'message': 'No active session'})
        return
    
    application_id = session_data['application_id']
    current_index = session_data['current_index']
    question_id = data.get('question_id')
    
    if question_id is None:
        emit('error', {'message': 'Question ID required to skip'})
        return
    
    if current_index >= len(session_data['questions']):
        emit('error', {'message': 'No more questions to skip'})
        return
    
    expected_question_id = session_data['questions'][current_index]
    if expected_question_id != question_id:
        emit('error', {'message': 'Question mismatch'})
        return
    
    question = Question.query.get(question_id)
    if not question:
        emit('error', {'message': 'Question not found'})
        return
    
    # Record skipped answer
    skipped_text = "Answer skipped by Candidate"
    answer = Answer(
        application_id=application_id,
        question_id=question_id,
        answer_text=skipped_text,
        audio_path=None,
        score=0.0,
        weightage=question.weightage,
        duration=0.0
    )
    
    db.session.add(answer)
    db.session.commit()
    
    # Track in session data
    session_data['answers'].append({
        'question': question.text,
        'answer': skipped_text,
        'score': 0.0
    })
    
    # Move to next question
    session_data['current_index'] += 1
    current_index = session_data['current_index']
    
    if current_index < len(session_data['questions']):
        next_question_id = session_data['questions'][current_index]
        next_question = Question.query.get(next_question_id)
        
        emit('question', {
            'question_id': next_question.id,
            'text': next_question.text,
            'weightage': next_question.weightage,
            'question_number': current_index + 1,
            'total_questions': len(session_data['questions'])
        })
        
        try:
            audio_content = generate_speech(next_question.text)
            if audio_content:
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                emit('speech_generated', {'audio_data': audio_base64})
        except Exception as e:
            print(f"Error generating speech for question: {e}")
    else:
        application = Application.query.get(application_id)
        finalize_interview(application, session_data)

@socketio.on('request_speech', namespace='/interview')
def handle_request_speech(data):
    """Generate speech audio for question text"""
    text = data.get('text')
    
    if not text:
        emit('error', {'message': 'Text required'})
        return
    
    try:
        audio_content = generate_speech(text)
        if audio_content:
            # Convert to base64 for transmission
            import base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            emit('speech_generated', {'audio_data': audio_base64})
        else:
            emit('error', {'message': 'Failed to generate speech'})
    except Exception as e:
        print(f"Error generating speech: {e}")
        emit('error', {'message': 'Speech generation failed'})

@socketio.on('ping', namespace='/interview')
def handle_ping():
    """Handle ping for connection testing"""
    emit('pong', {'timestamp': datetime.now().isoformat()})


def finalize_interview(application, session_data):
    """Finalize interview, persist results, and notify candidate"""
    if not application:
        emit('error', {'message': 'Application not found'})
        return
    
    candidate = application.candidate
    candidate_summary = ""
    if candidate and getattr(candidate, 'cv_summary', None):
        candidate_summary = candidate.cv_summary
    
    try:
        profile = generate_personality_profile(
            candidate_summary or "No CV summary available",
            session_data['answers']
        )
        application.personality_profile = profile
    except Exception as e:
        print(f"Error generating personality profile: {e}")
    
    application.status = 'completed'
    application.completed_at = datetime.utcnow()
    
    transcript = ""
    for item in session_data['answers']:
        transcript += f"Q: {item['question']}\nA: {item['answer']}\nScore: {item['score']}\n\n"
    application.interview_transcript = transcript
    
    db.session.commit()
    
    try:
        send_interview_completion_email(application)
    except Exception as e:
        print(f"Error sending interview completion email: {e}")
    
    emit('interview_complete', {
        'message': 'Thank you for completing the interview! Our team will review your application and reach out if we move forward together.',
        'total_score': application.total_score,
        'total_weightage': application.total_weightage
    })
    
    leave_room(f'interview_{application.id}')
    if request.sid in active_sessions:
        del active_sessions[request.sid]
