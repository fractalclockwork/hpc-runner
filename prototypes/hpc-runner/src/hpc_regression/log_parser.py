# tiny_log_parser.py
import json
import re
from typing import Literal

# building in an unknown so that, in the future, we can think about extracting different statuses
Status = Literal["success", "failure", "unknown"]

def parse_structlog_status(text: str) -> Status:
    """
    Parse structlog-style lines and infer status from runner.finish returncode.
    Looks for lines containing 'event": "runner.finish"' and a JSON object.
    """
    for line in text.splitlines():
        if '"runner.finish"' in line or '"event": "runner.finish"' in line:

            # Extract the JSON object: substring from first '{' to last '}'
            start = line.find("{")
            end = line.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    payload = json.loads(line[start:end+1])

                    # use the return code to determine success or failure
                    rc = payload.get("returncode")

                    # print(rc)  # Debugging output
                    # print(type(rc))  # Debugging output
                    if rc == 0:
                        return "success"
                    
                    # if any other number
                    elif isinstance(rc, int):
                        return "failure"
                # if error
                except json.JSONDecodeError:

                    # this could be a little more well-thought out, how do we want
                    # a parsing failure to be handled?
                    return "failure"
                
    # for spooky errors that I didn't think about 
    return "unknown"