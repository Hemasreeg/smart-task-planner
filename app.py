from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

# Google AI Integration
try:
    import google.generativeai as genai
    GOOGLE_API_KEY = "AIzaSyDpkaJCEnHgrwaEfMzznPCxT_5FPC1MIV4"
    genai.configure(api_key=GOOGLE_API_KEY)
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not installed. Using local AI logic.")

app = Flask(__name__)

class SmartTaskPlanner:
    """
    AI-powered task planner that breaks down goals into actionable tasks
    with realistic timelines and dependency management.
    Enhanced with Google Gemini AI for intelligent suggestions.
    """
    
    def __init__(self):
        self.use_gemini = GEMINI_AVAILABLE
        if self.use_gemini:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Google Gemini AI initialized successfully!")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.use_gemini = False
        
        self.phases_templates = {
            'product_launch': ['Planning', 'Design', 'Development', 'Testing', 'Marketing', 'Deployment'],
            'app_development': ['Planning', 'UI/UX Design', 'Frontend Development', 'Backend Development', 'Testing', 'Deployment'],
            'marketing_campaign': ['Research', 'Strategy', 'Content Creation', 'Channel Setup', 'Execution', 'Analysis'],
            'event_planning': ['Concept', 'Planning', 'Logistics', 'Marketing', 'Execution', 'Follow-up'],
            'default': ['Planning', 'Execution', 'Review', 'Completion']
        }
    
    def detect_project_type(self, goal):
        """Detect project type from goal description"""
        goal_lower = goal.lower()
        if any(word in goal_lower for word in ['product', 'launch', 'release']):
            return 'product_launch'
        elif any(word in goal_lower for word in ['app', 'application', 'software', 'website']):
            return 'app_development'
        elif any(word in goal_lower for word in ['marketing', 'campaign', 'promotion']):
            return 'marketing_campaign'
        elif any(word in goal_lower for word in ['event', 'conference', 'meetup']):
            return 'event_planning'
        return 'default'
    
    def parse_duration(self, goal):
        """Extract duration from goal text"""
        goal_lower = goal.lower()
        
        # Check for days
        if 'day' in goal_lower:
            for i in range(1, 100):
                if f"{i} day" in goal_lower:
                    return i
        
        # Check for weeks
        if 'week' in goal_lower:
            for i in range(1, 20):
                if f"{i} week" in goal_lower:
                    return i * 7
        
        # Check for months
        if 'month' in goal_lower:
            for i in range(1, 12):
                if f"{i} month" in goal_lower:
                    return i * 30
        
        # Default to 14 days
        return 14
    
    def generate_tasks_for_phase(self, phase, project_type, phase_duration, start_date):
        """Generate tasks for a specific phase"""
        task_templates = {
            'Planning': [
                {'name': 'Market Research', 'desc': 'Analyze competitors and target audience', 'ratio': 0.3, 'priority': 'High'},
                {'name': 'Define Requirements', 'desc': 'Document features and specifications', 'ratio': 0.35, 'priority': 'High'},
                {'name': 'Create Project Roadmap', 'desc': 'Set milestones and timeline', 'ratio': 0.35, 'priority': 'Medium'}
            ],
            'Design': [
                {'name': 'Wireframing', 'desc': 'Create low-fidelity layouts', 'ratio': 0.25, 'priority': 'High'},
                {'name': 'UI Design', 'desc': 'Design high-fidelity mockups', 'ratio': 0.45, 'priority': 'High'},
                {'name': 'Design Review', 'desc': 'Review and refine designs', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'UI/UX Design': [
                {'name': 'User Research', 'desc': 'Understand user needs and behavior', 'ratio': 0.25, 'priority': 'High'},
                {'name': 'Wireframes & Prototypes', 'desc': 'Create interactive prototypes', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Visual Design', 'desc': 'Apply branding and polish UI', 'ratio': 0.35, 'priority': 'Medium'}
            ],
            'Development': [
                {'name': 'Setup Development Environment', 'desc': 'Configure tools and frameworks', 'ratio': 0.15, 'priority': 'High'},
                {'name': 'Core Feature Development', 'desc': 'Build main functionality', 'ratio': 0.6, 'priority': 'High'},
                {'name': 'Integration & Bug Fixes', 'desc': 'Integrate components and fix issues', 'ratio': 0.25, 'priority': 'High'}
            ],
            'Frontend Development': [
                {'name': 'Component Architecture', 'desc': 'Set up component structure', 'ratio': 0.2, 'priority': 'High'},
                {'name': 'UI Implementation', 'desc': 'Build user interface', 'ratio': 0.5, 'priority': 'High'},
                {'name': 'State Management', 'desc': 'Implement data flow', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'Backend Development': [
                {'name': 'Database Design', 'desc': 'Design schema and relationships', 'ratio': 0.25, 'priority': 'High'},
                {'name': 'API Development', 'desc': 'Build REST/GraphQL endpoints', 'ratio': 0.5, 'priority': 'High'},
                {'name': 'Security & Authentication', 'desc': 'Implement auth and security', 'ratio': 0.25, 'priority': 'High'}
            ],
            'Testing': [
                {'name': 'Unit Testing', 'desc': 'Test individual components', 'ratio': 0.3, 'priority': 'High'},
                {'name': 'Integration Testing', 'desc': 'Test system integration', 'ratio': 0.35, 'priority': 'High'},
                {'name': 'User Acceptance Testing', 'desc': 'Get user feedback', 'ratio': 0.35, 'priority': 'Medium'}
            ],
            'Marketing': [
                {'name': 'Create Marketing Materials', 'desc': 'Design promotional content', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Social Media Campaign', 'desc': 'Launch social media presence', 'ratio': 0.35, 'priority': 'Medium'},
                {'name': 'PR & Outreach', 'desc': 'Contact media and influencers', 'ratio': 0.25, 'priority': 'Medium'}
            ],
            'Deployment': [
                {'name': 'Prepare Production Environment', 'desc': 'Setup servers and infrastructure', 'ratio': 0.3, 'priority': 'High'},
                {'name': 'Deploy to Production', 'desc': 'Launch the application', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Monitor & Optimize', 'desc': 'Track performance and fix issues', 'ratio': 0.3, 'priority': 'High'}
            ],
            'Research': [
                {'name': 'Market Analysis', 'desc': 'Study market trends and opportunities', 'ratio': 0.5, 'priority': 'High'},
                {'name': 'Competitor Research', 'desc': 'Analyze competitor strategies', 'ratio': 0.5, 'priority': 'High'}
            ],
            'Strategy': [
                {'name': 'Define Target Audience', 'desc': 'Identify and segment audience', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Set Campaign Goals', 'desc': 'Define KPIs and objectives', 'ratio': 0.6, 'priority': 'High'}
            ],
            'Content Creation': [
                {'name': 'Content Planning', 'desc': 'Plan content calendar', 'ratio': 0.3, 'priority': 'Medium'},
                {'name': 'Create Content', 'desc': 'Write, design, and produce content', 'ratio': 0.7, 'priority': 'High'}
            ],
            'Execution': [
                {'name': 'Implementation', 'desc': 'Execute planned activities', 'ratio': 0.7, 'priority': 'High'},
                {'name': 'Monitoring', 'desc': 'Track progress and adjust', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'Review': [
                {'name': 'Evaluate Results', 'desc': 'Analyze outcomes and metrics', 'ratio': 0.6, 'priority': 'High'},
                {'name': 'Document Learnings', 'desc': 'Record insights and improvements', 'ratio': 0.4, 'priority': 'Medium'}
            ],
            'Completion': [
                {'name': 'Final Delivery', 'desc': 'Complete and deliver project', 'ratio': 0.6, 'priority': 'High'},
                {'name': 'Post-Project Review', 'desc': 'Review and close project', 'ratio': 0.4, 'priority': 'Low'}
            ]
        }
        
        templates = task_templates.get(phase, [
            {'name': f'{phase} Task 1', 'desc': f'Complete first task of {phase}', 'ratio': 0.5, 'priority': 'High'},
            {'name': f'{phase} Task 2', 'desc': f'Complete second task of {phase}', 'ratio': 0.5, 'priority': 'Medium'}
        ])
        
        tasks = []
        current_date = start_date
        
        for i, template in enumerate(templates):
            duration_days = max(1, round(phase_duration * template['ratio']))
            end_date = current_date + timedelta(days=duration_days - 1)
            
            # Determine dependencies
            dependencies = []
            if i > 0:
                dependencies = [templates[i-1]['name']]
            
            task = {
                'task_name': template['name'],
                'description': template['desc'],
                'duration': f"{duration_days} day{'s' if duration_days > 1 else ''}",
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'dependencies': dependencies,
                'priority': template['priority']
            }
            
            tasks.append(task)
            current_date = end_date + timedelta(days=1)
        
        return tasks
    
    def generate_plan(self, goal):
        """Generate complete project plan"""
        # Parse input
        project_type = self.detect_project_type(goal)
        total_duration = self.parse_duration(goal)
        phases = self.phases_templates[project_type]
        
        # Calculate phase durations
        num_phases = len(phases)
        base_duration = total_duration // num_phases
        remaining = total_duration % num_phases
        
        # Distribute duration (give more time to middle phases)
        phase_durations = []
        for i in range(num_phases):
            if i == 0:  # Planning gets less time
                phase_durations.append(max(1, base_duration - 1))
            elif i < num_phases // 2:  # Early phases get standard time
                phase_durations.append(base_duration)
            elif i < num_phases - 1:  # Middle phases get more time
                phase_durations.append(base_duration + 1)
            else:  # Final phase gets remaining time
                phase_durations.append(base_duration + remaining)
        
        # Adjust to match total
        while sum(phase_durations) < total_duration:
            phase_durations[num_phases // 2] += 1
        while sum(phase_durations) > total_duration:
            phase_durations[-1] -= 1
        
        # Generate phases and tasks
        start_date = datetime.now()
        current_date = start_date
        phase_list = []
        all_milestones = []
        
        for i, phase_name in enumerate(phases):
            phase_duration = phase_durations[i]
            tasks = self.generate_tasks_for_phase(phase_name, project_type, phase_duration, current_date)
            
            phase_list.append({
                'phase': phase_name,
                'tasks': tasks
            })
            
            # Add milestone at end of key phases
            if i in [0, num_phases // 2, num_phases - 1]:
                milestone_date = tasks[-1]['end_date'] if tasks else current_date.strftime('%Y-%m-%d')
                all_milestones.append(f"{phase_name} Complete ({milestone_date})")
            
            # Update current date
            if tasks:
                last_task_end = datetime.strptime(tasks[-1]['end_date'], '%Y-%m-%d')
                current_date = last_task_end + timedelta(days=1)
        
        # Generate summary
        end_date = current_date - timedelta(days=1)
        actual_duration = (end_date - start_date).days + 1
        
        # Use Google AI to enhance summary if available
        ai_insights = self.get_ai_insights(goal, num_phases, actual_duration) if self.use_gemini else ""
        
        base_remarks = f"Optimized plan with {num_phases} phases across {actual_duration} days. Timeline accounts for dependencies and realistic task allocation."
        
        summary = {
            'milestones': all_milestones,
            'remarks': f"{base_remarks} {ai_insights}" if ai_insights else base_remarks
        }
        
        # Build final plan
        plan = {
            'goal': goal,
            'total_duration': f"{actual_duration} days",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'phases': phase_list,
            'summary': summary,
            'ai_enhanced': self.use_gemini
        }
        
        return plan
    
    def get_ai_insights(self, goal, num_phases, duration):
        """Get AI-powered insights using Google Gemini"""
        try:
            prompt = f"""Given this project goal: "{goal}"
            
With {num_phases} phases over {duration} days, provide ONE brief, actionable insight or recommendation (max 20 words) to ensure project success. Focus on potential risks or optimization opportunities."""
            
            response = self.model.generate_content(prompt)
            insight = response.text.strip()
            
            # Clean up the response
            if len(insight) > 150:
                insight = insight[:147] + "..."
            
            return insight
        except Exception as e:
            print(f"AI insight generation failed: {e}")
            return ""


# Initialize planner
planner = SmartTaskPlanner()


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """API endpoint to generate task plan"""
    try:
        data = request.get_json()
        goal = data.get('goal', '')
        
        if not goal:
            return jsonify({'error': 'Goal is required'}), 400
        
        # Generate plan
        plan = planner.generate_plan(goal)
        
        return jsonify(plan), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-suggest', methods=['POST'])
def ai_suggest():
    """API endpoint to get AI suggestions for goal improvement"""
    try:
        if not GEMINI_AVAILABLE:
            return jsonify({'suggestion': 'AI suggestions require Google API setup'}), 200
        
        data = request.get_json()
        partial_goal = data.get('goal', '')
        
        if not partial_goal or len(partial_goal) < 5:
            return jsonify({'suggestion': ''}), 200
        
        # Get AI suggestions
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""User is typing a project goal: "{partial_goal}"

Suggest a complete, specific project goal with a realistic timeline. Format: "Action + deliverable + timeline"
Example: "Build a mobile app in 3 weeks" or "Launch a marketing campaign in 2 weeks"

Provide ONE suggestion only (max 15 words):"""
        
        response = model.generate_content(prompt)
        suggestion = response.text.strip().strip('"').strip("'")
        
        return jsonify({'suggestion': suggestion}), 200
    
    except Exception as e:
        return jsonify({'suggestion': ''}), 200


@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint to check system status"""
    return jsonify({
        'status': 'online',
        'google_ai': GEMINI_AVAILABLE,
        'version': '1.1.0'
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
