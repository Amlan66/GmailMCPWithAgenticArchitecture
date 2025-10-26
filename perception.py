import os
from dotenv import load_dotenv
from google import genai
import asyncio
from model import PerceptionInput, PerceptionOutput, ExtractedFacts

load_dotenv()

class PerceptionModule:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
    
    async def call_llm(self, prompt: str, timeout: int = 10) -> str:
        """Call LLM with timeout - using the working implementation from talk2mcp-4.py"""
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
    
    async def extract_facts(self, input_data: PerceptionInput) -> PerceptionOutput:
        """Extract important facts from user input"""
        prompt = f"""
        Extract important facts from the user input and structure them as follows:
        
        User Input: {input_data.user_input}
        Context: {input_data.context or "None"}
        
        Please identify:
        1. Main task/goal - what the user wants to accomplish
        2. Entities mentioned - people, places, things, email addresses, etc.
        3. User characteristics - personality traits, communication style (e.g., funny, sarcastic, formal)
        4. User preferences - color preferences, style preferences, etc.
        5. Specific requirements or constraints
        
        Look specifically for:
        - Color preferences (red, blue, green, etc.)
        - Communication style (funny, comedy, sarcastic, formal, etc.)
        - Personal traits or characteristics
        
        Format your response EXACTLY as:
        TASK: [main task description]
        ENTITIES: [comma-separated list of entities]
        CHARACTERISTICS: [style:funny, tone:comedy] (use key:value format)
        PREFERENCES: [color:red, format:informal] (use key:value format)
        REQUIREMENTS: [requirement1, requirement2] (comma-separated)
        PROCESSED_QUERY: [cleaned and structured version of the query]
        
        Example:
        If user says "I prefer red color and funny answers", extract:
        CHARACTERISTICS: style:funny, tone:comedy
        PREFERENCES: color:red, communication:humorous
        """
        
        try:
            response = await self.call_llm(prompt)
            
            # Parse the response (simplified parsing - you might want to make this more robust)
            lines = response.split('\n')
            task = ""
            entities = []
            characteristics = {}
            preferences = {}
            requirements = []
            processed_query = input_data.user_input
            
            for line in lines:
                line = line.strip()
                if line.startswith("TASK:"):
                    task = line.replace("TASK:", "").strip()
                elif line.startswith("ENTITIES:"):
                    entities = [e.strip() for e in line.replace("ENTITIES:", "").split(",") if e.strip()]
                elif line.startswith("CHARACTERISTICS:"):
                    chars_str = line.replace("CHARACTERISTICS:", "").strip()
                    if chars_str and chars_str != "None":
                        # Parse key:value pairs
                        for pair in chars_str.split(","):
                            if ":" in pair:
                                key, value = pair.split(":", 1)
                                characteristics[key.strip()] = value.strip()
                elif line.startswith("PREFERENCES:"):
                    prefs_str = line.replace("PREFERENCES:", "").strip()
                    if prefs_str and prefs_str != "None":
                        # Parse key:value pairs
                        for pair in prefs_str.split(","):
                            if ":" in pair:
                                key, value = pair.split(":", 1)
                                preferences[key.strip()] = value.strip()
                elif line.startswith("REQUIREMENTS:"):
                    reqs_str = line.replace("REQUIREMENTS:", "").strip()
                    if reqs_str and reqs_str != "None":
                        requirements = [r.strip() for r in reqs_str.split(",") if r.strip()]
                elif line.startswith("PROCESSED_QUERY:"):
                    processed_query = line.replace("PROCESSED_QUERY:", "").strip()
            
            facts = ExtractedFacts(
                task=task or "Unknown task",
                entities=entities,
                characteristics=characteristics,
                preferences=preferences,
                requirements=requirements
            )
            
            return PerceptionOutput(
                facts=facts,
                processed_query=processed_query,
                confidence=0.8
            )
            
        except Exception as e:
            print(f"Error in fact extraction: {e}")
            # Return default response
            return PerceptionOutput(
                facts=ExtractedFacts(task="Unknown task"),
                processed_query=input_data.user_input,
                confidence=0.1
            )
