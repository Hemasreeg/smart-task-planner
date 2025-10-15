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
            {'name': f'{phase} Task 1', 'desc': f'Complete first task of {phase}', 'ratio': 0.5, 'priority': 'High'},
            {'name': f'{phase} Task 2', 'desc': f'Complete second task of {phase}', 'ratio': 0.5, 'priority': 'Medium'}
        ])
        
        tasks = []
        current_date = start_date
        
        # Ensure phase_duration is at least the number of tasks
        min_duration = len(templates)
        if phase_duration < min_duration:
            phase_duration = min_duration
        
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
        
        # Calculate phase durations intelligently
        num_phases = len(phases)
        base_duration = max(1, total_duration // num_phases)
        remaining = total_duration % num_phases
        
        # Distribute duration based on project type and phase importance
        phase_durations = []
        
        # Different distribution strategies based on project type
        if project_type == 'product_launch':
            # Product launch: More time for Development and Marketing
            weights = [0.12, 0.15, 0.28, 0.18, 0.15, 0.12]  # Planning, Design, Dev, Test, Marketing, Deploy
        elif project_type == 'app_development':
            # App dev: More time for Development phases
            weights = [0.10, 0.15, 0.25, 0.25, 0.15, 0.10]  # Planning, UI/UX, Frontend, Backend, Testing, Deploy
        elif project_type == 'marketing_campaign':
            # Marketing: More time for Content and Execution
            weights = [0.15, 0.15, 0.25, 0.15, 0.20, 0.10]  # Research, Strategy, Content, Channels, Execute, Analyze
        elif project_type == 'event_planning':
            # Events: More time for Logistics and Execution
            weights = [0.12, 0.18, 0.25, 0.15, 0.20, 0.10]  # Concept, Planning, Logistics, Marketing, Execute, Follow-up
        else:
            # Default: Equal distribution
            weights = [1.0 / num_phases] * num_phases
        
        # Ensure weights match number of phases
        if len(weights) != num_phases:
            weights = [1.0 / num_phases] * num_phases
        
        # Calculate durations based on weights
        for i in range(num_phases):
            duration = max(1, round(total_duration * weights[i]))
            phase_durations.append(duration)
        
        # Adjust to exactly match total_duration
        current_total = sum(phase_durations)
        diff = total_duration - current_total
        
        # Distribute the difference
        if diff > 0:
            # Add extra days to middle phases
            for i in range(diff):
                phase_durations[num_phases // 2 + (i % 2)] += 1
        elif diff < 0:
            # Remove days from phases with most time
            for i in range(abs(diff)):
                max_idx = phase_durations.index(max(phase_durations))
                if phase_durations[max_idx] > 1:
                    phase_durations[max_idx] -= 1
        
        # Final verification
        assert sum(phase_durations) == total_duration, "Phase durations don't match total duration"
        
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
        
        # Ensure we match the requested duration exactly
        if actual_duration != total_duration:
            # Recalculate end date to match requested duration
            end_date = start_date + timedelta(days=total_duration - 1)
            actual_duration = total_duration
        
        # Use Google AI to enhance summary if available
        ai_insights = self.get_ai_insights(goal, num_phases, actual_duration) if self.use_gemini else ""
        
        base_remarks = f"Optimized {project_type.replace('_', ' ').title()} plan with {num_phases} phases across {actual_duration} days. Timeline accounts for dependencies and realistic task allocation."
        
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
            'ai_enhanced': self.use_gemini,
            'project_type': project_type
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
