import re
import pandas as pd
import numpy as np
import time

def extract_and_remove_component_scores(text):
    # Regular expression pattern to find ```python ... ```
    pattern = r'```python(.*?)```'
    
    # Find the matching block
    match = re.search(pattern, text, re.DOTALL)
    
    components = {}
    if match:
        # Extract the content inside ```
        code_block = match.group(1).strip()
        
        # Execute the Python code to populate components dictionary
        exec(code_block, {}, components)
        
        # Remove the matched block from the original text
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    return text.strip(), components

def stream_gen(text):
    for word in text:
        yield word
        time.sleep(0.01)