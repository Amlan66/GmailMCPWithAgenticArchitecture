# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics
import subprocess
import pydirectinput
import pyautogui
import keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from model import *

# Load environment variables from .env file
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Get Gmail API service"""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for paint app
paint_app = None

# DEFINE TOOLS WITH PYDANTIC MODELS

# Mathematical operations
@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """Add two numbers"""
    print("CALLED: add(input: AddInput) -> AddOutput:")
    result = int(input.a + input.b)
    return AddOutput(result=result)

@mcp.tool()
def add_list(input: AddListInput) -> AddListOutput:
    """Add all numbers in a list"""
    print("CALLED: add_list(input: AddListInput) -> AddListOutput:")
    try:
        if not input.l:
            raise ValueError("List cannot be empty")
        result = sum(input.l)
        print(f"Successfully calculated sum: {result}")
        return AddListOutput(result=result)
    except Exception as e:
        print(f"ERROR in add_list: {str(e)}")
        raise

@mcp.tool()
def subtract(input: SubtractInput) -> SubtractOutput:
    """Subtract two numbers"""
    print("CALLED: subtract(input: SubtractInput) -> SubtractOutput:")
    result = int(input.a - input.b)
    return SubtractOutput(result=result)

@mcp.tool()
def multiply(input: MultiplyInput) -> MultiplyOutput:
    """Multiply two numbers"""
    print("CALLED: multiply(input: MultiplyInput) -> MultiplyOutput:")
    result = int(input.a * input.b)
    return MultiplyOutput(result=result)

@mcp.tool()
def divide(input: DivideInput) -> DivideOutput:
    """Divide two numbers"""
    print("CALLED: divide(input: DivideInput) -> DivideOutput:")
    result = float(input.a / input.b)
    return DivideOutput(result=result)

@mcp.tool()
def power(input: PowerInput) -> PowerOutput:
    """Power of two numbers"""
    print("CALLED: power(input: PowerInput) -> PowerOutput:")
    result = int(input.a ** input.b)
    return PowerOutput(result=result)

@mcp.tool()
def sqrt(input: SqrtInput) -> SqrtOutput:
    """Square root of a number"""
    print("CALLED: sqrt(input: SqrtInput) -> SqrtOutput:")
    result = float(input.a ** 0.5)
    return SqrtOutput(result=result)

@mcp.tool()
def cbrt(input: CbrtInput) -> CbrtOutput:
    """Cube root of a number"""
    print("CALLED: cbrt(input: CbrtInput) -> CbrtOutput:")
    result = float(input.a ** (1/3))
    return CbrtOutput(result=result)

@mcp.tool()
def factorial(input: FactorialInput) -> FactorialOutput:
    """factorial of a number"""
    print("CALLED: factorial(input: FactorialInput) -> FactorialOutput:")
    result = int(math.factorial(input.a))
    return FactorialOutput(result=result)

@mcp.tool()
def log(input: LogInput) -> LogOutput:
    """log of a number"""
    print("CALLED: log(input: LogInput) -> LogOutput:")
    result = float(math.log(input.a))
    return LogOutput(result=result)

@mcp.tool()
def remainder(input: RemainderInput) -> RemainderOutput:
    """remainder of two numbers divison"""
    print("CALLED: remainder(input: RemainderInput) -> RemainderOutput:")
    result = int(input.a % input.b)
    return RemainderOutput(result=result)

@mcp.tool()
def sin(input: SinInput) -> SinOutput:
    """sin of a number"""
    print("CALLED: sin(input: SinInput) -> SinOutput:")
    result = float(math.sin(input.a))
    return SinOutput(result=result)

@mcp.tool()
def cos(input: CosInput) -> CosOutput:
    """cos of a number"""
    print("CALLED: cos(input: CosInput) -> CosOutput:")
    result = float(math.cos(input.a))
    return CosOutput(result=result)

@mcp.tool()
def tan(input: TanInput) -> TanOutput:
    """tan of a number"""
    print("CALLED: tan(input: TanInput) -> TanOutput:")
    result = float(math.tan(input.a))
    return TanOutput(result=result)

@mcp.tool()
def mine(input: MineInput) -> MineOutput:
    """special mining tool"""
    print("CALLED: mine(input: MineInput) -> MineOutput:")
    result = int(input.a - input.b - input.b)
    return MineOutput(result=result)

# Add this tool to your existing action.py file, after the other mathematical operations

@mcp.tool()
def verify(input: VerifyInput) -> VerifyOutput:
    """Verify if a calculation is correct"""
    print("CALLED: verify(input: VerifyInput) -> VerifyOutput:")
    print(f"Verifying: {input.expression} = {input.expected}")
    
    try:
        # Create a safe namespace with math functions for eval
        import math
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "len": len, "int": int, "float": float,
            # Math functions
            "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "pi": math.pi, "e": math.e, "pow": pow,
            # Allow basic arithmetic
            "math": math
        }
        
        # Evaluate the expression safely with math functions available
        actual = float(eval(input.expression, safe_dict))
        expected = float(input.expected)
        
        # Use relative tolerance for large numbers, absolute tolerance for small numbers
        if abs(expected) > 1e-6:
            # For large numbers, use relative tolerance (0.01% difference allowed)
            relative_error = abs(actual - expected) / abs(expected)
            is_correct = relative_error < 1e-4  # 0.01% tolerance
        else:
            # For small numbers, use absolute tolerance
            is_correct = abs(actual - expected) < 1e-10
        
        print(f"DEBUG: actual={actual}, expected={expected}")
        if abs(expected) > 1e-6:
            relative_error = abs(actual - expected) / abs(expected)
            print(f"DEBUG: relative_error={relative_error}, threshold=1e-4")
        
        if is_correct:
            print(f"CORRECT! {input.expression} = {input.expected}")
            result_text = "True"
        else:
            print(f"INCORRECT! {input.expression} should be {actual}, got {input.expected}")
            result_text = "False"
            
        return VerifyOutput(result=result_text)
        
    except Exception as e:
        print(f"Error in verification: {str(e)}")
        return VerifyOutput(result=f"Error: {str(e)}")

# String and list operations
@mcp.tool()
def strings_to_chars_to_int(input: StringsToCharsToIntInput) -> StringsToCharsToIntOutput:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(input: StringsToCharsToIntInput) -> StringsToCharsToIntOutput:")
    result = [int(ord(char)) for char in input.string]
    return StringsToCharsToIntOutput(result=result)

@mcp.tool()
def int_list_to_exponential_sum(input: IntListToExponentialSumInput) -> IntListToExponentialSumOutput:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(input: IntListToExponentialSumInput) -> IntListToExponentialSumOutput:")
    try:
        if not input.int_list:
            raise ValueError("List cannot be empty")
        result = sum(math.exp(i) for i in input.int_list)
        print(f"Successfully calculated exponential sum: {result}")
        return IntListToExponentialSumOutput(result=result)
    except Exception as e:
        print(f"ERROR in int_list_to_exponential_sum: {str(e)}")
        raise

@mcp.tool()
def fibonacci_numbers(input: FibonacciNumbersInput) -> FibonacciNumbersOutput:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(input: FibonacciNumbersInput) -> FibonacciNumbersOutput:")
    if input.n <= 0:
        return FibonacciNumbersOutput(result=[])
    fib_sequence = [0, 1]
    for _ in range(2, input.n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    result = fib_sequence[:input.n]
    return FibonacciNumbersOutput(result=result)

# System operations (removed Image operations section)
@mcp.tool()
async def draw_rectangle_and_text(input: DrawRectangleAndTextInput) -> DrawRectangleAndTextOutput:
    """Draw a rectangle and add text in Paint with specified color"""
    print("=" * 50)
    print("DRAW RECTANGLE AND TEXT FUNCTION STARTED!")
    print(f"CALLED: draw_rectangle_and_text with text='{input.text}', color='{input.color}'")
    print("=" * 50)
    global paint_app
    try:
        if not paint_app:
            return DrawRectangleAndTextOutput(
                content=[
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            )
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Make sure Paint is active
        paint_window.set_focus()
        time.sleep(0.5)
        
        # Select color based on input
        print(f"Starting color selection for color: {input.color}")
        color_selected = False
        color_file_map = {
            "red": "red_icon.jpg",
            "yellow": "yellow_icon.jpg", 
            "green": "green_icon.jpg",
            "black": None  # Default color, no need to click
        }
        
        # Get the color file for the requested color
        color_file = color_file_map.get(input.color.lower())
        
        if color_file:
            # Find and click the color icon
            try:
                print(f"Looking for color file: {color_file}")
                color_location = pyautogui.locateCenterOnScreen(color_file, confidence=0.8)
                print(f"Color location result: {color_location}")
                if color_location:
                    x, y = color_location
                    print(f"{input.color.capitalize()} color found at: {x}, {y}")
                    pydirectinput.click(x, y)
                    color_selected = True
                    time.sleep(0.5)
                else:
                    print(f"{input.color.capitalize()} color icon not found on screen.")
                    print(f"Tried to find: {color_file}")
                    return DrawRectangleAndTextOutput(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Error: {input.color} color icon not found. Available colors: red, yellow, green, black"
                            )
                        ]
                    )
            except Exception as e:
                print(f"Exception during color selection: {str(e)}")
                print(f"Error selecting {input.color} color: {str(e)}")
                return DrawRectangleAndTextOutput(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error selecting {input.color} color: {str(e)}"
                        )
                    ]
                )
        elif input.color.lower() == "black":
            print("Using default black color")
            color_selected = True
        else:
            return DrawRectangleAndTextOutput(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: Unsupported color '{input.color}'. Available colors: red, yellow, green, black"
                    )
                ]
            )
        
        # Find rectangle tool icon on screen
        location = pyautogui.locateCenterOnScreen("rectangle_icon.jpg", confidence=0.8)
        if location:
            x, y = location
            print(f"Rectangle tool found at: {x}, {y}")
            pydirectinput.click(x, y)
        else:
            print("Rectangle tool icon not found on screen.")
            return DrawRectangleAndTextOutput(
                content=[
                    TextContent(
                        type="text",
                        text="Error: Rectangle tool icon not found on screen."
                    )
                ]
            )

        time.sleep(0.5)
        
        # Draw a rectangle first (using fixed coordinates for consistency)
        pydirectinput.moveTo(300, 400)
        pydirectinput.mouseDown()
        pydirectinput.moveTo(700, 700)
        pydirectinput.mouseUp()
        time.sleep(0.5)
        
        # Select text tool using keyboard shortcut
        pydirectinput.press('t')
        time.sleep(0.5)
        
        # Click where to start typing (inside the rectangle)
        pydirectinput.click(400, 500)
        time.sleep(0.5)
        
        # Type the text
        keyboard.write(input.text, delay=0.05)
        # Click outside to finish text entry
        pydirectinput.click(800, 800)
        
        return DrawRectangleAndTextOutput(
            content=[
                TextContent(
                    type="text",
                    text=f"Rectangle drawn and text '{input.text}' added successfully in {input.color} color"
                )
            ]
        )
    except Exception as e:
        return DrawRectangleAndTextOutput(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )

@mcp.tool()
async def open_paint(input: OpenPaintInput) -> OpenPaintOutput:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    try:
        subprocess.run(['cmd', '/c', 'start', 'mspaint'], shell=True)
        time.sleep(2)
        paint_app = Application().connect(class_name='MSPaintApp')
        time.sleep(0.2)
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        
        # First move to secondary monitor without specifying size
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            0, 0,  # Position it on secondary monitor
            0, 0,  # Let Windows handle the size
            win32con.SWP_NOSIZE  # Don't change the size
        )
        
        # Now maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.2)
        
        return OpenPaintOutput(
            content=[
                TextContent(
                    type="text",
                    text="Paint opened successfully on primary monitor and maximized"
                )
            ]
        )
    except Exception as e:
        return OpenPaintOutput(
            content=[
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        )

@mcp.tool()
async def send_email(input: SendEmailInput) -> SendEmailOutput:
    """Send email using Gmail API with personalized greeting and signature"""
    print(f"CALLED: send_email(input: SendEmailInput) -> SendEmailOutput:")
    
    try:
        # Get Gmail service
        service = get_gmail_service()
        
        # Replace literal \n with actual line breaks in the body
        formatted_body = input.body.replace('\\n', '\n')
        
        # Create email body with personalized greeting and signature
        email_body = f"Hi {input.receiver_name},\n\n{formatted_body}\n\nThanks,\nAmlan"
        
        # Create message
        message = MIMEMultipart()
        message["To"] = input.receiver_email
        message["Subject"] = input.subject
        message.attach(MIMEText(email_body, "plain"))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email
        send_message = service.users().messages().send(
            userId="me", 
            body={'raw': raw_message}
        ).execute()
        
        return SendEmailOutput(
            content=[
                TextContent(
                    type="text",
                    text=f"Email sent successfully to {input.receiver_email} with subject '{input.subject}' (Message ID: {send_message['id']})"
                )
            ]
        )
        
    except FileNotFoundError:
        return SendEmailOutput(
            content=[
                TextContent(
                    type="text",
                    text="Error: credentials.json file not found. Please download it from Google Cloud Console and place it in the project directory."
                )
            ]
        )
    except Exception as e:
        return SendEmailOutput(
            content=[
                TextContent(
                    type="text",
                    text=f"Error sending email: {str(e)}"
                )
            ]
        )

# DEFINE RESOURCES (unchanged from original)
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"

# DEFINE AVAILABLE PROMPTS (unchanged from original)
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING THE SERVER AT AMAZING LOCATION")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
