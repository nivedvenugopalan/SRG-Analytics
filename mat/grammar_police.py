import json
from language_tool_python import LanguageTool

tool = LanguageTool('en-GB')


def check_grammar(text):
    matches = tool.check(text)

    # make all the matches a readable string
    return [repr(match) for match in matches]
