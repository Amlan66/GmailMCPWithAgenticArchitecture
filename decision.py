import os
from dotenv import load_dotenv
from google import genai
import asyncio
from model import DecisionInput, DecisionOutput, ToolCall

load_dotenv()

class DecisionModule:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
    
    async def call_llm(self, prompt: str, timeout: int = 10) -> str:
        """Generate content with a timeout"""
        print("Starting LLM generation...")
        try:
            # Add delay to respect rate limits
            await asyncio.sleep(4)
            
            # Convert the synchronous generate_content call to run in a thread
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: self.client.models.generate_content( 
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                ),
                timeout=timeout
            )
            print("LLM generation completed")
            return response.text.strip()
        except Exception as e:
            print(f"Error in LLM call: {e}")
            raise
    
    async def decide(self, input_data: DecisionInput) -> DecisionOutput:
        """Decide what action to take next"""
        
        # Build context from facts and memory
        facts_context = f"""
        Task: {input_data.facts.task}
        Entities: {', '.join(input_data.facts.entities)}
        Characteristics: {input_data.facts.characteristics}
        Preferences: {input_data.facts.preferences}
        Requirements: {', '.join(input_data.facts.requirements)}
        """
        
        memory_context = "\n".join([f"- {fact.content}" for fact in input_data.memory_context])
        
        iteration_context = "\n".join(input_data.iteration_history) if input_data.iteration_history else "No previous iterations"
        
        tools_list = "\n".join([f"- {tool}" for tool in input_data.available_tools])
        
        system_prompt = f"""You are a math agent solving problems in 
        iterations. You have access to various mathematical tools. 
        Additionally you have ability to draw on the canvas using the 
        system tools and gmail tool as well. For user query, think 
        step by step and think before you select a tool. You should 
        verify your answers at every step using verify tool as well. 
        Also you should identify the type of reasoning used like 
        arithmetic, logic, lookup tool, system tool. If a certain 
        tool fails, let the user know the reason and follow the 
        specified fall back tool mentioned in the initial tool used.

CRITICAL VERIFICATION REQUIREMENT - MANDATORY ENFORCEMENT:
- After EVERY mathematical calculation, the VERY NEXT action MUST be verification
- Mathematical operations include: add, subtract, multiply, divide, power, sqrt, cbrt, factorial, log, sin, cos, tan, strings_to_chars_to_int, int_list_to_exponential_sum
- NEVER proceed to the next calculation without verifying the previous one
- If you just called a math function, your NEXT call MUST be verify
- The verify tool takes: FUNCTION_CALL: verify|expression|expected_result

STRICT WORKFLOW ENFORCEMENT:
1. Math operation → 2. VERIFY (mandatory) → 3. Next step
Example: strings_to_chars_to_int → verify → int_list_to_exponential_sum → verify → open_paint

Available tools:
{tools_list}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [number or string]

MANDATORY VERIFICATION WORKFLOW:
1. Perform mathematical calculation
2. IMMEDIATELY verify the result using: FUNCTION_CALL: verify|expression|expected_result
3. Only proceed to next step after verification passes
4. If verification fails, recalculate before proceeding

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations AND verifications
- Do not repeat function calls with the same parameters
- ALWAYS consider user preferences and characteristics when making decisions
- For draw_rectangle_and_text: use format FUNCTION_CALL: draw_rectangle_and_text|text_content|color
- If user prefers red color, use red; if no color preference mentioned, use black
- Use user's preferred communication style (funny, formal, etc.) in email content

Examples with MANDATORY verification:
- FUNCTION_CALL: add|5|3  (returns 8)
- FUNCTION_CALL: verify|5 + 3|8  (MUST verify immediately)
- FUNCTION_CALL: strings_to_chars_to_int|INDIA  (returns [73,78,68,73,65])
- FUNCTION_CALL: int_list_to_exponential_sum|[73,78,68,73,65]  (returns large number)
- FUNCTION_CALL: verify|exp(73) + exp(78) + exp(68) + exp(73) + exp(65)|7.59982224609308e33  (MUST verify)
- FUNCTION_CALL: draw_rectangle_and_text|Hello World|red
- FUNCTION_CALL: send_email|amlan@gmail.com|Hello|Amlan|Hello, how are you?
- FINAL_ANSWER: [42]
- FINAL_ANSWER: [Email sent successfully to amlan@gmail.com with subject 'Hello' (Message ID: 1234567890)]
- FINAL_ANSWER: [Verification successful]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""
        
        prompt = f"""{system_prompt}

Current Context:
{facts_context}

User Preferences/Memory:
{memory_context}

Previous Iterations:
{iteration_context}

Current Query: {input_data.query}

What should I do next?"""
        
        try:
            response = await self.call_llm(prompt)
            
            # Find the FUNCTION_CALL or FINAL_ANSWER line in the response
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("FUNCTION_CALL:"):
                    _, function_info = line.split(":", 1)
                    parts = [p.strip() for p in function_info.split("|")]
                    func_name, params = parts[0], parts[1:]
                    
                    return DecisionOutput(
                        action_type="FUNCTION_CALL",
                        tool_call=ToolCall(function_name=func_name, parameters=params),
                        reasoning=f"Decided to call {func_name} with parameters {params}"
                    )
                elif line.startswith("FINAL_ANSWER:"):
                    answer = line.replace("FINAL_ANSWER:", "").strip()
                    return DecisionOutput(
                        action_type="FINAL_ANSWER",
                        final_answer=answer,
                        reasoning="Task completed"
                    )
            
            # If no valid response found, return error
            return DecisionOutput(
                action_type="FINAL_ANSWER",
                final_answer="Error: Could not determine next action",
                reasoning="Failed to parse LLM response"
            )
            
        except Exception as e:
            print(f"Error in decision making: {e}")
            return DecisionOutput(
                action_type="FINAL_ANSWER",
                final_answer=f"Error in decision making: {str(e)}",
                reasoning="Exception occurred"
            )
