#!/bin/bash

# Claude-Flow Swarm Initialization Script
# This script stores swarm configuration for Claude to use

SWARM_CONFIG_FILE=".claude-flow/current_swarm.json"

# Function to create new swarm config
create_swarm() {
    local swarm_name=$1
    local topology=${2:-"hierarchical"}
    local max_agents=${3:-8}
    
    echo "Creating Claude-Flow swarm configuration..."
    
    mkdir -p .claude-flow
    
    cat > $SWARM_CONFIG_FILE << EOF
{
    "swarm_name": "$swarm_name",
    "topology": "$topology",
    "max_agents": $max_agents,
    "created_at": "$(date -Iseconds)",
    "agents": [
        {"type": "coordinator", "name": "Queen Coordinator"},
        {"type": "researcher", "name": "Researcher Worker 1"},
        {"type": "coder", "name": "Coder Worker 2"},
        {"type": "analyst", "name": "Analyst Worker 3"},
        {"type": "tester", "name": "Tester Worker 4"},
        {"type": "architect", "name": "Architect Worker 5"},
        {"type": "reviewer", "name": "Reviewer Worker 6"},
        {"type": "optimizer", "name": "Optimizer Worker 7"},
        {"type": "documenter", "name": "Documenter Worker 8"}
    ],
    "instructions": "Tell Claude: 'Initialize swarm from .claude-flow/current_swarm.json'"
}
EOF
    
    echo "✅ Swarm configuration created!"
    echo "📍 Configuration saved to: $SWARM_CONFIG_FILE"
    echo ""
    echo "To use this swarm in Claude, say:"
    echo "  'Load swarm configuration from .claude-flow/current_swarm.json'"
    echo "  'Initialize swarm: $swarm_name'"
}

# Function to load existing swarm
load_swarm() {
    if [ -f $SWARM_CONFIG_FILE ]; then
        echo "📋 Current swarm configuration:"
        cat $SWARM_CONFIG_FILE | python3 -m json.tool
        echo ""
        echo "To use this swarm in Claude, say:"
        echo "  'Load my saved swarm configuration'"
    else
        echo "❌ No swarm configuration found!"
        echo "Create one with: $0 create <swarm_name>"
    fi
}

# Main script logic
case "$1" in
    create)
        create_swarm "${2:-BookGenerator}" "${3:-hierarchical}" "${4:-8}"
        ;;
    load)
        load_swarm
        ;;
    *)
        echo "Claude-Flow Swarm Manager"
        echo "========================="
        echo ""
        echo "Usage:"
        echo "  $0 create <name> [topology] [agents]  - Create new swarm config"
        echo "  $0 load                                - Load existing swarm"
        echo ""
        echo "Examples:"
        echo "  $0 create BookGenerator hierarchical 10"
        echo "  $0 create TestSwarm mesh 5"
        echo "  $0 load"
        echo ""
        echo "Topologies: hierarchical, mesh, ring, star"
        ;;
esac