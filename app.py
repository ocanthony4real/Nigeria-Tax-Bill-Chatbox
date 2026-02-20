"""
Entry point for AWS App Runner deployment.
This file imports and runs the Gradio chat UI.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the chat UI
from tools.chat_ui import demo

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=port,
        show_error=False,
        show_api=False,
    )
