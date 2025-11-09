# AI Prompts Management System

## Overview

The AI Prompts Management system allows super administrators to view, edit, and customize all AI prompts used throughout the interview platform. This provides flexibility to fine-tune AI behavior without modifying code.

## Features

- **Centralized Prompt Management**: All AI prompts stored in database
- **Context Documentation**: Each prompt includes description of its purpose
- **Model Configuration**: Choose different OpenAI models per prompt
- **Temperature Control**: Adjust creativity vs. consistency
- **Version Control**: Track when prompts were last updated
- **Active/Inactive Toggle**: Enable or disable prompts without deletion
- **Category Organization**: Prompts grouped by function

## Setup

### 1. Run Migration (First Time Only)

```bash
python migrate_add_ai_prompts.py
```

This creates the `ai_prompts` table in your database.

### 2. Initialize Default Prompts

```bash
python init_ai_prompts.py
```

This populates the database with 4 default prompts:
- **Generate Interview Questions** - Creates questions from job descriptions
- **Analyze CV** - Matches candidate CVs with job requirements
- **Evaluate Interview Answer** - Scores candidate responses with context awareness
- **Generate Personality Profile** - Creates candidate personality summaries

## Using the System

### Accessing AI Prompts

1. Log in as Super Admin
2. Navigate to Dashboard
3. Click "🤖 AI Prompts" button

### Viewing Prompts

Prompts are organized by category. Each prompt card shows:
- **Name**: Descriptive title
- **Key**: Unique identifier used in code
- **Status**: Active/Inactive badge
- **Description**: Purpose and context
- **Model**: AI model being used (e.g., gpt-4o-mini, gpt-3.5-turbo)
- **Temperature**: Creativity setting (0-2)
- **System Message**: AI role definition
- **Prompt Template**: The actual prompt with variables

### Editing a Prompt

1. Click "Edit" button on any prompt card
2. Modify any field:
   - **Basic Info**: Name, description, category
   - **AI Config**: Model, temperature, active status
   - **System Message**: How the AI should behave
   - **Prompt Template**: The prompt text with variables
3. Click "Save Changes"

### Variable Placeholders

Use curly braces for dynamic content in prompts:

**Question Generation:**
- `{job_description}` - The job posting content

**CV Analysis:**
- `{job_description}` - The job posting content
- `{cv_text}` - Extracted text from candidate's CV

**Answer Evaluation:**
- `{question_text}` - The interview question
- `{answer_text}` - Candidate's response
- `{question_weightage}` - Maximum score for this question

**Personality Profile:**
- `{cv_summary}` - Summary of candidate's CV
- `{answers_text}` - All interview Q&A pairs

### Adding New Prompts

1. Click "+ Add New Prompt" button
2. Fill in all required fields:
   - **Unique Key**: Lowercase identifier (e.g., `my_custom_prompt`)
   - **Name**: Display name
   - **Description**: What this prompt does
   - **Category**: Organizational category
   - **Model**: Choose AI model
   - **Temperature**: Set creativity level
   - **System Message**: Define AI behavior
   - **Prompt Template**: Write the prompt with variables
3. Click "Create Prompt"

**Note**: To use custom prompts in code, call:
```python
from app.services.ai_service import get_prompt

prompt_config = get_prompt('my_custom_prompt', var1=value1, var2=value2)
```

### Toggling Prompt Status

- Click "Deactivate" to disable a prompt (system will use fallback)
- Click "Activate" to re-enable a prompt
- Inactive prompts won't be used but remain in database

### Deleting Prompts

1. Click "Delete" button on prompt card
2. Confirm deletion in popup
3. **Warning**: Deletion is permanent

## Current AI Prompts

### 1. Generate Interview Questions
- **Key**: `generate_questions`
- **Purpose**: Creates 5-8 relevant pre-screening questions from job descriptions
- **Model**: GPT-3.5 Turbo
- **Temperature**: 0.7 (creative)
- **Used When**: Org admin clicks "Generate with AI" when creating a job

### 2. Analyze CV
- **Key**: `analyze_cv`
- **Purpose**: Compares candidate CV with job requirements
- **Model**: GPT-3.5 Turbo
- **Temperature**: 0.5 (balanced)
- **Used When**: Candidate uploads CV during application

### 3. Evaluate Interview Answer
- **Key**: `evaluate_answer`
- **Purpose**: Scores candidate answers with context awareness
- **Model**: GPT-4o Mini
- **Temperature**: 0.3 (consistent)
- **Used When**: Candidate submits each interview answer
- **Key Feature**: Identifies question types and scores appropriately

### 4. Generate Personality Profile
- **Key**: `personality_profile`
- **Purpose**: Creates personality summary from CV and answers
- **Model**: GPT-3.5 Turbo
- **Temperature**: 0.6 (slightly creative)
- **Used When**: Candidate completes interview

## Best Practices

### Temperature Settings
- **0.0-0.3**: Deterministic, consistent (good for scoring/evaluation)
- **0.4-0.7**: Balanced creativity (good for generation)
- **0.8-2.0**: Very creative (rarely used in business context)

### Model Selection
- **GPT-4o**: Most capable, slower, expensive
- **GPT-4o Mini**: Great balance of capability and speed
- **GPT-3.5 Turbo**: Fast and cost-effective for simple tasks

### Prompt Writing Tips
1. **Be Specific**: Clear instructions produce better results
2. **Use Examples**: Show the AI what you want
3. **Request Format**: Specify JSON, text, or other output formats
4. **Set Context**: Use system messages to define AI's role
5. **Test Iterations**: Try different temperatures and phrasings

### System Messages
Good system messages:
- ✅ "You are an expert HR interviewer..."
- ✅ "You are a professional recruiter with 10 years experience..."
- ❌ "Be helpful" (too vague)

## Troubleshooting

### Prompts Not Loading
- Check database connection
- Verify `ai_prompts` table exists
- Run `init_ai_prompts.py` to populate

### Changes Not Applied
- Ensure prompt is marked as "Active"
- Restart the application to clear any caches
- Check for errors in application logs

### Poor AI Responses
- Adjust temperature (lower = more consistent)
- Improve prompt clarity and specificity
- Add examples to the prompt
- Try a more capable model (e.g., GPT-4o Mini instead of GPT-3.5)

## Technical Details

### Database Schema
```sql
CREATE TABLE ai_prompts (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_message TEXT,
    prompt_template TEXT NOT NULL,
    model VARCHAR(50) DEFAULT 'gpt-3.5-turbo',
    temperature FLOAT DEFAULT 0.5,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Fallback Behavior
If a prompt is inactive or not found, the system uses hardcoded fallback prompts. This ensures the application continues working even if database prompts are misconfigured.

### Code Integration
The system uses a helper function to fetch prompts:

```python
from app.services.ai_service import get_prompt

# Get and format prompt
prompt_config = get_prompt('evaluate_answer', 
                          question_text="Sample question?",
                          answer_text="Sample answer",
                          question_weightage=10)

if prompt_config:
    # Use database prompt
    model = prompt_config['model']
    temperature = prompt_config['temperature']
    system_message = prompt_config['system_message']
    formatted_prompt = prompt_config['prompt']
else:
    # Use fallback prompt
    model = 'gpt-3.5-turbo'
    # ... fallback values
```

## Security Considerations

- Only super admins can access AI prompts management
- Prompts are stored server-side (not exposed to candidates)
- OpenAI API key remains secure in environment variables
- No user input is directly injected into prompts without sanitization

## Future Enhancements

Potential features for future versions:
- Prompt versioning and rollback
- A/B testing different prompt variations
- Analytics on prompt performance
- Import/export prompt configurations
- Prompt templates library

## Support

For questions or issues:
1. Check application logs for errors
2. Verify database connectivity
3. Ensure OpenAI API key is configured
4. Contact system administrator

---

**Last Updated**: November 9, 2025
**Version**: 1.0

