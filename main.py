import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from perception import PerceptionModule
from memory import MemoryModule
from decision import DecisionModule
from model import (
    PerceptionInput, MemoryInput, DecisionInput, AgentState,
    Fact, ExtractedFacts
)

class AgentOrchestrator:
    def __init__(self):
        self.perception = PerceptionModule()
        self.memory = MemoryModule()
        self.decision = DecisionModule()
        self.state = AgentState()
        
    async def get_tools_description(self, tools):
        """Convert tools to description format"""
        tools_description = []
        for i, tool in enumerate(tools):
            try:
                params = tool.inputSchema
                desc = getattr(tool, 'description', 'No description available')
                name = getattr(tool, 'name', f'tool_{i}')
                
                if 'properties' in params:
                    param_details = []
                    for param_name, param_info in params['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        param_details.append(f"{param_name}: {param_type}")
                    params_str = ', '.join(param_details)
                else:
                    params_str = 'no parameters'

                tool_desc = f"{name}({params_str}) - {desc}"
                tools_description.append(tool_desc)
            except Exception as e:
                print(f"Error processing tool {i}: {e}")
                tools_description.append(f"Error processing tool")
        
        return tools_description
    
    async def execute_tool(self, session, tools, tool_call):
        """Execute a tool call"""
        func_name = tool_call.function_name
        params = tool_call.parameters
        
        print(f"  Executing tool: {func_name} with params: {params}")
        
        # Find the matching tool
        tool = next((t for t in tools if t.name == func_name), None)
        if not tool:
            raise ValueError(f"Unknown tool: {func_name}")
        
        # Get the tool's input schema
        schema = tool.inputSchema
        print(f"  Full tool schema: {schema}")
        
        # For tools that use Pydantic models, we need to construct the arguments differently
        if 'properties' in schema and 'input' in schema['properties']:
            # This is a Pydantic model-based tool
            input_schema_ref = schema['properties']['input']
            print(f"  Input schema: {input_schema_ref}")
            
            # Handle $ref to get the actual schema definition
            if '$ref' in input_schema_ref:
                ref_path = input_schema_ref['$ref']
                if ref_path.startswith('#/$defs/'):
                    def_name = ref_path.replace('#/$defs/', '')
                    if '$defs' in schema and def_name in schema['$defs']:
                        actual_input_schema = schema['$defs'][def_name]
                        print(f"  Resolved schema for {def_name}: {actual_input_schema}")
                        
                        if 'properties' in actual_input_schema:
                            # Construct the nested argument structure
                            input_properties = actual_input_schema['properties']
                            input_args = {}
                            
                            param_index = 0
                            for prop_name, prop_info in input_properties.items():
                                prop_type = prop_info.get('type', 'string')
                                print(f"  Processing property {prop_name} (type: {prop_type})")
                                
                                if prop_type == 'array':
                                    # For array types, collect ALL remaining parameters
                                    if param_index < len(params):
                                        # Check if it's a single parameter that looks like an array
                                        first_param = params[param_index]
                                        if (len(params) == param_index + 1 and 
                                            (',' in first_param or first_param.startswith('['))):
                                            # Single parameter with comma-separated values or JSON-like array
                                            if first_param.startswith('[') and first_param.endswith(']'):
                                                value = first_param.strip('[]').split(',')
                                            else:
                                                value = first_param.split(',')
                                            input_args[prop_name] = [int(x.strip()) for x in value if x.strip()]
                                            param_index += 1
                                        else:
                                            # Multiple parameters - collect all remaining as array elements
                                            array_values = params[param_index:]
                                            input_args[prop_name] = [int(x) for x in array_values]
                                            param_index = len(params)  # Mark all params as consumed
                                    else:
                                        input_args[prop_name] = []
                                    
                                    print(f"  Set array {prop_name}={input_args[prop_name]}")
                                else:
                                    # For non-array types, take one parameter
                                    if param_index < len(params):
                                        value = params[param_index]
                                        
                                        # Convert the value to the correct type
                                        if prop_type == 'integer':
                                            input_args[prop_name] = int(value)
                                        elif prop_type == 'number':
                                            input_args[prop_name] = float(value)
                                        else:
                                            input_args[prop_name] = str(value)
                                        
                                        param_index += 1
                                        print(f"  Set {prop_name}={input_args[prop_name]} (type: {prop_type})")
                            
                            arguments = {'input': input_args}
                            print(f"  Constructed nested arguments: {arguments}")
                        else:
                            # Fallback: simple input
                            arguments = {'input': params[0] if params else ""}
                    else:
                        # Fallback: simple input
                        arguments = {'input': params[0] if params else ""}
                else:
                    # Fallback: simple input
                    arguments = {'input': params[0] if params else ""}
            elif 'properties' in input_schema_ref:
                # Direct properties in input schema
                input_properties = input_schema_ref['properties']
                input_args = {}
                
                param_index = 0
                for prop_name, prop_info in input_properties.items():
                    if param_index < len(params):
                        value = params[param_index]
                        prop_type = prop_info.get('type', 'string')
                        
                        print(f"  Setting {prop_name}={value} (type: {prop_type})")
                        
                        # Convert the value to the correct type
                        if prop_type == 'integer':
                            input_args[prop_name] = int(value)
                        elif prop_type == 'number':
                            input_args[prop_name] = float(value)
                        elif prop_type == 'array':
                            if isinstance(value, str):
                                if value.startswith('[') and value.endswith(']'):
                                    value = value.strip('[]').split(',')
                                else:
                                    value = value.split(',')
                                input_args[prop_name] = [int(x.strip()) for x in value if x.strip()]
                            else:
                                input_args[prop_name] = value
                        else:
                            input_args[prop_name] = str(value)
                        
                        param_index += 1
                
                arguments = {'input': input_args}
            else:
                # Simple input schema
                arguments = {'input': params[0] if params else ""}
        else:
            # Legacy argument handling for non-Pydantic tools (shouldn't happen with your current setup)
            arguments = {}
            schema_properties = schema.get('properties', {})
            
            for param_name, param_info in schema_properties.items():
                if not params:
                    raise ValueError(f"Not enough parameters provided for {func_name}")
                    
                value = params.pop(0)
                param_type = param_info.get('type', 'string')
                
                # Convert the value to the correct type
                if param_type == 'integer':
                    arguments[param_name] = int(value)
                elif param_type == 'number':
                    arguments[param_name] = float(value)
                elif param_type == 'array':
                    if isinstance(value, str):
                        value = value.strip('[]').split(',')
                    arguments[param_name] = [int(x.strip()) for x in value]
                else:
                    arguments[param_name] = str(value)
        
        print(f"  Final arguments: {arguments}")
        
        # Execute the tool
        print(f"  Calling session.call_tool({func_name}, arguments={arguments})")
        result = await session.call_tool(func_name, arguments=arguments)
        print(f"  Raw tool result: {result}")
        
        # Check if the result indicates an error
        if hasattr(result, 'isError') and result.isError:
            print(f"  ERROR: Tool execution failed!")
            if hasattr(result, 'content') and result.content:
                error_msg = result.content[0].text if isinstance(result.content, list) else str(result.content)
                print(f"  Error details: {error_msg}")
                raise Exception(f"Tool {func_name} failed: {error_msg}")
        
        # Process result
        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                iteration_result = [
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                ]
            else:
                iteration_result = str(result.content)
        else:
            iteration_result = str(result)
        
        print(f"  Processed result: {iteration_result}")
        return iteration_result
    
    async def run(self, user_query: str):
        """Main orchestration method"""
        print("Starting Agent Orchestrator...")
        
        try:
            # Step 1: Perception - understand the query
            print("Step 1: Processing query through perception...")
            perception_input = PerceptionInput(user_input=user_query)
            perception_output = await self.perception.extract_facts(perception_input)
            print(f"Extracted facts: {perception_output.facts}")
            
            # Step 2: Store facts in memory if needed
            print("Step 2: Storing relevant facts in memory...")
            
            # Store entities
            for entity in perception_output.facts.entities:
                fact = Fact(content=f"Entity mentioned: {entity}", category="entity")
                await self.memory.recall_facts(MemoryInput(fact=fact))
            
            # Store characteristics
            for char_key, char_value in perception_output.facts.characteristics.items():
                fact = Fact(content=f"User characteristic: {char_key} = {char_value}", category="characteristic")
                await self.memory.recall_facts(MemoryInput(fact=fact))
            
            # Store preferences
            for pref_key, pref_value in perception_output.facts.preferences.items():
                fact = Fact(content=f"User preference: {pref_key} = {pref_value}", category="preference")
                await self.memory.recall_facts(MemoryInput(fact=fact))
            
            # Step 3: Connect to MCP server
            print("Step 3: Connecting to MCP server...")
            server_params = StdioServerParameters(
                command="python",
                args=["action.py"]  # Use action.py instead of example2.py
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Get available tools
                    tools_result = await session.list_tools()
                    tools = tools_result.tools
                    tools_description = await self.get_tools_description(tools)
                    
                    print(f"Available tools: {len(tools)}")
                    
                    # Step 4: Main decision loop
                    print("Step 4: Starting decision loop...")
                    current_query = perception_output.processed_query
                    
                    while self.state.iteration < self.state.max_iterations and not self.state.is_complete:
                        print(f"\n--- Iteration {self.state.iteration + 1} ---")
                        
                        # Get memory context
                        memory_output = await self.memory.recall_facts(
                            MemoryInput(query=current_query)
                        )
                        
                        # Make decision
                        decision_input = DecisionInput(
                            facts=perception_output.facts,
                            memory_context=memory_output.relevant_facts,
                            available_tools=tools_description,
                            iteration_history=self.state.iteration_responses,
                            query=current_query
                        )
                        
                        decision_output = await self.decision.decide(decision_input)

                        # Enhanced logging with more details
                        if decision_output.action_type == "FUNCTION_CALL" and decision_output.tool_call:
                            print(f"Decision: {decision_output.action_type}")
                            print(f"  Tool: {decision_output.tool_call.function_name}")
                            print(f"  Parameters: {decision_output.tool_call.parameters}")
                            if decision_output.reasoning:
                                print(f"  Reasoning: {decision_output.reasoning}")
                        else:
                            print(f"Decision: {decision_output.action_type}")
                            if decision_output.final_answer:
                                print(f"  Answer: {decision_output.final_answer}")

                        if decision_output.action_type == "FUNCTION_CALL" and decision_output.tool_call:
                            try:
                                print(f"  Starting tool execution...")
                                # Execute tool
                                result = await self.execute_tool(session, tools, decision_output.tool_call)
                                
                                print(f"  Tool execution completed successfully")
                                print(f"  Result: {result}")
                                
                                # Check if result indicates failure (even if no exception was thrown)
                                if isinstance(result, list) and len(result) > 0:
                                    result_text = result[0] if isinstance(result[0], str) else str(result[0])
                                    if "Error" in result_text or "error" in result_text.lower():
                                        print(f"  WARNING: Tool result contains error message")
                                        # Still continue but log the issue
                                
                                # Update state
                                result_str = str(result) if not isinstance(result, list) else f"[{', '.join(map(str, result))}]"
                                
                                iteration_response = (
                                    f"In iteration {self.state.iteration + 1}, called {decision_output.tool_call.function_name} "
                                    f"with parameters {decision_output.tool_call.parameters}, "
                                    f"and the function returned {result_str}."
                                )
                                
                                self.state.iteration_responses.append(iteration_response)
                                self.state.last_response = result
                                
                                print(f"  Updated iteration responses: {len(self.state.iteration_responses)} total")
                                
                                # Update current query for next iteration
                                current_query = current_query + "\n\n" + " ".join(self.state.iteration_responses) + " What should I do next?"
                                
                            except Exception as e:
                                print(f"  ERROR executing tool: {e}")
                                print(f"  Error type: {type(e)}")
                                import traceback
                                traceback.print_exc()
                                
                                # Add more detailed error info to help the agent recover
                                error_response = f"Error in iteration {self.state.iteration + 1}: Failed to execute {decision_output.tool_call.function_name} with parameters {decision_output.tool_call.parameters}. Error: {str(e)}"
                                self.state.iteration_responses.append(error_response)
                                
                                # Don't break immediately - let the agent try to recover
                                current_query = current_query + "\n\n" + " ".join(self.state.iteration_responses) + " The previous tool call failed. What should I do next?"
                                
                        elif decision_output.action_type == "FINAL_ANSWER":
                            print(f"\n=== Agent Execution Complete ===")
                            print(f"Final Answer: {decision_output.final_answer}")
                            self.state.is_complete = True
                            break
                        
                        self.state.iteration += 1
                    
                    if not self.state.is_complete:
                        print("Maximum iterations reached without completion")
                        
        except Exception as e:
            print(f"Error in main execution: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Entry point"""
    orchestrator = AgentOrchestrator()
    
    query = """I prefer comedy and funny answers. Find the ASCII values of characters in INDIA and then find sum of exponentials of those values and save it as exponential sum, then Open Paint and draw a rectangle  and add text in Paint with the exponential sum. Then send an email to amlan.routray@gmail.com with story about the exponential sum'"""
    
    await orchestrator.run(query)

if __name__ == "__main__":
    asyncio.run(main())
