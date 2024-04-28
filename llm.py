import ast
import os

from llm_prompts import SYSTEM_EXTRACT_ASSIGNMENT_SKILLS, SYSTEM_GENERATE_RECOMMENDATIONS, SYSTEM_GENERATE_CLOSEST_SKILL_RECOMMENDATIONS, SYSTEM_SKILL_EXTRACTION
from openai import OpenAI
from pprint import pprint

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ['OPEN_AI_API_KEY'],
)

def interact_with_llm_to_get_recommendation(llm_input, job_description, debug):
    if debug:
        print(f"Generating recommendations")

    messages = [
            {"role": "system", "content": SYSTEM_GENERATE_RECOMMENDATIONS},
            {"role": "user", "content": llm_input},
            {"role": "user", "content": job_description}
        ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    llm_response = response.choices[0].message.content

    if debug:
        print("Recommendations are:")
        pprint(llm_response)
    return llm_response

def get_assignment_skills(assignment_context, debug):
    assignment_skills = {}
    if debug:
        print(f"Extracting Assignment skills using assignment context")
    messages = [
            {"role": "system", "content": SYSTEM_EXTRACT_ASSIGNMENT_SKILLS},
            {"role": "user", "content": assignment_context}
        ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assignment = response.choices[0].message.content
    assignment_skills = ast.literal_eval(assignment)
    if debug:
        print("Extracted skills are:")
        pprint(assignment_skills)

    return assignment_skills

def interact_with_llm_to_fetch_skills(job_description, resume, debug):
    llm_response_json = {}
    if debug:
        print("Extracting hard & soft skills from resume & JD. Then comparing them fetching missing skills")
    try:
        messages = [
                {"role": "system", "content": SYSTEM_SKILL_EXTRACTION},
                {"role": "user", "content": job_description},
                {"role": "user", "content": resume},
            ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        llm_response = response.choices[0].message.content
        llm_response_json = ast.literal_eval(llm_response)
        if debug:
            print("Extracted skills are:")
            pprint(llm_response_json)

    except Exception as exc:
        print(f"Unable to access ChatGpt API to extract skills `{exc}`")

    return llm_response_json

def get_closest_skill_recommendation(my_skills, skill_needed, debug):
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
            {"role": "system", "content": "You are a student career/academic advisor/ resumer builder"},
            {"role": "user", "content": msg},
            # {"role": "user", "content": output_template},
        ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    llm_response_skill_recommendation = response.choices[0].message.content

    if debug:
        print("Closest Skill Recommendations are:")
        pprint(llm_response_skill_recommendation)
    return llm_response_skill_recommendation