// ====================================
// SMART TASK PLANNER - JAVASCRIPT
// Dynamic Plan Generation & UI Interaction
// Google AI Enhanced
// ====================================

// Global variables
let currentPlan = null;
let googleAIAvailable = false;

// DOM Elements
const goalInput = document.getElementById('goalInput');
const generateBtn = document.getElementById('generateBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const exampleChips = document.querySelectorAll('.chip');
const newPlanBtn = document.getElementById('newPlanBtn');
const downloadBtn = document.getElementById('downloadBtn');
const aiBadge = document.getElementById('aiBadge');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check API status
    checkAPIStatus();
    
    // Example chip clicks
    exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const example = chip.getAttribute('data-example');
            goalInput.value = example;
            goalInput.focus();
        });
    });

    // Generate button
    generateBtn.addEventListener('click', generatePlan);

    // Enter key in textarea
    goalInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generatePlan();
        }
    });

    // New plan button
    newPlanBtn.addEventListener('click', resetForm);

    // Download button
    downloadBtn.addEventListener('click', downloadPlanJSON);

    // Auto-resize textarea
    goalInput.addEventListener('input', () => {
        goalInput.style.height = 'auto';
        goalInput.style.height = goalInput.scrollHeight + 'px';
    });
});

// ===== API STATUS CHECK =====

async function checkAPIStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        googleAIAvailable = data.google_ai;
        
        if (googleAIAvailable && aiBadge) {
            aiBadge.style.display = 'inline-flex';
            console.log('✅ Google AI Enhanced Mode Active');
        }
    } catch (error) {
        console.log('⚠️ API status check failed');
    }
}

// ===== MAIN FUNCTIONS =====

async function generatePlan() {
    const goal = goalInput.value.trim();

    if (!goal) {
        showNotification('Please enter a goal', 'error');
        goalInput.focus();
        return;
    }

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ goal }),
        });

        if (!response.ok) {
            throw new Error('Failed to generate plan');
        }

        const plan = await response.json();
        currentPlan = plan;

        // Hide loading, show results
        hideLoading();
        displayPlan(plan);

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showNotification('Failed to generate plan. Please try again.', 'error');
    }
}

function displayPlan(plan) {
    // Show results section
    resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Display overview
    document.getElementById('planGoal').textContent = plan.goal;
    document.getElementById('planDuration').textContent = `Total Duration: ${plan.total_duration}`;
    document.getElementById('startDate').textContent = formatDate(plan.start_date);
    document.getElementById('endDate').textContent = formatDate(plan.end_date);
    document.getElementById('totalPhases').textContent = plan.phases.length;

    // Display timeline
    displayTimeline(plan);

    // Display phases
    displayPhases(plan.phases);

    // Display milestones
    displayMilestones(plan.summary.milestones);

    // Display summary
    document.getElementById('summaryRemarks').textContent = plan.summary.remarks;
}

function displayTimeline(plan) {
    const container = document.getElementById('timelineProgress');
    container.innerHTML = '';

    const totalDuration = parseInt(plan.total_duration);

    plan.phases.forEach((phase, index) => {
        const phaseDuration = calculatePhaseDuration(phase.tasks);
        const percentage = (phaseDuration / totalDuration) * 100;

        const bar = document.createElement('div');
        bar.className = 'timeline-bar';
        bar.style.animationDelay = `${index * 0.1}s`;

        bar.innerHTML = `
            <div class="timeline-phase-name">${phase.phase}</div>
            <div class="timeline-bar-track">
                <div class="timeline-bar-fill" style="width: 0%;" data-width="${percentage}%"></div>
            </div>
            <div class="timeline-duration">${phaseDuration} day${phaseDuration !== 1 ? 's' : ''}</div>
        `;

        container.appendChild(bar);

        // Animate bar fill
        setTimeout(() => {
            const fill = bar.querySelector('.timeline-bar-fill');
            fill.style.width = fill.getAttribute('data-width');
        }, 100 + (index * 100));
    });
}

function displayPhases(phases) {
    const container = document.getElementById('phasesContainer');
    container.innerHTML = '';

    phases.forEach((phase, index) => {
        const phaseCard = createPhaseCard(phase, index);
        container.appendChild(phaseCard);
    });
}

function createPhaseCard(phase, index) {
    const card = document.createElement('div');
    card.className = 'phase-card';
    card.style.animationDelay = `${index * 0.1}s`;

    const taskCount = phase.tasks.length;
    const phaseDuration = calculatePhaseDuration(phase.tasks);

    card.innerHTML = `
        <div class="phase-header">
            <div class="phase-info">
                <div class="phase-icon">
                    <i class="${getPhaseIcon(phase.phase)}"></i>
                </div>
                <div class="phase-details">
                    <h3>${phase.phase}</h3>
                    <div class="phase-meta">
                        <span><i class="fas fa-tasks"></i> ${taskCount} task${taskCount !== 1 ? 's' : ''}</span>
                        <span><i class="fas fa-clock"></i> ${phaseDuration} day${phaseDuration !== 1 ? 's' : ''}</span>
                    </div>
                </div>
            </div>
            <i class="fas fa-chevron-down phase-toggle"></i>
        </div>
        <div class="phase-tasks">
            <div class="task-list">
                ${phase.tasks.map(task => createTaskHTML(task)).join('')}
            </div>
        </div>
    `;

    // Toggle functionality
    const header = card.querySelector('.phase-header');
    header.addEventListener('click', () => {
        card.classList.toggle('expanded');
    });

    return card;
}

function createTaskHTML(task) {
    const hasDependencies = task.dependencies && task.dependencies.length > 0;
    const duration = parseInt(task.duration);

    return `
        <div class="task-item">
            <div class="task-checkbox"></div>
            <div class="task-content">
                <div class="task-header">
                    <span class="task-name">${task.task_name}</span>
                    <span class="priority-badge priority-${task.priority.toLowerCase()}">${task.priority}</span>
                </div>
                <p class="task-description">${task.description}</p>
                <div class="task-meta">
                    <span><i class="fas fa-calendar-day"></i> ${formatDate(task.start_date)} - ${formatDate(task.end_date)}</span>
                    <span><i class="fas fa-hourglass-half"></i> ${task.duration}</span>
                </div>
                ${hasDependencies ? `
                    <div class="task-dependencies">
                        <span style="color: var(--text-muted); font-size: 0.85rem;">
                            <i class="fas fa-link"></i> Depends on:
                        </span>
                        ${task.dependencies.map(dep => `<span class="dependency-tag">${dep}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function displayMilestones(milestones) {
    const container = document.getElementById('milestonesContainer');
    container.innerHTML = '';

    milestones.forEach((milestone, index) => {
        const item = document.createElement('div');
        item.className = 'milestone-item fade-in';
        item.style.animationDelay = `${index * 0.1}s`;

        item.innerHTML = `
            <div class="milestone-icon">
                <i class="fas fa-flag-checkered"></i>
            </div>
            <div class="milestone-text">${milestone}</div>
        `;

        container.appendChild(item);
    });
}

// ===== UTILITY FUNCTIONS =====

function calculatePhaseDuration(tasks) {
    if (!tasks || tasks.length === 0) return 0;

    const lastTask = tasks[tasks.length - 1];
    const firstTask = tasks[0];

    const start = new Date(firstTask.start_date);
    const end = new Date(lastTask.end_date);

    return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function getPhaseIcon(phaseName) {
    const icons = {
        'Planning': 'fas fa-lightbulb',
        'Design': 'fas fa-palette',
        'UI/UX Design': 'fas fa-pencil-ruler',
        'Development': 'fas fa-code',
        'Frontend Development': 'fas fa-laptop-code',
        'Backend Development': 'fas fa-server',
        'Testing': 'fas fa-vial',
        'Marketing': 'fas fa-bullhorn',
        'Deployment': 'fas fa-rocket',
        'Research': 'fas fa-search',
        'Strategy': 'fas fa-chess',
        'Content Creation': 'fas fa-pen-fancy',
        'Channel Setup': 'fas fa-share-alt',
        'Execution': 'fas fa-play',
        'Analysis': 'fas fa-chart-bar',
        'Review': 'fas fa-clipboard-check',
        'Completion': 'fas fa-check-circle',
        'Concept': 'fas fa-brain',
        'Logistics': 'fas fa-truck',
        'Follow-up': 'fas fa-redo'
    };

    return icons[phaseName] || 'fas fa-tasks';
}

function showLoading() {
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Generating...</span>';

    // Scroll to loading
    setTimeout(() => {
        loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

function hideLoading() {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-magic"></i><span>Generate Plan</span>';
}

function resetForm() {
    goalInput.value = '';
    resultsSection.classList.add('hidden');
    currentPlan = null;

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Focus input
    setTimeout(() => {
        goalInput.focus();
    }, 500);
}

function downloadPlanJSON() {
    if (!currentPlan) {
        showNotification('No plan to download', 'error');
        return;
    }

    const dataStr = JSON.stringify(currentPlan, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `task-plan-${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showNotification('Plan downloaded successfully!', 'success');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(16, 185, 129, 0.9)'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    `;

    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .notification {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .notification i {
        font-size: 1.2rem;
    }
`;
document.head.appendChild(style);

// ===== EASTER EGG: Konami Code =====
let konamiCode = [];
const konamiPattern = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-10);

    if (konamiCode.join(',') === konamiPattern.join(',')) {
        activateEasterEgg();
    }
});

function activateEasterEgg() {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    `;

    for (let i = 0; i < 100; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background: ${['#7c3aed', '#6366f1', '#a78bfa', '#818cf8'][Math.floor(Math.random() * 4)]};
            top: -20px;
            left: ${Math.random() * 100}%;
            animation: fall ${2 + Math.random() * 3}s linear;
            border-radius: 50%;
        `;
        confetti.appendChild(particle);
    }

    const fallAnimation = document.createElement('style');
    fallAnimation.textContent = `
        @keyframes fall {
            to {
                transform: translateY(100vh) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(fallAnimation);
    document.body.appendChild(confetti);

    setTimeout(() => {
        document.body.removeChild(confetti);
    }, 5000);

    showNotification('🎉 You found the secret! Enjoy the confetti!', 'success');
}
