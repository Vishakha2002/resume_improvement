import ast
import os
import sys
import click
from pprint import pprint
import google.generativeai as genai
from llm_prompts import SYSTEM_EXTRACT_ASSIGNMENT_SKILLS, SYSTEM_GENERATE_RECOMMENDATIONS, SYSTEM_GENERATE_CLOSEST_SKILL_RECOMMENDATIONS, SYSTEM_SKILL_EXTRACTION

import google.ai.generativelanguage as glm
try:
    GOOGLE_API_KEY=os.environ['GOOGLE_API_KEY']
except KeyError:
    click.echo("Please follow README instructions to fetch and set GOOGLE_API_KEY. Exiting now.")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]
model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)

def gemini_fetch_skills(job_description, resume, debug):
    llm_response_json = {}
    if debug:
        print("Extracting hard & soft skills from resume & JD. Then comparing them fetching missing skills")
    try:

        messages = [
                {"role": "user", "parts": [SYSTEM_SKILL_EXTRACTION, job_description, resume, "Do not send a pretty print json."]},
            ]
        response = model.generate_content(messages)

        llm_response = response.text

        if llm_response.startswith("```"):
            llm_response = llm_response[3:]

        if llm_response.endswith("```"):
            llm_response = llm_response[:-3]

        llm_response_json = ast.literal_eval(llm_response)
        if debug:
            print("Extracted skills are:")
            pprint(llm_response_json)

    except Exception as exc:
        print(f"Unable to access Gemini API to extract skills `{exc}`")

    return llm_response_json

def gemini_get_assignment_skills(assignment_context, debug):
    assignment_skills = {}
    if debug:
        print(f"Extracting Assignment skills using assignment context")

    messages = [
                {"role": "user", "parts": [SYSTEM_EXTRACT_ASSIGNMENT_SKILLS, assignment_context, "Do not send a pretty print json."]},
            ]

    response = model.generate_content(messages)

    assignment = response.text
    assignment_skills = ast.literal_eval(assignment)
    if debug:
        print("Extracted skills are:")
        pprint(assignment_skills)

    return assignment_skills

def gemini_get_recommendation(llm_input, job_description, debug):
    if debug:
        print(f"Generating recommendations")

    messages = [
                {"role": "user", "parts": [SYSTEM_GENERATE_RECOMMENDATIONS, llm_input, job_description, "Do not send a pretty print json."]},
            ]
    response = model.generate_content(messages)

    llm_response = response.text

    if debug:
        print("Recommendations are:")
        pprint(llm_response)
    return llm_response

def gemini_get_closest_skill_recommendation(my_skills, skill_needed, debug):
    msg = f"""I have skills in {my_skills} What are the closest skills among these to {skill_needed}, which I need to learn?
    """
#     output_template ="""
#     - Format:
#     Among the skills you listed, the closest skills to {skill_needed} that you may want to focus on learning include:
#     1. ..
#     ..
#     - No addtional new lines between the recommendation in case of multiple reommendations
# """
    if debug:
        print(f"Generating closest skills recommendations")

    messages = [
                {"role": "user", "parts": [SYSTEM_GENERATE_CLOSEST_SKILL_RECOMMENDATIONS, msg, "Do not send a pretty print json."]},
            ]
    response = model.generate_content(messages)

    llm_response_skill_recommendation = response.text
    if debug:
        print("Closest Skill Recommendations are:")
        pprint(llm_response_skill_recommendation)
    return llm_response_skill_recommendation
