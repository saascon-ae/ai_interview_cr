from app import create_app, socketio, db
from app.models import User, Organization, Job, Question, Candidate, Application, Answer

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Organization': Organization,
        'Job': Job,
        'Question': Question,
        'Candidate': Candidate,
        'Application': Application,
        'Answer': Answer
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5005))
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

