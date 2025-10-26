from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from mcp.server.fastmcp import Image
from mcp.types import TextContent

# Mathematical operations models
class AddInput(BaseModel):
    a: int
    b: int

class AddOutput(BaseModel):
    result: int

class AddListInput(BaseModel):
    l: List[int]

class AddListOutput(BaseModel):
    result: int

class SubtractInput(BaseModel):
    a: int
    b: int

class SubtractOutput(BaseModel):
    result: int

class MultiplyInput(BaseModel):
    a: int
    b: int

class MultiplyOutput(BaseModel):
    result: int

class DivideInput(BaseModel):
    a: int
    b: int

class DivideOutput(BaseModel):
    result: float

class PowerInput(BaseModel):
    a: int
    b: int

class PowerOutput(BaseModel):
    result: int

class SqrtInput(BaseModel):
    a: int

class SqrtOutput(BaseModel):
    result: float

class CbrtInput(BaseModel):
    a: int

class CbrtOutput(BaseModel):
    result: float

class FactorialInput(BaseModel):
    a: int

class FactorialOutput(BaseModel):
    result: int

class LogInput(BaseModel):
    a: int

class LogOutput(BaseModel):
    result: float

class RemainderInput(BaseModel):
    a: int
    b: int

class RemainderOutput(BaseModel):
    result: int

class SinInput(BaseModel):
    a: int

class SinOutput(BaseModel):
    result: float

class CosInput(BaseModel):
    a: int

class CosOutput(BaseModel):
    result: float

class TanInput(BaseModel):
    a: int

class TanOutput(BaseModel):
    result: float

class MineInput(BaseModel):
    a: int
    b: int

class MineOutput(BaseModel):
    result: int

# String and list operations models
class StringsToCharsToIntInput(BaseModel):
    string: str

class StringsToCharsToIntOutput(BaseModel):
    result: List[int]

class IntListToExponentialSumInput(BaseModel):
    int_list: List[int]

class IntListToExponentialSumOutput(BaseModel):
    result: float

class FibonacciNumbersInput(BaseModel):
    n: int

class FibonacciNumbersOutput(BaseModel):
    result: List[int]

# System operations models
class DrawRectangleAndTextInput(BaseModel):
    text: str
    color: str = "black"

class DrawRectangleAndTextOutput(BaseModel):
    content: List[TextContent]

class OpenPaintInput(BaseModel):
    pass  # No input parameters

class OpenPaintOutput(BaseModel):
    content: List[TextContent]

class SendEmailInput(BaseModel):
    receiver_email: str
    subject: str
    receiver_name: str
    body: str

class SendEmailOutput(BaseModel):
    content: List[TextContent]

# New models for modular architecture

# Perception models
class PerceptionInput(BaseModel):
    user_input: str
    context: Optional[str] = None

class ExtractedFacts(BaseModel):
    task: str
    entities: List[str] = []
    characteristics: Dict[str, str] = {}
    preferences: Dict[str, str] = {}
    requirements: List[str] = []

class PerceptionOutput(BaseModel):
    facts: ExtractedFacts
    processed_query: str
    confidence: float = 1.0

# Memory models
class Fact(BaseModel):
    content: str
    category: str
    timestamp: Optional[str] = None
    relevance_score: float = 1.0

class MemoryInput(BaseModel):
    fact: Optional[Fact] = None
    query: Optional[str] = None

class MemoryOutput(BaseModel):
    relevant_facts: List[Fact] = []
    summary: Optional[str] = None

# Decision models
class DecisionInput(BaseModel):
    facts: ExtractedFacts
    memory_context: List[Fact]
    available_tools: List[str]
    iteration_history: List[str] = []
    query: str

class ToolCall(BaseModel):
    function_name: str
    parameters: List[str]

class DecisionOutput(BaseModel):
    action_type: str  # "FUNCTION_CALL" or "FINAL_ANSWER"
    tool_call: Optional[ToolCall] = None
    final_answer: Optional[str] = None
    reasoning: Optional[str] = None

# Main orchestrator models
class AgentState(BaseModel):
    iteration: int = 0
    max_iterations: int = 10
    iteration_responses: List[str] = []
    last_response: Optional[Any] = None
    is_complete: bool = False

# Verification tool models
class VerifyInput(BaseModel):
    expression: str
    expected: float

class VerifyOutput(BaseModel):
    result: str  # Will contain "True", "False", or error message
