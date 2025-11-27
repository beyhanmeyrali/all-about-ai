from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import os
from openai import AzureOpenAI, ChatCompletion
from langchain_core.output_parsers import StrOutputParser
import uvicorn
import json
import requests
from requests.auth import HTTPBasicAuth

import sys
import os

# Add 'chameleon/ai_base' to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_base'))
sys.path.append(base_dir)

from params import Params


class AzureOpenAIBot:
    def __init__(self, model, endpoint, api_version, api_key):
        self.api_key = api_key
        self.model = model
        os.environ['AZURE_OPENAI_API_KEY'] = self.api_key

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather. Returns weather of city given in JSON format.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location, city name or state name.",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The unit of temperature.",
                            }
                        },
                        "required": ["location"],
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Name of city or state",
                            },
                            "temperature": {
                                "type": "number",
                                "description": "The current temperature.",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The unit of temperature.",
                            },
                            "weather_condition": {
                                "type": "string",
                                "enum": ["sunny", "cloudy", "rainy", "stormy"],
                                "description": "The current weather condition.",
                            },
                            "humidity": {
                                "type": "string",
                                "enum": ["high", "low"],
                                "description": "The humidity level.",
                            },
                        },
                        "required": ["temperature", "weather_condition"],
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_employees_of_manager",
                    "description": "Get employees of manager. Returns employee list information based on manager employee ID. Return value is a JSON and json_data object is a list containing employee JSON objects.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "manager_emp_id": {
                                "type": "string",
                                "description": "The ID of the manager's employee ID.",
                            }
                        },
                        "required": ["manager_emp_id"],
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "The status of the request. E.g., 'S' for success."
                            },
                            "status_text": {
                                "type": "string",
                                "description": "A text message providing additional details about the status."
                            },
                            "json_data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "The unique identifier for the employee."
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "The name of the employee."
                                        },
                                        "manager_id": {
                                            "type": "string",
                                            "description": "The ID of the manager of the employee."
                                        }
                                    },
                                    "required": ["id", "name", "manager_id"]
                                }
                            }
                        },
                        "required": ["status", "json_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_payroll_by_employee",
                    "description": "Get payroll details for a given employee ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "The ID of the employee.",
                            }
                        },
                        "required": ["employee_id"],
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "The status of the request. E.g., 'S' for success."
                            },
                            "status_text": {
                                "type": "string",
                                "description": "A text message providing additional details about the status."
                            },
                            "json_data": {
                                "type": "object",
                                "properties": {
                                    "employee_id": {
                                        "type": "string",
                                        "description": "The unique identifier of the employee."
                                    },
                                    "salary": {
                                        "type": "number",
                                        "description": "The salary of the employee."
                                    },
                                    "bonus": {
                                        "type": "number",
                                        "description": "The bonus amount for the employee."
                                    },
                                    "tax_rate": {
                                        "type": "number",
                                        "description": "The tax rate applicable to the employee."
                                    },
                                    "tax_amount": {
                                        "type": "number",
                                        "description": "The calculated tax amount for the employee."
                                    }
                                },
                                "required": ["employee_id", "salary", "bonus", "tax_rate", "tax_amount"]
                            }
                        },
                        "required": ["status", "json_data"]
                    }
                }
            }
        ]

        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
        )

        self.messages = []  # Initialize messages list
    
    def ask_question(self, question=None, image_data=None):
        try:
            # Prepare messages based on the input
            if question:
                self.messages.append({"role": "user", "content": question})

            if image_data:
                self.messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"{image_data}"}}]})

            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
            )

            # Process and return the response
            return self.process_response(response)
        
        except Exception as e:
            # Print the error if something goes wrong
            print(f"An error occurred: {e}")
            return {"error": str(e)}


    def process_response(self, response: 'ChatCompletion'):
        if response and response.choices:
            first_choice = response.choices[0]
            if first_choice.message:
                self.messages.append(first_choice.message)

                if first_choice.message.tool_calls:
                    # Create a mapping of tool call IDs to responses
                    tool_responses = {}

                    for tool_call in first_choice.message.tool_calls:
                        tool_call_id = tool_call.id
                        function_name = tool_call.function.name
                        arguments_str = tool_call.function.arguments
                        arguments_dict = json.loads(arguments_str)

                        if function_name == "get_employees_of_manager":
                            manager_emp_id = arguments_dict.get('manager_emp_id')
                            if manager_emp_id:
                                manage_emp_details = self.get_employees_of_manager(manager_emp_id)
                                tool_responses[tool_call_id] = {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "name": function_name,
                                    "content": manage_emp_details
                                }
                        elif function_name == "get_payroll_by_employee":
                            employee_id = arguments_dict.get('employee_id')
                            if employee_id:
                                payroll_details = self.get_payroll_by_employee(employee_id)
                                tool_responses[tool_call_id] = {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "name": function_name,
                                    "content": payroll_details
                                }
                        elif function_name == "get_current_weather":
                            location = arguments_dict.get('location')
                            if location:
                                weather_in_location = self.get_current_weather(location)
                                tool_responses[tool_call_id] = {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "name": function_name,
                                    "content": weather_in_location
                                }

                    # Ensure proper formatting when appending tool responses
                    for tool_call_id in tool_responses:
                        tool_response = tool_responses[tool_call_id]
                        # Ensure the content is a string or a properly formatted dictionary
                        if isinstance(tool_response["content"], dict):
                            tool_response["content"] = json.dumps(tool_response["content"])
                        self.messages.append(tool_response)

                    # Make another call with updated messages
                    return self.ask_question()
                else:
                    if response and response.choices:
                        first_choice = response.choices[0]
                        return first_choice.message.content
                    else:
                        return 'no_data!'
        else:
            return 'Whattaa ?!!'

    
    def get_current_weather(self, location, unit="celsius"):
        return get_current_weather(location)

    def get_employees_of_manager(self,manager_emp_id):
        return get_employees_of_manager(manager_emp_id)
    
    def get_payroll_by_employee(self,employee_id):
        return get_payroll_by_employee(employee_id)
    


#Can be implemented as web api. You can get that data from any 3rd party system
def get_current_weather(location, unit="celsius"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "42", "unit": unit , "weather_condition": "stormy", "humidity": "low"})
    elif "bursa" in location.lower():
        return json.dumps({"location": "Bursa", "temperature": "-12", "unit": unit , "weather_condition": "snowy", "humidity": "low"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit , "weather_condition": "sunny", "humidity": "low"})
    elif "istanbul" in location.lower():
        return json.dumps({"location": "Istanbul", "temperature": "32", "unit": unit , "weather_condition": "sunny", "humidity": "high"})
    else:
        return json.dumps({"location": location, "temperature": "unknown" , "weather_condition": "unknown", "humidity": "unknown"})


# Base URL for your FastAPI service
erp_base_url = "http://127.0.0.1:8001/"  # Replace with your actual URL

# Example function to call the POST endpoint for employees of a manager
def get_employees_of_manager(manager_emp_id):
    url = f"{erp_base_url}/get_employees_of_manager"
    data = {"query": manager_emp_id}
    response = requests.post(url, json=data)
    return response.json()

# Example function to call the POST endpoint for payroll by employee
def get_payroll_by_employee(employee_id):
    url = f"{erp_base_url}/get_payroll_by_employee"
    data = {"query": employee_id}
    response = requests.post(url, json=data)
    return response.json()


app = FastAPI()

class Query(BaseModel):
    query: str

class QueryImg(BaseModel):
    query: str
    image_data:str


@app.get("/")
async def root():
    return {"message": "Hello World"}

async def gpt4o_raw(query: str, image_data: str = None):
    try:
        bot = AzureOpenAIBot(Params.model, Params.endpoint, Params.api_version, Params.api_key)
        if image_data:
            answer = bot.ask_question(query, image_data)
        else:
            answer = bot.ask_question(query)
        return {"ai_response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gpt4o_raw/{query}")
async def gpt4o_get_raw(query: str):
    return await gpt4o_raw(query)

@app.post("/gpt4o_raw")
async def gpt4o_post_raw(query: Query):
    return await gpt4o_raw(query.query)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

#http://127.0.0.1:8002/gpt4o_raw/get%20employees%20of%20manager%20id%202