"""
Information about the server that can be safely shared with students.
Confidential information about the server and its deployment should go
in master_grader/server.py, not here.
"""

from enum import Enum
from config import MODE


class RequiredRequestFields(Enum):
    """All must be in body to make a valid request to the gpt220 server."""

    PROJECT_ID = "project_id"
    QUESTION_ID = "question_id"
    EXPECTED_ANSWER = "expected_answer"
    PROMPT = "prompt"
    STUDENT_CODE = "student_code"
    AUTOGRADER_OUTPUT = "autograder_output"
    LANGUAGE = "language"


# The URL to hit to access our LLM feedback service. This is
# viewable in the top center of the screen when viewing the
# gpt220 service. Uncomment the line below when running tests
# using the locally running docker container for the server.
# Otherwise, all requests should route to the deployed server.

if MODE == "deploy":
    GPT_SERVICE_PUBLIC_URL = "https://feedback.cs220-feedback-server.cs.wisc.edu/"
elif MODE == "dev":
    GPT_SERVICE_PUBLIC_URL = "http://0.0.0.0:8080/"
else:
    raise ValueError(f"Unknown mode: {MODE}. Expected 'deploy' or 'dev'.")
