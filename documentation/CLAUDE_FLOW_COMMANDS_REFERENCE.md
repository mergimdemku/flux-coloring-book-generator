# 📚 CLAUDE-FLOW AGENT COMMAND REFERENCE GUIDE
**Last Updated: September 1, 2025**  
**Version: 1.0**  
**Project: Kids Content Creator - Coloring Book Generator**

---

## 🎯 SWARM MANAGEMENT COMMANDS

### 1. Initialize a New Swarm
```python
mcp__claude-flow__swarm_init
```
**Parameters:**
- `topology`: "hierarchical" | "mesh" | "ring" | "star"
- `maxAgents`: Number (default: 8, max: 16)
- `strategy`: "auto" | "manual" | "adaptive"

**When to use:** Start of project or when creating new agent team

**Example Commands:**
```
"Initialize a hierarchical swarm with 10 agents using auto strategy"
"Create a mesh network swarm for distributed processing"
"Set up a star topology swarm with 5 agents"
```

### 2. Check Swarm Status
```python
mcp__claude-flow__swarm_status
```
**Parameters:**
- `swarmId`: (optional) Specific swarm ID

**When to use:** Monitor active swarms and agent availability

**Example Commands:**
```
"Show me the current swarm status"
"Check status of swarm_1756705529831_vwz8lr4az"
```

### 3. Scale Swarm Size
```python
mcp__claude-flow__swarm_scale
```
**Parameters:**
- `swarmId`: Swarm to scale
- `targetSize`: New number of agents

**When to use:** Increase/decrease agent count based on workload

**Example Commands:**
```
"Scale the swarm up to 12 agents"
"Reduce swarm size to 5 agents"
```

### 4. Destroy Swarm
```python
mcp__claude-flow__swarm_destroy
```
**Parameters:**
- `swarmId`: Swarm to terminate

**When to use:** Clean shutdown of swarm operations

**Example Commands:**
```
"Shutdown the current swarm"
"Destroy swarm_1756705529831_vwz8lr4az"
```

---

## 🤖 AGENT MANAGEMENT COMMANDS

### 5. Spawn New Agent
```python
mcp__claude-flow__agent_spawn
```
**Parameters:**
- `type`: "coordinator" | "analyst" | "optimizer" | "documenter" | "monitor" | "specialist" | "architect" | "task-orchestrator" | "code-analyzer" | "perf-analyzer" | "api-docs" | "performance-benchmarker" | "system-architect" | "researcher" | "coder" | "tester" | "reviewer"
- `name`: Custom agent name
- `swarmId`: Target swarm
- `capabilities`: Array of capabilities

**When to use:** Add specialized agents to swarm

**Example Commands:**
```
"Spawn a researcher agent named DataHunter with web-scraping capabilities"
"Create a coder agent specialized in Python"
"Add an optimizer agent for performance tuning"
```

### 6. List All Agents
```python
mcp__claude-flow__agent_list
```
**Parameters:**
- `swarmId`: (optional) Specific swarm

**When to use:** See all available agents and their status

**Example Commands:**
```
"Show me all active agents"
"List agents in the current swarm"
```

### 7. Get Agent Metrics
```python
mcp__claude-flow__agent_metrics
```
**Parameters:**
- `agentId`: Specific agent ID

**When to use:** Monitor individual agent performance

**Example Commands:**
```
"Show metrics for the coordinator agent"
"Get performance data for agent_1756705554977_nssbyg"
```

### 8. Dynamic Agent Creation
```python
mcp__claude-flow__daa_agent_create
```
**Parameters:**
- `agent_type`: Type of agent
- `capabilities`: Array of capabilities
- `resources`: Resource allocation

**When to use:** Create custom agents with specific skills

**Example Commands:**
```
"Create a dynamic agent for image processing with GPU resources"
"Build a custom agent for database operations"
```

### 9. Agent Lifecycle Management
```python
mcp__claude-flow__daa_lifecycle_manage
```
**Parameters:**
- `agentId`: Target agent
- `action`: "start" | "stop" | "restart" | "pause" | "resume"

**When to use:** Control agent states

**Example Commands:**
```
"Pause the analyzer agent"
"Restart the coder agent"
"Stop agent_1756705554977_nssbyg"
```

---

## 📋 TASK ORCHESTRATION COMMANDS

### 10. Orchestrate Complex Tasks
```python
mcp__claude-flow__task_orchestrate
```
**Parameters:**
- `task`: Main task description
- `strategy`: "parallel" | "sequential" | "adaptive" | "balanced"
- `priority`: "low" | "medium" | "high" | "critical"
- `dependencies`: Array of subtasks

**When to use:** Coordinate multiple agents on complex projects

**Example Commands:**
```
"Orchestrate parallel task: Build complete web application with dependencies: [frontend, backend, database, testing, documentation]"
"Run sequential task: Deploy application with steps: [test, build, deploy, verify]"
"Execute adaptive strategy for: Optimize system performance"
```

### 11. Check Task Status
```python
mcp__claude-flow__task_status
```
**Parameters:**
- `taskId`: Task to check

**When to use:** Monitor ongoing task progress

**Example Commands:**
```
"Check status of task_1756705779564_z4xp6bt7d"
"Show me the current task progress"
```

### 12. Get Task Results
```python
mcp__claude-flow__task_results
```
**Parameters:**
- `taskId`: Completed task ID

**When to use:** Retrieve outputs from completed tasks

**Example Commands:**
```
"Get results from the optimization task"
"Show output of task_1756705779564_z4xp6bt7d"
```

### 13. Parallel Task Execution
```python
mcp__claude-flow__parallel_execute
```
**Parameters:**
- `tasks`: Array of task objects with id, description, agent

**When to use:** Run multiple independent tasks simultaneously

**Example Commands:**
```
"Execute parallel tasks: [
  {id: 'analyze', description: 'Analyze codebase', agent: 'analyst'},
  {id: 'test', description: 'Run tests', agent: 'tester'},
  {id: 'docs', description: 'Update documentation', agent: 'documenter'}
]"
```

### 14. Batch Processing
```python
mcp__claude-flow__batch_process
```
**Parameters:**
- `items`: Array of items to process
- `operation`: Operation to perform

**When to use:** Process multiple similar items

**Example Commands:**
```
"Batch process 50 images for coloring book generation"
"Process batch of JSON stories through pipeline"
```

---

## 🔄 WORKFLOW AUTOMATION COMMANDS

### 15. Create Workflow
```python
mcp__claude-flow__workflow_create
```
**Parameters:**
- `name`: Workflow name
- `steps`: Array of step objects
- `triggers`: Array of trigger conditions

**When to use:** Define reusable task sequences

**Example Commands:**
```
"Create workflow 'DailyBookGeneration' with steps: [generate story, create images, process lines, generate PDF] triggered daily"
"Build workflow for automated testing pipeline"
```

### 16. Execute Workflow
```python
mcp__claude-flow__workflow_execute
```
**Parameters:**
- `workflowId`: Workflow to run
- `params`: Execution parameters

**When to use:** Run predefined workflows

**Example Commands:**
```
"Execute workflow_1756705808072_ctbno5 with params: {theme: 'animals', count: 5}"
"Run the DailyBookGeneration workflow"
```

### 17. Export Workflow
```python
mcp__claude-flow__workflow_export
```
**Parameters:**
- `workflowId`: Workflow to export
- `format`: "json" | "yaml" | "xml"

**When to use:** Save workflow definitions

**Example Commands:**
```
"Export the book generation workflow as JSON"
"Save workflow_1756705808072_ctbno5 in YAML format"
```

### 18. Workflow Templates
```python
mcp__claude-flow__workflow_template
```
**Parameters:**
- `action`: "create" | "list" | "apply" | "delete"
- `template`: Template object

**When to use:** Manage reusable workflow templates

**Example Commands:**
```
"Create template from current workflow"
"List all available workflow templates"
"Apply the BookGeneration template"
```

---

## 🧠 MEMORY & COORDINATION COMMANDS

### 19. Memory Operations
```python
mcp__claude-flow__memory_usage
```
**Parameters:**
- `action`: "store" | "retrieve" | "list" | "delete" | "search"
- `key`: Memory key
- `value`: Data to store
- `namespace`: Memory namespace
- `ttl`: Time to live (optional)

**When to use:** Share data between agents

**Example Commands:**
```
"Store task results in memory with key 'analysis-results'"
"Retrieve shared configuration from namespace 'swarm-config'"
"List all memory keys in current namespace"
```

### 20. Memory Search
```python
mcp__claude-flow__memory_search
```
**Parameters:**
- `pattern`: Search pattern
- `namespace`: (optional) Specific namespace
- `limit`: Max results (default: 10)

**When to use:** Find stored information

**Example Commands:**
```
"Search memory for pattern 'story-*'"
"Find all keys containing 'config'"
```

### 21. Inter-Agent Communication
```python
mcp__claude-flow__daa_communication
```
**Parameters:**
- `from`: Sender agent ID
- `to`: Receiver agent ID
- `message`: Message object

**When to use:** Direct agent-to-agent messaging

**Example Commands:**
```
"Send message from coordinator to all workers: 'Begin phase 2'"
"Have analyst agent send results to reviewer agent"
```

### 22. Consensus Mechanisms
```python
mcp__claude-flow__daa_consensus
```
**Parameters:**
- `agents`: Array of voting agents
- `proposal`: Proposal object

**When to use:** Democratic decision making

**Example Commands:**
```
"Get consensus from all agents on: 'Should we implement feature X?'"
"Have technical agents vote on architecture decision"
```

### 23. Coordination Sync
```python
mcp__claude-flow__coordination_sync
```
**Parameters:**
- `swarmId`: Swarm to synchronize

**When to use:** Ensure all agents are synchronized

**Example Commands:**
```
"Synchronize all agents in the swarm"
"Sync coordination state before major task"
```

### 24. Load Balancing
```python
mcp__claude-flow__load_balance
```
**Parameters:**
- `swarmId`: Target swarm
- `tasks`: Array of tasks to distribute

**When to use:** Automatically distribute work

**Example Commands:**
```
"Load balance 20 image generation tasks across available agents"
"Distribute story processing tasks evenly"
```

---

## 🤖 AI/NEURAL COMMANDS

### 25. Neural Training
```python
mcp__claude-flow__neural_train
```
**Parameters:**
- `pattern_type`: "coordination" | "optimization" | "prediction"
- `training_data`: Training dataset
- `epochs`: Number of epochs (default: 50)

**When to use:** Train AI patterns for agent behavior

**Example Commands:**
```
"Train coordination pattern with team performance data"
"Train optimization model for resource allocation"
```

### 26. Neural Prediction
```python
mcp__claude-flow__neural_predict
```
**Parameters:**
- `modelId`: Trained model ID
- `input`: Input data

**When to use:** Get AI predictions

**Example Commands:**
```
"Predict optimal agent count for current workload"
"Predict task completion time"
```

### 27. Pattern Recognition
```python
mcp__claude-flow__pattern_recognize
```
**Parameters:**
- `data`: Data to analyze
- `patterns`: (optional) Specific patterns to look for

**When to use:** Identify patterns in data

**Example Commands:**
```
"Recognize patterns in generation failures"
"Identify recurring issues in pipeline"
```

### 28. Neural Status Check
```python
mcp__claude-flow__neural_status
```
**Parameters:**
- `modelId`: (optional) Specific model ID

**When to use:** Check neural network status

**Example Commands:**
```
"Check neural network status"
"Get status of model_xyz"
```

---

## 📊 MONITORING & ANALYTICS COMMANDS

### 29. Swarm Monitoring
```python
mcp__claude-flow__swarm_monitor
```
**Parameters:**
- `swarmId`: Swarm to monitor
- `interval`: Update interval in ms

**When to use:** Real-time swarm monitoring

**Example Commands:**
```
"Monitor swarm with 5 second updates"
"Start real-time monitoring dashboard"
```

### 30. Performance Report
```python
mcp__claude-flow__performance_report
```
**Parameters:**
- `format`: "summary" | "detailed" | "json"
- `timeframe`: "24h" | "7d" | "30d"

**When to use:** Generate performance reports

**Example Commands:**
```
"Generate detailed performance report for last 7 days"
"Get summary report for past 24 hours"
```

### 31. Bottleneck Analysis
```python
mcp__claude-flow__bottleneck_analyze
```
**Parameters:**
- `component`: Component to analyze
- `metrics`: Metrics to examine

**When to use:** Identify performance issues

**Example Commands:**
```
"Analyze bottlenecks in image generation pipeline"
"Find performance issues in PDF creation"
```

### 32. Error Analysis
```python
mcp__claude-flow__error_analysis
```
**Parameters:**
- `logs`: Log entries to analyze

**When to use:** Understand failure patterns

**Example Commands:**
```
"Analyze errors from last 100 generations"
"Find root cause of pipeline failures"
```

### 33. Token Usage Analysis
```python
mcp__claude-flow__token_usage
```
**Parameters:**
- `operation`: Specific operation to analyze
- `timeframe`: Time period (default: "24h")

**When to use:** Monitor token consumption

**Example Commands:**
```
"Analyze token usage for story generation"
"Get token consumption for last 7 days"
```

---

## 🔧 SYSTEM MANAGEMENT COMMANDS

### 34. Health Check
```python
mcp__claude-flow__health_check
```
**Parameters:**
- `components`: Array of components to check

**When to use:** System health verification

**Example Commands:**
```
"Run full system health check"
"Check health of [agents, memory, neural, workflows]"
```

### 35. Backup System
```python
mcp__claude-flow__backup_create
```
**Parameters:**
- `components`: Components to backup
- `destination`: Backup location

**When to use:** Create system backups

**Example Commands:**
```
"Backup all workflows and configurations"
"Create full system backup to ./backups/"
```

### 36. Restore System
```python
mcp__claude-flow__restore_system
```
**Parameters:**
- `backupId`: Backup to restore

**When to use:** Restore from backup

**Example Commands:**
```
"Restore system from backup_20240831"
"Restore workflows from last checkpoint"
```

### 37. Configuration Management
```python
mcp__claude-flow__config_manage
```
**Parameters:**
- `action`: "get" | "set" | "update" | "reset"
- `config`: Configuration object

**When to use:** Manage system configuration

**Example Commands:**
```
"Get current configuration"
"Update config with new API endpoints"
"Reset configuration to defaults"
```

---

## 🚀 SPECIALIZED MODES

### 38. SPARC Development Mode
```python
mcp__claude-flow__sparc_mode
```
**Parameters:**
- `mode`: "dev" | "api" | "ui" | "test" | "refactor"
- `task_description`: What to build/fix
- `options`: Mode-specific options

**When to use:** Structured development approach

**Example Commands:**
```
"Run SPARC dev mode: Build new story generator with math themes"
"Execute SPARC refactor mode: Optimize line processing algorithm"
"Start SPARC test mode: Validate all generation paths"
```

---

## 🔌 GITHUB INTEGRATION COMMANDS

### 39. Repository Analysis
```python
mcp__claude-flow__github_repo_analyze
```
**Parameters:**
- `repo`: Repository name
- `analysis_type`: "code_quality" | "performance" | "security"

**When to use:** Analyze GitHub repositories

**Example Commands:**
```
"Analyze code quality of flux-coloring-book-generator repo"
"Run security analysis on current repository"
```

### 40. Pull Request Management
```python
mcp__claude-flow__github_pr_manage
```
**Parameters:**
- `repo`: Repository name
- `action`: "review" | "merge" | "close"
- `pr_number`: Pull request number

**When to use:** Manage pull requests

**Example Commands:**
```
"Review pull request #42 in main repo"
"Merge approved PR #38"
```

---

## 📖 PRACTICAL USAGE SCENARIOS

### Scenario 1: Start Complete Book Generation System
```bash
1. "Initialize hierarchical swarm with 8 agents"
2. "Spawn specialized agents for book creation"
3. "Create workflow for automated book generation"
4. "Execute workflow with theme: animals, pages: 20"
5. "Monitor swarm status every 10 seconds"
```

### Scenario 2: Parallel Development Tasks
```bash
"Orchestrate parallel task: Improve coloring book system with dependencies: [
  'Research new art styles',
  'Optimize FLUX prompts',
  'Test line processing',
  'Update documentation',
  'Review code quality',
  'Analyze user feedback'
] using parallel strategy with high priority"
```

### Scenario 3: Automated Pipeline with Monitoring
```bash
1. "Create workflow 'HourlyGeneration' with steps: generate, process, validate"
2. "Set triggers for every hour"
3. "Execute workflow with auto-monitoring"
4. "Generate performance report after 24 hours"
```

### Scenario 4: Smart Task Distribution
```bash
"Load balance these tasks across swarm: [
  'Generate 10 adventure stories',
  'Generate 10 learning stories',
  'Process 20 cover images',
  'Create 20 PDFs',
  'Run quality checks'
]"
```

### Scenario 5: Emergency Recovery
```bash
1. "Run health check on all components"
2. "Identify failed agents"
3. "Restart failed agents"
4. "Restore from last checkpoint"
5. "Resume workflow execution"
```

---

## 💡 TIPS & BEST PRACTICES

### Agent Management
- Always spawn agents with specific capabilities for better task matching
- Use hierarchical topology for complex projects with clear task hierarchy
- Use mesh topology for collaborative tasks requiring peer communication
- Monitor agent metrics regularly to identify overloaded agents

### Task Orchestration
- Use `parallel` strategy for independent tasks
- Use `sequential` strategy for dependent tasks
- Use `adaptive` strategy when unsure about dependencies
- Set appropriate priority levels (critical > high > medium > low)

### Memory Management
- Use namespaces to organize memory by project/component
- Set TTL for temporary data to prevent memory bloat
- Use memory search to find related data quickly
- Backup memory state before major changes

### Workflow Automation
- Create templates for frequently used workflows
- Use triggers for scheduled automation
- Export workflows for version control
- Test workflows with small datasets first

### Performance Optimization
- Run bottleneck analysis weekly
- Generate performance reports after major changes
- Use load balancing for large task batches
- Scale swarm size based on workload

### Error Handling
- Analyze error patterns to prevent recurring issues
- Set up automated recovery workflows
- Keep backups before system changes
- Monitor health checks continuously

---

## 🔗 QUICK REFERENCE TABLE

| Category | Common Commands | Usage |
|----------|----------------|-------|
| **Setup** | `swarm_init`, `agent_spawn` | Initialize system |
| **Tasks** | `task_orchestrate`, `parallel_execute` | Run operations |
| **Monitor** | `swarm_status`, `agent_metrics` | Check progress |
| **Memory** | `memory_usage`, `memory_search` | Share data |
| **Workflow** | `workflow_create`, `workflow_execute` | Automation |
| **Analysis** | `performance_report`, `error_analysis` | Optimization |
| **Backup** | `backup_create`, `restore_system` | Safety |

---

## 📞 SUPPORT & DOCUMENTATION

- **Project**: Kids Content Creator - Coloring Book Generator
- **System**: Claude-Flow Agent Orchestration
- **Version**: 1.0
- **Last Updated**: September 1, 2025

For additional help or custom implementations, refer to the project documentation in the `Documentation and Checkpoints` folder.

---

**Note**: Save this file for quick reference when working with the Claude-Flow agent system. All commands are designed to work with natural language inputs - just describe what you want to achieve!