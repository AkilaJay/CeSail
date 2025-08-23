import asyncio
import json
import sys
import os
from typing import Dict, Any, List

from cesail.dom_parser.src.dom_parser import DOMParser as BaseDOMParser
from cesail.dom_parser.src.py.types import Action as UIAction
try:
    from .llm_interface import get_llm_response
except ImportError:
    # Fallback for when running the file directly
    from llm_interface import get_llm_response
import logging

logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self):
        self.dom_parser = None
        self.context = {
            'execution_history': [],
            'current_state': None,
            'current_action': None
        }
        
    async def initialize(self, url: str = None):
        """Initialize the agent with a target URL"""
        if url is None:
            url = input("Enter the URL you want to navigate to (or press Enter for default): ").strip()
            if not url:
                url = "https://www.google.com/travel/flights"
        
        self.dom_parser = BaseDOMParser()
        await self.dom_parser.__aenter__()

        
        action = UIAction(
                type="navigate",
                description=f"Navigate to {url}",
                confidence=1.0,
                metadata={"url": url}
        )
        
        await self.dom_parser.execute_action(action, wait_for_idle=True, translate_element_id=True)
        print(f"Initialized agent and navigated to {url}")
        
    async def breakdown_handler(self, user_input: str) -> Dict[str, Any]:
        """Break down user input into actionable steps using real LLM"""
        prompt = f"""
You are an AI agent that helps users accomplish complex UI tasks on browser/website by breaking down actions into steps.

Rules:
- Break down the action into clear, executable steps
- Each step should be atomic and specific enough to be executed independently
- Include success criteria for verification
- Specify dependencies between steps
- Ensure steps are in logical order

Action to break down: {user_input}

Return a JSON object with the exact structure shown below.
"""
        
        output_format = {
            "main_action": {
                "name": "string",
                "text": "string"
            },
            "sub_actions": [
                {
                    "name": "string",
                    "text": "string", 
                    "success_criteria": "string"
                }
            ],
            "dependencies": [
                {
                    "from": "string",
                    "to": "string",
                    "type": "string"
                }
            ]
        }
        
        try:
            # result = get_llm_response(prompt, 'breakdown', output_format)

            # Get screenshot for breakdown analysis
            screenshot = await self.dom_parser.take_screenshot(
                            filepath="/tmp/screenshot3.png",
                            quality=None,
                            format="png",
                            full_page=False,
                            return_base64=True
                        )
            
            
            # self.dom_parser.get_screenshot() if hasattr(self.dom_parser, 'get_screenshot') else None
            
            result = get_llm_response(
                prompt=prompt,
                purpose='breakdown',
                output_format=output_format,
                screenshot=screenshot
            )
            return result
        except Exception as e:
            print(f"Error in LLM breakdown: {e}")
            # Fallback to simple breakdown
            return {
                "main_action": {
                    "name": user_input,
                    "text": f"Complete the task: {user_input}"
                },
                "sub_actions": [
                    {
                        "name": "Step 1",
                        "text": f"First step to accomplish: {user_input}",
                        "success_criteria": "Step 1 is complete when..."
                    },
                    {
                        "name": "Step 2", 
                        "text": f"Second step to accomplish: {user_input}",
                        "success_criteria": "Step 2 is complete when..."
                    }
                ],
                "dependencies": [
                    {
                        "from": "Step 1",
                        "to": "Step 2", 
                        "type": "sequential"
                    }
                ]
            }
        
    async def execute_action(self, ui_action: Dict[str, Any]) -> tuple:
        """Execute a UI action and return results"""
        try:
            # Create UIAction object
            action = UIAction.from_json(ui_action)
            
            # Execute the action
            result = await self.dom_parser.execute_action(action, wait_for_idle=True, translate_element_id=True)
            
            # # Simulate side effects (in real implementation, this would be actual side effects)
            # side_effects = []
            
            return result
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {"error": str(e)}, []
        
    async def analyze_observation(self, ui_action: Dict[str, Any], execution_result: Dict[str, Any], 
                                breakdown_action: str, breakdown_first_sub_action: str) -> Dict[str, Any]:
        
        input("Start analyze_observation...")

        """Analyze the results of an executed action"""
        observation_prompt = f"""
        Analyze the execution results and determine if we should proceed.

        Executed Action: {json.dumps(ui_action, indent=2)}
        Execution Result: {json.dumps(execution_result, indent=2)}

        Current Action: {breakdown_action}
        Current Sub-Action: {breakdown_first_sub_action}

        Screenshot: Screenshot after the action is executed is attached.

        Return a JSON response with:
        - success: true/false
        - observation: Analysis of the results
        - next_step: generate the sub-action to be executed next
        
        If the sub-action is complete, set sub_action_complete to true.
        """
        
        output_format = {
            'success': 'bool',
            'observation': 'str',
            'next_step': 'str',
        }
        
        try:
            # Get screenshot for observation analysis
            screenshot = await self.dom_parser.take_screenshot(
                            filepath="/tmp/screenshot3.png",
                            quality=None,
                            format="png",
                            full_page=False,
                            return_base64=True
                        )
            
            
            # self.dom_parser.get_screenshot() if hasattr(self.dom_parser, 'get_screenshot') else None
            
            result = get_llm_response(
                prompt=observation_prompt,
                purpose='observation',
                output_format=output_format,
                screenshot=screenshot
            )

            print("RESULT ", json.dumps(observation_prompt, indent=2));
            input("Press Enter to continue...")
            return result
        except Exception as e:
            logger.error(f"Error in observation analysis: {e}")
            # Fallback response
            return {
                'success': True,
                'observation': f"Action executed: {ui_action.get('type', 'unknown')}",
                'next_step': 'continue',
                'sub_action_complete': True
            }
        
    async def planner_react_loop(self, breakdown_action: str, breakdown_first_sub_action: str, breakdown_success_criteria: str) -> Dict[str, Any]:
        """React loop that implements think-plan-execute pattern using real LLM"""
        max_iterations = 10
        iteration = 0
        current_state = None
        previous_state = None
        last_observation = None

        print(f"Starting react loop for action: {breakdown_action}")
        input("Press Enter to continue...")
        
        # Create a simple action structure
        class SimpleAction:
            def __init__(self, name, text, sub_actions):
                self.name = name
                self.text = text
                self.sub_actions = sub_actions
                self.status = "NOT_STARTED"
                
        class SimpleSubAction:
            def __init__(self, name, text, success_criteria):
                self.name = name
                self.text = text
                self.success_criteria = success_criteria
                self.status = "NOT_STARTED"
                
        # # Create main action
        # main_action = SimpleAction(
        #     breakdown['main_action']['name'],
        #     breakdown['main_action']['text'],
        #     []
        # )
        
        # # Create sub-actions
        # for sub_action_data in breakdown['sub_actions']:
        #     sub_action = SimpleSubAction(
        #         sub_action_data['name'],
        #         sub_action_data['text'], 
        #         sub_action_data['success_criteria']
        #     )
        #     main_action.sub_actions.append(sub_action)
            
        # self.context['current_action'] = main_action
        
        while iteration < max_iterations:
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get current state
            parsed_dom = await self.dom_parser.analyze_page()
            site_actions = parsed_dom.actions if hasattr(parsed_dom, 'actions') else []
            
            # Find current sub-action
            # current_sub_action = None
            # for sub_action in main_action.sub_actions:
            #     if sub_action.status == "NOT_STARTED":
            #         current_sub_action = sub_action
            #         sub_action.status = "IN_PROGRESS"
            #         break
                    
            # if not current_sub_action:
            #     return {
            #         'status': 'success',
            #         'message': 'All sub-actions are complete'
            #     }
                
            # print(f"Current sub-action: {current_sub_action.name}")
            # print(f"Description: {current_sub_action.text}")
            
            # Use real LLM for react loop logic
            react_prompt = f"""
You are an agent on a webpage. Based on the current action and sub-action, generate a UI action to execute.

Last Observation: {last_observation}

Current Action: {breakdown_action}
Current Sub-Action: {breakdown_first_sub_action}
Success Criteria: {breakdown_success_criteria}

Extracted Actions:
{site_actions.to_json()}

Screenshot: Screenshot is attached. It draws bounding boxes around the actionable elements.
            The center of the bounding box has a number. The number is the element id and corresponds to the selector.

Available Actions:
{json.dumps(self.dom_parser.get_available_actions(), indent=2)}

Recent History:
{json.dumps(self.context.get('execution_history', [])[-5:], indent=2)}

Based on this information:
1. Analyze what has been done so far
2. Determine what needs to be done next
3. Consider any dependencies or prerequisites
4. Identify potential challenges or risks
5. Generate a UI action to accomplish the next step

Return a JSON response with:
- decision: "think_more", "proceed", "need_info", "cancel", "task_complete"
- reasoning: Your analysis of the situation
- if decision is "proceed", include:
  - ui_action: {{
      "type": "action type from site",
      "description": "why this action is needed",
      "confidence": 0.0,
      "element_id": "element identifier taken from the selector",
      "text_to_type": "text to input/select",
      "value": "value to set"
    }}
  - prerequisites: Any requirements that must be met
  - potential_challenges: Possible issues to watch for

Rules for UI Action:
1. Only fill in the fields that are relevant to the action using the available actions
   required_params and optional_params are available in the available actions
2. The type must be from the Site provided above
3. The selector must be a valid CSS selector from the Site. The selector is the element id.
4. The text must be valid for the element
5. The success criteria must be verifiable

Decision Guide:
- Task complete: Return if the current action (not sub-action) is complete
- Proceed: Return with a UI action to execute
- Cancel: Return if the task is not possible
"""
            
            output_format = {
                "decision": "string",  # "think_more", "proceed", "need_info", "cancel", "task_complete"
                "reasoning": "string",
                "ui_action": {
                    "type": "string",
                    "description": "string", 
                    "confidence": "number",
                    "element_id": "string",
                    "text_to_type": "string",
                    "value": "any"
                },
                "prerequisites": "list?",
                "potential_challenges": "list?"
            }
            
            try:
                # Get screenshot for react analysis
                screenshot = await self.dom_parser.take_screenshot(
                            filepath="/tmp/screenshot4.png",
                            quality=None,
                            format="png",
                            full_page=False,
                            return_base64=True
                        )

                react_response = get_llm_response(
                    prompt=react_prompt,
                    purpose='react',
                    output_format=output_format,
                    screenshot=screenshot
                )
            

                print("PROMPT ", json.dumps(react_prompt, indent=2));
                print("--------------------------------8888");
                print("REACT RESPONSE ", react_response);
                print("--------------------------------8888");

                input("Press Enter to continue...")
            except Exception as e:
                print(f"Error in LLM react loop: {e}")
                # Fallback to simple response
                react_response = {
                    'decision': 'proceed',
                    'reasoning': f'Executing step: {breakdown_first_sub_action}',
                    'ui_action': {
                        'type': 'click',
                        'description': f'Click to proceed with {breakdown_first_sub_action}',
                        'confidence': 0.8,
                        'element_id': '1',
                        'text_to_type': '',
                        'value': None
                    }
                }
            
            print(f"Decision: {react_response['decision']}")
            print(f"Reasoning: {react_response['reasoning']}")
            
            # Handle different decisions
            if react_response['decision'] == 'cancel':
                return {
                    'status': 'cancel',
                    'message': react_response['reasoning']
                }
            elif react_response['decision'] == 'task_complete':
                return {
                    'status': 'success',
                    'message': 'Task completed successfully'
                }
            elif react_response['decision'] == 'proceed':
                # Execute the UI action
                ui_action = react_response['ui_action']
                print(f"Executing UI action: {ui_action['type']} on element {ui_action['element_id']}")
                
                try:
                    # Execute the action
                    execution_result = await self.execute_action(ui_action)

                    print("--------------------------------9999");
                    print("EXECUTION RESULT ", execution_result);
                    print("--------------------------------9999");
                    input("Press Enter to continue...")
                    print(f"Execution result: {execution_result}")
                    # print(f"Side effects: {side_effects}")
                    
                    # # Update state
                    # previous_state = current_state
                    current_state = await self.dom_parser.analyze_page()
                    
                    # Analyze the results
                    observation_response = await self.analyze_observation(
                        ui_action, execution_result, breakdown_action, breakdown_first_sub_action
                    )
                    
                    print(f"Observation: {observation_response['observation']}")
                    last_observation = observation_response

                    breakdown_first_sub_action = observation_response['next_step']
                    
                    # if observation_response['sub_action_complete']:
                    #     current_sub_action.status = "COMPLETE"
                    #     print(f"Completed sub-action: {current_sub_action.name}")
                    
                    # if observation_response['next_step'] == 'need_info':
                    #     return {
                    #         'status': 'need_info',
                    #         'message': observation_response['observation'],
                    #         'reason': observation_response.get('reason', ''),
                    #         'suggested_fix': observation_response.get('suggested_fix', '')
                    #     }
                    # elif observation_response['next_step'] == 'retry':
                    #     iteration += 1
                    #     continue
                    # elif observation_response['next_step'] == 'continue':
                    #     # Find the next incomplete sub-action
                    #     next_sub_action = None
                    #     for sub_action in main_action.sub_actions:
                    #         if sub_action.status == "NOT_STARTED":
                    #             next_sub_action = sub_action
                    #             next_sub_action.status = "IN_PROGRESS"
                    #             print(f"Next sub-action: {next_sub_action.name}")
                    #             break
                        
                    #     # If there are no more sub-actions, mark the main action as complete
                    #     if not next_sub_action:
                    #         main_action.status = "COMPLETE"
                    #         return {
                    #             'status': 'success',
                    #             'message': 'All sub-actions completed successfully'
                    #         }
                        
                    #     # Update current sub-action for next iteration
                    #     current_sub_action = next_sub_action
                    
                    # Add to execution history
                    self.context['execution_history'].append({
                        'action': ui_action,
                        'result': execution_result,
                        'observation': observation_response,
                        'timestamp': asyncio.get_event_loop().time()
                    })
                    
                except Exception as e:
                    print(f"Error executing action: {str(e)}")
                    return {
                        'status': 'error',
                        'message': f"Failed to execute action: {str(e)}",
                        'action': ui_action
                    }
            
            iteration += 1
            
        return {
            'status': 'timeout',
            'message': f'React loop reached maximum iterations ({max_iterations})'
        }
        
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Main method to process user input through breakdown and planning"""
        print(f"\n=== Processing User Input: {user_input} ===")
        
        # Step 1: Breakdown
        print("\n1. Breaking down action...")
        breakdown = await self.breakdown_handler(user_input)
        print(f"Breakdown complete: {breakdown['main_action']['name']}")
        print(f"Sub-actions: {len(breakdown['sub_actions'])}")

        breakdown_action = breakdown['main_action']['text']
        breakdown_first_sub_action = breakdown['sub_actions'][0]['text']
        breakdown_success_criteria = breakdown['sub_actions'][0]['success_criteria']
        
        # Step 2: Planning and Execution
        print("\n2. Starting react loop...")
        result = await self.planner_react_loop(breakdown_action, breakdown_first_sub_action, breakdown_success_criteria)
        
        return {
            'user_input': user_input,
            'breakdown': breakdown,
            'result': result
        }
        
    async def cleanup(self):
        """Clean up resources"""
        if self.dom_parser:
            await self.dom_parser.__aexit__(None, None, None)

async def main():
    """Main function to run the simple agent"""
    agent = SimpleAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        
        # Interactive mode - ask user for input
        print("\n=== Simple Agent Ready ===")
        print("The agent is ready to help you with web tasks!")
        print("Type 'quit' or 'exit' to stop the agent.")
        print("=" * 50)
        
        while True:
            # Get user input
            user_input = input("\nWhat would you like me to do? (e.g., 'Find and click on the men's shoes section'): ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                print("Please enter a task to perform.")
                continue
            
            # Process user input
            result = await agent.process_user_input(user_input)
            
            print(f"\n=== Task Result ===")
            print(json.dumps(result, indent=2))
            
            # Ask if user wants to continue
            continue_input = input("\nWould you like to perform another task? (y/n): ").strip().lower()
            if continue_input not in ['y', 'yes']:
                print("Goodbye!")
                break
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 