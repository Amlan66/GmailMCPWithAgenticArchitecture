import os
from dotenv import load_dotenv
from google import genai
import asyncio
from typing import List
from model import Fact, MemoryInput, MemoryOutput

load_dotenv()

class MemoryModule:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.facts: List[Fact] = []
    
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
    
    def store_fact(self, fact: Fact):
        """Store a new fact in memory"""
        self.facts.append(fact)
        print(f"Stored fact: {fact.content}")
    
    async def recall_facts(self, input_data: MemoryInput) -> MemoryOutput:
        """Recall relevant facts based on query"""
        if input_data.fact:
            self.store_fact(input_data.fact)
            return MemoryOutput(relevant_facts=[], summary="Fact stored successfully")
        
        if not input_data.query:
            return MemoryOutput(relevant_facts=self.facts, summary="All stored facts")
        
        # Use LLM to find relevant facts
        facts_text = "\n".join([f"- {fact.content} (Category: {fact.category})" for fact in self.facts])
        
        prompt = f"""
        Given the following stored facts:
        {facts_text}
        
        Query: {input_data.query}
        
        Please identify which facts are most relevant to this query and provide a brief summary.
        
        Format your response as:
        RELEVANT_FACTS: [list the most relevant facts]
        SUMMARY: [brief summary of relevant information]
        """
        
        try:
            response = await self.call_llm(prompt)
            
            # Simple parsing - you might want to make this more sophisticated
            relevant_facts = []
            summary = "No relevant facts found"
            
            lines = response.split('\n')
            for line in lines:
                if line.startswith("SUMMARY:"):
                    summary = line.replace("SUMMARY:", "").strip()
            
            # For now, return all facts with the summary
            # In a more sophisticated implementation, you'd filter based on relevance
            return MemoryOutput(
                relevant_facts=self.facts,
                summary=summary
            )
            
        except Exception as e:
            print(f"Error in fact recall: {e}")
            return MemoryOutput(relevant_facts=[], summary="Error retrieving facts")
