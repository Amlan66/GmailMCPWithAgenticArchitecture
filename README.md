# 🤖 Multimodal Agent with Perception-Action-Decision-Memory (PADM) Architecture

A sophisticated AI agent system that combines mathematical computation, system automation, and communication capabilities through a modular architecture with built-in verification and reasoning.

## 🏗️ Architecture Overview

### Core Components

#### 1. 🧠 **Perception Layer** (`perception.py`)
- **Purpose**: Extracts structured facts from natural language user input
- **Capabilities**:
  - Task identification and goal extraction
  - Entity recognition (people, places, email addresses)
  - User characteristics detection (communication style: funny, formal, sarcastic)
  - Preference extraction (color preferences, format preferences)
  - Requirement parsing and constraint identification
- **Technology**: Google Gemini 2.0 Flash with structured output parsing
- **Output**: Structured facts with confidence scoring

#### 2. 🧮 **Memory Layer** (`memory.py`)
- **Purpose**: Persistent storage and retrieval of facts and context
- **Capabilities**:
  - Fact storage with categorization (entity, characteristic, preference)
  - Context-aware fact retrieval using LLM-based relevance matching
  - Memory summarization for decision context
- **Storage**: In-memory fact database with timestamp and relevance scoring
- **Integration**: Provides context to decision layer for personalized responses

#### 3. 🎯 **Decision Layer** (`decision.py`)
- **Purpose**: Intelligent tool selection and workflow orchestration
- **Capabilities**:
  - Step-by-step reasoning with explicit verification requirements
  - Tool selection based on context, memory, and user preferences
  - Structured output format enforcement (FUNCTION_CALL/FINAL_ANSWER)
  - Mandatory verification workflow for mathematical operations
- **Technology**: Enhanced system prompt with verification enforcement
- **Output**: Structured decisions with reasoning traces

#### 4. ⚡ **Action Layer** (`action.py`)
- **Purpose**: Tool execution and system interaction
- **Capabilities**:
  - **Mathematical Tools**: 15+ math operations with verification support
  - **System Automation**: Paint application control with UI automation
  - **Communication**: Gmail API integration for email sending
  - **Verification**: Built-in result validation with relative/absolute tolerance
- **Technology**: MCP (Model Context Protocol) framework with FastMCP

## 🔧 Available Tools

### Mathematical Operations
- Basic arithmetic: `add`, `subtract`, `multiply`, `divide`
- Advanced math: `power`, `sqrt`, `cbrt`, `factorial`, `log`
- Trigonometry: `sin`, `cos`, `tan`
- String processing: `strings_to_chars_to_int`, `int_list_to_exponential_sum`
- Sequences: `fibonacci_numbers`
- **Verification**: `verify` tool with smart tolerance (relative for large numbers, absolute for small)

### System Automation
- **Paint Integration**: `open_paint`, `draw_rectangle_and_text`
  - Color selection support (red, yellow, green, black)
  - Image-based UI automation using `pyautogui`
  - Rectangle drawing and text insertion

### Communication
- **Email**: `send_email` via Gmail API
  - Personalized greetings and signatures
  - Support for user communication style preferences

## ✅ Verification System

### Mandatory Verification Workflow
1. **Mathematical Operation** → 2. **VERIFY (mandatory)** → 3. **Next Step**
2. All mathematical calculations must be immediately verified
3. Smart tolerance system:
   - **Large numbers** (>1e-6): Relative tolerance (0.01%)
   - **Small numbers** (≤1e-6): Absolute tolerance (1e-10)
4. Comprehensive math function support in verification (`exp`, `log`, `sqrt`, etc.)

### Error Handling
- Unicode encoding fixes for Windows compatibility
- Detailed error logging and recovery mechanisms
- Graceful degradation with informative error messages

## 📋 System Prompt Evaluation

Our system prompt has been evaluated against the "Prompt of Prompts" criteria:

```json
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Excellent structure with comprehensive verification, clear examples, and mandatory workflow enforcement. Strong separation of reasoning and tools with explicit self-checks."
}
```

### ✅ **Evaluation Details:**

1. **✅ Explicit Reasoning Instructions**: "think step by step and think before you select a tool"
2. **✅ Structured Output Format**: Enforced `FUNCTION_CALL: function_name|param1|param2` and `FINAL_ANSWER: [result]`
3. **✅ Separation of Reasoning and Tools**: Clear workflow: calculate → verify → proceed
4. **✅ Conversation Loop Support**: Multi-turn context with iteration history and memory integration
5. **✅ Instructional Framing**: Comprehensive examples with mandatory verification patterns
6. **✅ Internal Self-Checks**: Mandatory verification after every mathematical operation
7. **✅ Reasoning Type Awareness**: "identify the type of reasoning used like arithmetic, logic, lookup tool, system tool"
8. **✅ Error Handling or Fallbacks**: "If a certain tool fails, let the user know the reason and follow the specified fall back tool"
9. **✅ Overall Clarity and Robustness**: Structured sections, clear examples, and explicit enforcement rules

## 🚀 Key Achievements

### 1. **Modular Architecture**
- Clean separation of concerns across 4 layers
- Asynchronous processing with proper error handling
- Extensible design for adding new tools and capabilities

### 2. **Intelligent Verification**
- Automatic verification of all mathematical operations
- Smart tolerance system handling both large and small numbers
- Comprehensive math function support in evaluation

### 3. **User Personalization**
- Preference extraction and storage (colors, communication style)
- Context-aware responses based on user characteristics
- Memory-driven personalization across sessions

### 4. **Robust System Integration**
- Paint application automation with image-based UI control
- Gmail API integration with OAuth2 authentication
- Cross-platform compatibility with Windows-specific optimizations

### 5. **Enhanced Prompt Engineering**
- Systematic evaluation against established criteria
- Mandatory workflow enforcement for reliability
- Clear examples and structured output requirements

## 🔄 Workflow Example

```
User Input: "I prefer red color and funny answers. Calculate ASCII values of INDIA, find exponential sum, draw in Paint, and email the result."

1. PERCEPTION: Extracts preferences (color:red, style:funny) and task breakdown
2. MEMORY: Stores user preferences for future use
3. DECISION: Plans step-by-step workflow with verification
4. ACTION: Executes tools in sequence:
   - strings_to_chars_to_int|INDIA → [73,78,68,73,65]
   - verify|ord('I')+ord('N')+ord('D')+ord('I')+ord('A')|[73,78,68,73,65] → True
   - int_list_to_exponential_sum|[73,78,68,73,65] → 7.59982224609308e33
   - verify|exp(73)+exp(78)+exp(68)+exp(73)+exp(65)|7.59982224609308e33 → True
   - open_paint → Success
   - draw_rectangle_and_text|7.59982224609308e33|red → Success
   - send_email|user@email.com|Story|Name|Funny story about the result → Success
```

## 🛠️ Technical Stack

- **Language**: Python 3.8+
- **LLM**: Google Gemini 2.0 Flash
- **Framework**: MCP (Model Context Protocol) with FastMCP
- **UI Automation**: pyautogui, pywinauto, pydirectinput
- **Email**: Gmail API with OAuth2
- **Data Models**: Pydantic for type safety and validation
- **Async**: asyncio for concurrent operations

## 📁 Project Structure

```
first_padm/
├── main.py           # Orchestrator and entry point
├── perception.py     # Fact extraction from user input
├── memory.py         # Fact storage and retrieval
├── decision.py       # Tool selection and workflow planning
├── action.py         # Tool implementations (MCP server)
├── model.py          # Pydantic data models
├── pyproject.toml    # Dependencies and project config
└── *.jpg            # UI automation image assets
```

## 🎯 Future Enhancements

- **Fallback Tools**: Multi-level fallback strategies for system tools
- **Enhanced Memory**: Persistent storage with vector embeddings
- **Tool Expansion**: Additional system automation and API integrations
- **Performance Optimization**: Caching and parallel tool execution
- **Advanced Verification**: Domain-specific validation rules

---

*This multimodal agent demonstrates advanced AI orchestration with robust verification, user personalization, and comprehensive system integration capabilities.*
