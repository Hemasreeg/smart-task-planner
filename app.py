from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os
import re

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
    """AI-powered task planner that breaks down goals into actionable tasks
    with realistic timelines and dependency management.
    Enhanced with Google Gemini AI for intelligent suggestions."""

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
        """Extract duration from goal text using regex for better matching"""
        goal_lower = goal.lower()
        
        # Use regex to find number + time unit patterns (handles extra spaces, plural/singular)
        # Pattern: number followed by optional spaces and 'day', 'days', 'week', 'weeks', 'month', 'months'
        
        # Check for days (e.g., "10 days", "10  days", "10 day")
        day_match = re.search(r'(\d+)\s*days?', goal_lower)
        if day_match:
            return int(day_match.group(1))
        
        # Check for weeks (e.g., "2 weeks", "2  week", "2 weeks")
        week_match = re.search(r'(\d+)\s*weeks?', goal_lower)
        if week_match:
            return int(week_match.group(1)) * 7
        
        # Check for months (e.g., "1 month", "1  months", "2 month")
        month_match = re.search(r'(\d+)\s*months?', goal_lower)
        if month_match:
            return int(month_match.group(1)) * 30
        
        # Default to 14 days if no duration found
        return 14
    
    def generate_tasks_for_phase(self, phase, project_type, phase_duration, start_date):
        """Generate tasks for each phase"""
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
            'Channel Setup': [
                {'name': 'Setup Social Media', 'desc': 'Configure social media accounts', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Setup Analytics', 'desc': 'Configure tracking and analytics', 'ratio': 0.3, 'priority': 'Medium'},
                {'name': 'Test Channels', 'desc': 'Verify all channels are working', 'ratio': 0.3, 'priority': 'High'}
            ],
            'Execution': [
                {'name': 'Implementation', 'desc': 'Execute planned activities', 'ratio': 0.7, 'priority': 'High'},
                {'name': 'Monitoring', 'desc': 'Track progress and adjust', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'Analysis': [
                {'name': 'Collect Data', 'desc': 'Gather performance metrics', 'ratio': 0.3, 'priority': 'High'},
                {'name': 'Analyze Results', 'desc': 'Evaluate campaign effectiveness', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Report Findings', 'desc': 'Create performance report', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'Concept': [
                {'name': 'Define Event Vision', 'desc': 'Establish event goals and theme', 'ratio': 0.5, 'priority': 'High'},
                {'name': 'Budget Planning', 'desc': 'Create initial budget estimate', 'ratio': 0.5, 'priority': 'High'}
            ],
            'Logistics': [
                {'name': 'Venue Selection', 'desc': 'Research and book venue', 'ratio': 0.35, 'priority': 'High'},
                {'name': 'Vendor Coordination', 'desc': 'Contract with suppliers and vendors', 'ratio': 0.35, 'priority': 'High'},
                {'name': 'Timeline Creation', 'desc': 'Develop detailed event schedule', 'ratio': 0.3, 'priority': 'Medium'}
            ],
            'Follow-up': [
                {'name': 'Thank You Communications', 'desc': 'Send thank you messages to attendees', 'ratio': 0.3, 'priority': 'Medium'},
                {'name': 'Collect Feedback', 'desc': 'Gather and analyze attendee feedback', 'ratio': 0.4, 'priority': 'High'},
                {'name': 'Final Report', 'desc': 'Create event summary and learnings', 'ratio': 0.3, 'priority': 'Medium'}
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
            {'name': f'{phase} Task 1', 'desc': f'First task in {phase}', 'ratio': 0.5, 'priority': 'High'},
            {'name': f'{phase} Task 2', 'desc': f'Second task in {phase}', 'ratio': 0.5, 'priority': 'Medium'}
        ])

        tasks = []
        current_date = start_date
        num_tasks = len(templates)

        # ✅ FIX: Calculate task durations that sum EXACTLY to phase_duration
        if phase_duration < num_tasks:
            # Phase too short - assign 1 day to first N tasks
            task_durations = [1 if i < phase_duration else 0 for i in range(num_tasks)]
        else:
            # Calculate initial durations based on ratios
            task_durations = [max(0, round(phase_duration * t['ratio'])) for t in templates]
            # Ensure at least 1 day for non-zero allocations
            task_durations = [max(1, d) if d > 0 else 0 for d in task_durations]
            
            # Adjust to match phase_duration exactly
            total_task_days = sum(task_durations)
            diff = phase_duration - total_task_days
            
            if diff > 0:
                # Add extra days to tasks with highest ratios
                for _ in range(diff):
                    max_idx = max(range(num_tasks), 
                                  key=lambda i: templates[i]['ratio'] if task_durations[i] > 0 else 0)
                    task_durations[max_idx] += 1
            elif diff < 0:
                # Remove days from tasks with most allocation
                for _ in range(abs(diff)):
                    max_idx = max(range(num_tasks), key=lambda i: task_durations[i])
                    if task_durations[max_idx] > 1:
                        task_durations[max_idx] -= 1
        
        # Generate tasks (skip tasks with 0 duration)
        for i, t in enumerate(templates):
            duration_days = task_durations[i]
            if duration_days == 0:
                continue  # Skip tasks with no time allocated
                
            end_date = current_date + timedelta(days=duration_days - 1)
            dependencies = [templates[i-1]['name']] if i > 0 and task_durations[i-1] > 0 else []
            tasks.append({
                'task_name': t['name'],
                'description': t['desc'],
                'duration': f"{duration_days} day{'s' if duration_days > 1 else ''}",
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'dependencies': dependencies,
                'priority': t['priority']
            })
            current_date = end_date + timedelta(days=1)
        return tasks
    
    def generate_plan(self, goal):
        """Generate complete project plan with accurate total duration"""
        project_type = self.detect_project_type(goal)
        total_duration = self.parse_duration(goal)
        phases = self.phases_templates[project_type]
        num_phases = len(phases)

        # Weighted distribution per project type
        if project_type == 'product_launch':
            weights = [0.12, 0.15, 0.28, 0.18, 0.15, 0.12]
        elif project_type == 'app_development':
            weights = [0.10, 0.15, 0.25, 0.25, 0.15, 0.10]
        elif project_type == 'marketing_campaign':
            weights = [0.15, 0.15, 0.25, 0.15, 0.20, 0.10]
        elif project_type == 'event_planning':
            weights = [0.12, 0.18, 0.25, 0.15, 0.20, 0.10]
        else:
            weights = [1.0 / num_phases] * num_phases

        if len(weights) != num_phases:
            weights = [1.0 / num_phases] * num_phases

        # Compute durations and adjust to exact total
        phase_durations = [max(1, round(total_duration * w)) for w in weights]
        diff = total_duration - sum(phase_durations)
        if diff != 0:
            for i in range(abs(diff)):
                idx = i % num_phases
                if diff > 0:
                    phase_durations[idx] += 1
                elif phase_durations[idx] > 1:
                    phase_durations[idx] -= 1

        start_date = datetime.now()
        current_date = start_date
        phase_list, milestones = [], []

        for i, phase_name in enumerate(phases):
            duration = phase_durations[i]
            tasks = self.generate_tasks_for_phase(phase_name, project_type, duration, current_date)
            phase_list.append({'phase': phase_name, 'tasks': tasks})

            if i in [0, num_phases // 2, num_phases - 1]:
                milestone_date = tasks[-1]['end_date'] if tasks else current_date.strftime('%Y-%m-%d')
                milestones.append(f"{phase_name} Complete ({milestone_date})")

            # ✅ CRITICAL: Move to next day after phase ends (no overlap, no gaps)
            if tasks:
                last_task_end = datetime.strptime(tasks[-1]['end_date'], '%Y-%m-%d')
                current_date = last_task_end + timedelta(days=1)

        # Calculate exact end date based on requested duration
        end_date = start_date + timedelta(days=total_duration - 1)
        ai_insights = self.get_ai_insights(goal, num_phases, total_duration) if self.use_gemini else ""

        summary = {
            'milestones': milestones,
            'remarks': f"Optimized {project_type.replace('_', ' ').title()} plan with {num_phases} phases across {total_duration} days. "
                       f"Timeline accounts for dependencies and realistic task allocation. {ai_insights}"
        }

        return {
            'goal': goal,
            'total_duration': f"{total_duration} days",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'phases': phase_list,
            'summary': summary,
            'ai_enhanced': self.use_gemini,
            'project_type': project_type
        }
    
    def get_ai_insights(self, goal, num_phases, duration):
        """Generate short AI insight"""
        try:
            prompt = f"""Given this project goal: "{goal}"
With {num_phases} phases over {duration} days, give ONE short actionable insight (max 20 words)."""
            response = self.model.generate_content(prompt)
            insight = response.text.strip()
            return insight[:150] if len(insight) > 150 else insight
        except Exception as e:
            print(f"AI insight error: {e}")
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
    return jsonify({
        'status': 'online',
        'google_ai': GEMINI_AVAILABLE,
        'version': '1.3.0'
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
