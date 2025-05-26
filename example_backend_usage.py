"""
Example Flask backend demonstrating how to use the dynamic_sprint.html template
with personalized variables for different team members.

This shows how to replace the hardcoded sprint boards with a dynamic template
that receives variables from the backend.
"""

from flask import Flask, render_template

app = Flask(__name__)

# Define team member configurations
TEAM_MEMBERS = {
    'fintan': {
        'member_name': 'Fintan',
        'assignee': 'fintan',
        'primary_color': '#0052cc',
        'secondary_color': '#0747a6',
        'drag_over_bg': '#e3f2fd',
        'sprint_name': 'Innovation Sprint',
        'sprint_duration': '3 weeks'
    },
    'jack': {
        'member_name': 'Jack',
        'assignee': 'jack',
        'primary_color': '#ff8b00',
        'secondary_color': '#ff5722',
        'drag_over_bg': '#fff3e0',
        'sprint_name': 'Development Sprint',
        'sprint_duration': '2 weeks'
    },
    'micheal': {
        'member_name': 'Micheál',
        'assignee': 'micheal',
        'primary_color': '#36b37e',
        'secondary_color': '#00875a',
        'drag_over_bg': '#e3fcef',
        'sprint_name': 'Testing Sprint',
        'sprint_duration': '2 weeks'
    },
    'new_member': {
        'member_name': 'Sarah',
        'assignee': 'sarah',
        'primary_color': '#8B5CF6',
        'secondary_color': '#7C3AED',
        'drag_over_bg': '#f3e8ff',
        'sprint_name': 'Design Sprint',
        'sprint_duration': '1 week'
    }
}

@app.route('/sprint/<member_id>')
def dynamic_sprint_board(member_id):
    """
    Dynamic sprint board route that serves personalized sprint boards
    using the same template with different variables.
    
    Usage examples:
    - /sprint/fintan  -> Fintan's personalized board (blue theme)
    - /sprint/jack    -> Jack's personalized board (orange theme)  
    - /sprint/micheal -> Micheál's personalized board (green theme)
    - /sprint/new_member -> Sarah's personalized board (purple theme)
    """
    
    # Get member configuration or use default
    member_config = TEAM_MEMBERS.get(member_id, {
        'member_name': member_id.title(),
        'assignee': member_id,
        'primary_color': '#0052cc',
        'secondary_color': '#0747a6',
        'drag_over_bg': '#e3f2fd',
        'sprint_name': 'Default Sprint',
        'sprint_duration': '2 weeks'
    })
    
    # Add navigation context
    member_config['active_page'] = 'sprint'
    
    return render_template('dynamic_sprint.html', **member_config)

@app.route('/sprint')
def sprint_board_selector():
    """
    Sprint board selector page that shows available team members
    """
    return render_template('sprint_selector.html', team_members=TEAM_MEMBERS)

# Individual routes for backward compatibility
@app.route('/fintan-sprint')
def fintan_sprint():
    return dynamic_sprint_board('fintan')

@app.route('/jack-sprint')
def jack_sprint():
    return dynamic_sprint_board('jack')

@app.route('/micheal-sprint')
def micheal_sprint():
    return dynamic_sprint_board('micheal')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

"""
Key Benefits of this approach:

1. **Single Template**: One template file instead of three nearly identical ones
2. **Easy Scaling**: Adding new team members requires only adding their config
3. **Consistent Updates**: Changes to functionality apply to all team members
4. **Maintainable**: Reduces code duplication and maintenance overhead
5. **Flexible**: Easy to customize colors, names, sprint details per member

Variables passed to the template:
- member_name: Display name for the team member
- assignee: Internal ID used for filtering tasks
- primary_color: Main theme color for the board
- secondary_color: Secondary color for gradients
- drag_over_bg: Background color when dragging tasks
- sprint_name: Custom sprint name
- sprint_duration: Sprint duration text
- active_page: For navigation highlighting

Example configurations show different color themes:
- Fintan: Blue theme (#0052cc)
- Jack: Orange theme (#ff8b00)  
- Micheál: Green theme (#36b37e)
- Sarah: Purple theme (#8B5CF6)
""" 