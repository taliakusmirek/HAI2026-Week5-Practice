# Enhanced Human-Agent Data Analysis Tool

This project demonstrates an advanced human-agent collaboration system with real-time guidance and steering capabilities for autonomous data analysis.

## 🚀 Key Features

### Real-time Guidance System
- **Guidance Levels**: Choose from None, Light, Moderate, or Strong guidance
- **Proactive Steering**: Guide the agent's analysis approach before and during execution
- **Dynamic Focus Areas**: Specify what aspects of the data to focus on
- **Preferred Approaches**: Select analysis methods you want the agent to prioritize

### Enhanced Human-Agent Collaboration
- **Multi-phase Approval**: Tool execution approval with detailed feedback
- **Guidance Integration**: User guidance dynamically injected into agent reasoning
- **Real-time Updates**: Update guidance mid-analysis to steer the agent
- **Comprehensive Feedback Loop**: Rich interaction beyond simple binary approval

## 🛠️ Technology Stack

- **Streamlit**: Web interface framework
- **OpenAI GPT-4o-mini**: Function calling and structured outputs
- **Pydantic**: Data validation and structured parsing
- **ReAct Pattern**: Reasoning and Acting loop for autonomous problem-solving

## 📦 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd HAI2026-Week5-Practice
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - The `.env` file is already included with your OpenAI API key
   - For security, consider using your own API key

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🌐 Deployment to Streamlit Community Cloud

### Option 1: Using the included secrets (Quick Start)

1. **Fork or upload this repository to GitHub**
2. **Go to [Streamlit Community Cloud](https://share.streamlit.io/)**
3. **Click "New app" and connect your GitHub account**
4. **Select your repository and branch**
5. **Main file path**: `app.py`
6. **Click "Deploy"**

The included `.streamlit/secrets.toml` file contains your API key and will be automatically used.

### Option 2: Manual Secret Configuration (Recommended for Production)

1. **Remove the API key from `.streamlit/secrets.toml`**
2. **In Streamlit Community Cloud dashboard:**
   - Go to your app settings
   - Click "Secrets"
   - Add your OpenAI API key:
   ```toml
   [openai]
   api_key = "your-api-key-here"
   ```

### Option 3: Using Environment Variables

1. **In Streamlit Community Cloud dashboard:**
   - Go to your app settings  
   - Click "Secrets"
   - Add:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

## 🎯 How to Use the Guidance System

1. **Start the application** and load the movie dataset
2. **Set your guidance preferences** in the left panel:
   - **Guidance Level**: How strictly the agent should follow your guidance
   - **General Guidance**: Overall approach or constraints
   - **Analysis Focus**: Specific areas to concentrate on
   - **Preferred Approaches**: Methods to prioritize

3. **Ask your question** about the data
4. **Apply guidance** before or during analysis
5. **Review agent actions** and approve/reject as needed
6. **Update guidance in real-time** to steer the analysis

## 📊 Example Guidance Scenarios

### Statistical Analysis Focus
- **Guidance Level**: Moderate
- **General Guidance**: "Focus on statistical significance and confidence intervals"
- **Analysis Focus**: "rating patterns, genre correlations"
- **Preferred Approaches**: "statistical analysis, comparison"

### Visualization-First Approach  
- **Guidance Level**: Strong
- **General Guidance**: "Prioritize data visualization over raw numbers"
- **Analysis Focus**: "visual trends, comparative charts"
- **Preferred Approaches**: "data visualization, trend analysis"

### Quick Insights Mode
- **Guidance Level**: Light
- **General Guidance**: "Be concise and focus on the most important findings"
- **Analysis Focus**: "key patterns, outliers"
- **Preferred Approaches**: "aggregation, filtering"

## 🔧 Configuration Files

- **`.env`**: Local development environment variables
- **`.streamlit/secrets.toml`**: Cloud deployment secrets
- **`requirements.txt`**: Python dependencies
- **`app.py`**: Main application entry point
- **`agent_panel.py`**: Core agent logic and guidance system

## 🚨 Security Notes

- The API key is included for convenience but should be secured in production
- Never commit real API keys to public repositories
- Use Streamlit's built-in secret management for production deployments
- Consider API rate limits and costs when running the application

## 🤖 Agent Architecture

The enhanced system uses a sophisticated multi-phase approach:

1. **Guidance Integration**: User guidance dynamically injected into system prompts
2. **ReAct Loop**: Reasoning and Acting with tool selection
3. **Approval Gates**: Human oversight for tool execution
4. **Feedback Integration**: User feedback incorporated into subsequent reasoning
5. **Real-time Steering**: Guidance updates affect ongoing analysis

## 📈 Advanced Features

- **Dynamic Prompt Engineering**: Guidance affects agent behavior in real-time
- **Multi-modal Feedback**: Text guidance + structured preferences
- **Adaptive Control**: Different guidance levels for varying user expertise
- **Comprehensive Logging**: Full trace of guidance updates and agent responses

## 🎨 UI/UX Enhancements

- **Two-column layout**: Guidance panel + main analysis area
- **Real-time status**: Current guidance level and active settings
- **Visual feedback**: Guidance updates shown in reasoning trace
- **Intuitive controls**: Easy-to-use guidance configuration

## 📝 License

This project is part of the HAI2026 course and demonstrates advanced human-agent interaction patterns in autonomous systems.
