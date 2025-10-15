# Smart Task Planner 🧠

An intelligent AI-powered task planning system that transforms your goals into comprehensive, actionable project plans with beautiful, modern UI.

**🤖 NOW ENHANCED WITH GOOGLE GEMINI AI!**

## ✨ Features

- **🤖 Google AI Enhanced**: Powered by Google Gemini AI for intelligent insights and recommendations
- **AI-Powered Planning**: Advanced algorithm breaks down goals into logical phases and tasks
- **Smart Timeline Generation**: Automatically calculates realistic timelines with dependencies
- **Intelligent Insights**: AI-powered project analysis and optimization suggestions
- **Beautiful Modern UI**: Glassmorphism design with purple/blue gradient theme
- **Interactive Visualizations**: Timeline progress bars, collapsible phase cards, and milestone tracking
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Export Functionality**: Download plans as JSON for future reference
- **Multiple Project Types**: Optimized templates for product launches, app development, marketing campaigns, and more

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google API Key (included)

### Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd Stp
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## 📁 Project Structure

```
Stp/
├── app.py                 # Flask backend with AI planning logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # Glassmorphism styling
    └── script.js         # Frontend interactivity
```

## 💡 How to Use

1. **Enter Your Goal**: Type your project goal with a timeline
   - Example: "Launch a product in 2 weeks"
   - Example: "Build a mobile app in 20 days"

2. **Generate Plan**: Click the "Generate Plan" button

3. **Review Your Plan**: 
   - View project overview and timeline
   - Expand phases to see detailed tasks
   - Check dependencies and priorities
   - Review key milestones

4. **Export or Print**: Download as JSON or print the plan

## 🎨 Design Highlights

- **Glassmorphism Cards**: Frosted glass effect with blur
- **Animated Gradients**: Dynamic purple-blue background
- **Smooth Transitions**: Fade-in animations and hover effects
- **Priority Badges**: Color-coded task priorities (High/Medium/Low)
- **Timeline Visualization**: Animated progress bars for each phase
- **Responsive Grid**: Adapts beautifully to any screen size

## 🧩 Supported Project Types

The AI automatically detects and optimizes for:
- Product Launches
- App/Software Development
- Marketing Campaigns
- Event Planning
- General Projects

## 🛠️ Technology Stack

### Backend
- **Flask**: Lightweight Python web framework
- **Python**: Core planning logic and algorithms

### Frontend
- **HTML5**: Semantic structure
- **CSS3**: Modern styling with glassmorphism
- **JavaScript**: Dynamic interactions and API calls
- **Font Awesome**: Beautiful icons
- **Google Fonts**: Poppins typography

## 📊 AI Planning Algorithm

The Smart Task Planner uses sophisticated logic to:

1. **Detect Project Type**: Analyzes goal keywords to determine optimal phase structure
2. **Parse Duration**: Extracts timeline from natural language (days, weeks, months)
3. **Generate Phases**: Creates logical workflow phases based on project type
4. **Allocate Time**: Distributes duration intelligently across phases
5. **Create Tasks**: Generates detailed tasks with descriptions and priorities
6. **Build Dependencies**: Establishes task relationships for optimal sequencing
7. **Set Milestones**: Identifies key checkpoints throughout the project

## 🎯 Example Use Cases

### Product Launch
- Market research and competitive analysis
- Product requirements and specifications
- Design and prototyping
- Development and testing
- Marketing materials and campaigns
- Deployment and monitoring

### App Development
- Planning and user research
- UI/UX design and prototyping
- Frontend and backend development
- Integration testing
- Deployment and launch

### Marketing Campaign
- Research and strategy
- Content creation
- Channel setup
- Campaign execution
- Performance analysis

## 🌟 Advanced Features

- **Dependency Tracking**: Visual indicators for task dependencies
- **Priority System**: High/Medium/Low priority badges
- **Date Calculations**: Automatic start/end date computation
- **Progress Timeline**: Visual representation of project flow
- **Milestone Highlighting**: Key achievements marked clearly
- **Print-Friendly**: Optimized styles for printing plans

## 🔧 Customization

### Modify Phases
Edit `app.py` → `phases_templates` dictionary to add custom project types

### Change Theme Colors
Edit `static/styles.css` → `:root` variables for color customization

### Add Task Templates
Edit `app.py` → `task_templates` dictionary for custom task structures

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in app.py (last line)
app.run(debug=True, port=5001)  # Use different port
```

**Modules not found?**
```bash
pip install -r requirements.txt --upgrade
```

**Styling not loading?**
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that static folder contains styles.css

## 📄 License

This project is open source and available for educational and commercial use.

## 🙏 Credits

- **Design Inspiration**: Glassmorphism trend
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Poppins)

## 🚀 Future Enhancements

- [ ] Database integration for saving plans
- [ ] User authentication
- [ ] Collaborative planning features
- [ ] Export to PDF/Excel
- [ ] Gantt chart visualization
- [ ] Email reminders for milestones
- [ ] Integration with project management tools

## 💬 Support

For issues or questions, please create an issue in the repository.

---

**Made with ❤️ using Flask, AI, and Modern Web Technologies**

⭐ **Star this project if you found it helpful!**
