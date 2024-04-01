import os
import sys
import click
import pprint
import PyPDF2
import requests
import numpy as np
import ast



from openai import OpenAI

# System input for the chat completion
SYSTEM_INPUT = """ You will be provided with four inputs: resume, job_description, github_context and pdf_text_data.
Extract Hard Skills and Soft Skills from both resume and job_description.
Compare all the Hard Skills and Soft Skills from resume and job_description to show the user all the Hard Skills and Soft Skills from the job_description that did not match
with the resume's Hard Skills and Soft Skills. We are calling these unmatched hard skills and soft skills as missing skills.

github_context contains the hard skills fetched from user’s github repositories.
Extract hard skills and soft skills from the pdf_text_data.

The skills extracted from github_context and pdf_text_data means that the user has worked on those skills before. So, provide recommendations ONLY on missing skills from resume
and those recommendations should only be based on hard skills extracted from github_context and pdf_text_data. Generate recommendations on missing soft skills like "If you have
any experience working on this skill, add it to the resume". 
For example, if one of the missing skill is C# and C# is mentioned in skills extracted from github_context or pdf_text_data, then give the suggestion somewhat like 
‘You have worked on C# before as per your github or assignments, you can add this to your resume’.

Of all the relevant skills you are finding for missing skills, Generate recommendations on most relevant skills by picking first 2 skills and recommend like "You"

Rules:
1. Do not recommendations skills if only present in Job Description and not present in any other inputs. 
2. Hard Skill Recommendations should be based on github_context, pdf_text_data and relevant skills. 
3. Output format has to be following
{
  "resume": {
    "hard_skills": [],
    "soft_skills": []
  },
  "job_description": {
    "hard_skills": [],
    "soft_skills": []
  },
  "missing_skills": {
    "hard_skills": [],
    "soft_skills": []
  },
  "github_skills": {
    "hard_skills": [],
    "soft_skills": []
  },
  "pdf_text_skills": {
    "hard_skills": [],
    "soft_skills": []
  },
  "recommendations": {
    "improvements": []
  }
}
"""

# Initialize OpenAI client
client = OpenAI(
    api_key='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',
)

def pretty_print_list(list_to_print):
    if list_to_print:
        for item in list_to_print:
            print(f" - {item}")
    else:
        print(" - Not Specified")


def pretty_print_llm_response(llm_response):

    print("** Resume | Hard Skills **")
    pretty_print_list(llm_response.get("resume").get("hard_skills"))
    print("\n")

    print("** Resume | Soft Skills **")
    pretty_print_list(llm_response.get("resume").get("soft_skills"))
    print("\n")

    print("** Job Description | Hard Skills **")
    pretty_print_list(llm_response.get("job_description").get("hard_skills"))
    print("\n")

    print("** Job Description | Soft Skills **")
    pretty_print_list(llm_response.get("job_description").get("soft_skills"))
    print("\n")
    print("** Missing | Hard Skills **")
    pretty_print_list(llm_response.get("missing_skills").get("hard_skills"))
    print("\n")

    print("** Missing | Soft Skills **")
    pretty_print_list(llm_response.get("missing_skills").get("soft_skills"))
    print("\n")

    print("** GitHub Skills **")
    pretty_print_list(llm_response.get("github_skills").get("hard_skills"))
    print("\n")

    print("** Assignment Skills **")
    pretty_print_list(llm_response.get("pdf_text_skills").get("hard_skills"))
    print("\n")

    print("** Improvement Recommendations **")
    pretty_print_list(llm_response.get("recommendations").get("improvements"))

def interact_with_llm(job_description, resume, github_context,pdf_text_data):

    # # Initialize OpenAI client
    # client = OpenAI(
    #   api_key='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',
    # )
    try:
        messages = [
                {"role": "system", "content": SYSTEM_INPUT},
                {"role": "user", "content": job_description},
                {"role": "user", "content": resume},
                {"role": "user", "content": pdf_text_data}
            ]
        if github_context:
            messages.append({"role": "user", "content": github_context})
        # try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # prompt=user_input,
            messages=messages
        )
        llm_response = response.choices[0].message.content
        # print(llm_response)
        llm_response_json = ast.literal_eval(llm_response)
        pretty_print_llm_response(llm_response_json)
    except Exception as exc:
        print(f"Unable to access ChatGpt API to extract skills `{exc}`")

    # print(type(llm_response_json))
    missing_hard_skill = llm_response_json.get("missing_skills").get("hard_skills")
    github_assignment_hard_skills = llm_response_json.get("pdf_text_skills").get("hard_skills") + llm_response_json.get("github_skills").get("hard_skills")
    # XXX Vishakha here
    print(f"\nMissing Hard Skills to be used for finding similarities: {missing_hard_skill}")
    print(f"Github & Assignment Hard Skills to be used for finding similarities: {github_assignment_hard_skills}\n")

    try:
        # XXX TODO - finish this
        embedding_github_assignment_hard_skills = get_embeddings(github_assignment_hard_skills)
        for skill in missing_hard_skill:
            relevant_skills = find_most_relevant_skills(skill, embedding_github_assignment_hard_skills)
            print(f"Most relevant skills for {skill}:  {relevant_skills}")

    except Exception as exc:
        print(f"Unable to access ChatGpt API due to find similar skills `{exc}`")

    # call the new llm function with input you need to feed it, that may include resume /jd /skills and new relavent skills to fetch suggestion.

###########################################################
# Create embeddings for each skill
def get_embeddings(skills):
    skill_embeddings = {}
    for skill in skills:
        response = client.embeddings.create(
            input=skill,
            model="text-embedding-ada-002"
        )
        skill_embeddings[skill] = response.data[0].embedding

    return skill_embeddings

# Given an input skill, find the most relevant skills
def find_most_relevant_skills(input_skill, skill_embeddings, top_n=3):
    # print(skill_embeddings)
    input_embedding = client.embeddings.create(
        input=input_skill,
        model="text-embedding-ada-002"
    ).data[0].embedding

    # Calculate cosine similarity between the input skill and all other skills
    similarities = {}
    for skill, embedding in skill_embeddings.items():
        similarity = np.dot(input_embedding, embedding) / (np.linalg.norm(input_embedding) * np.linalg.norm(embedding))
        similarities[skill] = similarity

    # Sort skills based on similarity and return the top N
    relevant_skills = sorted(similarities, key=similarities.get, reverse=True)[:top_n]
    # print(relevant_skills)
    return relevant_skills
############################################################

def read_pdf_files(directory_path):
    # Step 1: Check if directory exists
    if not os.path.isdir(directory_path):
        print("Invalid directory path.")
        return None

    text_data = []
    # Step 2: Read PDF files and convert to text
    for filename in os.listdir(directory_path):
        # Initialize an empty list to store text data

        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Initialize an empty string to store text from the PDF
                pdf_text = ''
                # Read each page of the PDF and append text to pdf_text
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_text += page.extract_text().replace('\n', ' ')
                # print(f"{type(pdf_text)}")
                # pdf_text.replace('\n', ' ')
                text_data.append(pdf_text)

    return str(text_data)

def get_all_distinct_language(repos_langauge_urls, headers):
    return_value= []
    for url in repos_langauge_urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            languages = response.json()
            if len(languages) > 0:
                for lang in languages:
                    return_value.append(lang)
        except Exception as exc:
            continue
    return set(return_value)

def has_collaborated(list_of_repos_contributors, headers):
    """
    Return True if has contributor in any repo. It will return true as soon as
    first repo is found which has contributor.
    XXX BUG- It is fetching info even for the forked repos.
    """
    for url in list_of_repos_contributors:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            contributors = response.json()
            if len(contributors) > 1:
                return True
        except Exception as exc:
            continue

    return False

def fetch_user_github_info(username):
    """
    API: https://api.github.com/users/<username>/repos
    Vishakha2002

    Contributions: `contributors_url`. returns a list looks for `contributions`.
    """
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "Authorization": "Bearer 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"}
    distinct_language = []
    try:
        url = f"https://api.github.com/users/{username}/repos"
        # fetch all repos of the current username. NOTE: Only public repos will be available here.
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        temp_data = {}
        for repo in repos:
            if repo['fork']:
                print(f"Skipping {repo['full_name']} as its a forked repo")
                continue
            if repo['languages_url']:
                if temp_data.get('languages_urls'):
                    temp_data['languages_urls'].append(repo['languages_url'])
                else:
                    temp_data['languages_urls']= [repo['languages_url']]


            if repo['contributors_url']:
                if not temp_data.get('contributors_url'):
                    temp_data['contributors_url'] = [repo['contributors_url']]
                else:
                    temp_data['contributors_url'].append(repo['contributors_url'])

        # pprint.pprint(temp_data)
        collaboration = has_collaborated(temp_data['contributors_url'], headers)
        distinct_language = get_all_distinct_language(temp_data['languages_urls'], headers)


    except Exception as exc:
        print(f"Unable to contact github API due to {exc}.\n")
        print(exc)

    return distinct_language

def user_exists(username):
    if not username:
        return False
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url)
        return response.ok
    except Exception as exc:
        print(f"Unable to contact github API due to {exc}.\n")

    return False

def print_help_and_exit():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

def is_valid_file(value):
    _, ext = os.path.splitext(value)
    if ext in [".pdf", ".txt"]:
        return True
    print(f"File {value} is not a .txt or .pdf file")
    return False

# Command-line interface using Click
@click.command()
@click.option("--job-description", type=str, help="Job description for skill extraction")
@click.option("--job-description-path", type=click.Path(exists=True, file_okay=True, dir_okay=False), help="Path to job description file. File Must be txt or pdf file")
@click.option("--resume", type=str, help="Resume for skill matching")
@click.option("--resume-path", type=click.Path(exists=True, file_okay=True, dir_okay=False), help="Path to resume file. File Must be txt or pdf file")
@click.option("--resume-db", is_flag=True, help="Flag to tell cli to use first 5 default resume db")
@click.option("--github-userid", type=str, help="GitHub user ID (optional)")
def snoopy(job_description, job_description_path, resume, resume_path, resume_db, github_userid):
    github_context = None
    if not job_description and not job_description_path:
        print("Neither --job-description nor --job-description-path was provided.")
        print_help_and_exit()

    if not resume and not resume_path and not resume_db:
        print("Neither --resume or --resume_path was provided.")
        print_help_and_exit()

    if job_description_path and not is_valid_file(job_description_path):
        print_help_and_exit()

    if resume_path and not is_valid_file(resume_path):
        print_help_and_exit()

    # Prompt user for GitHub user ID if not provided
    if not github_userid:
        will_provide_github_userid = click.prompt("Do you want to provide your github id to fetch soft and hard skills?", default="N", type=click.Choice(['Y', 'N']))
        if not will_provide_github_userid == "N":
            github_userid = click.prompt("Github Userid")
            if not user_exists(github_userid):
                print(f"Please ensure `{github_userid}` is the correct github id or try again later. For now, skipping pulling information github")
            # Fetch the user repos
            github_context = str(fetch_user_github_info(github_userid))
        else:
            print("Skipping fetching soft and hard skills using Github")

    # Read job description from file if path is provided
    if job_description_path:
        with open(job_description_path, "r") as jd_file:
            job_description = jd_file.read()

    # Read resume from file if path is provided
    if resume_path:
        with open(resume_path, "r") as resume_file:
            resume = resume_file.read()

    if resume_db:
        resume_directory_path = "/Users/vtyagi/Desktop/Copy of data.jsonl"

        with open(resume_directory_path, "r") as resume_file:
            resume = resume_file.readline()
        # print("........................\n")


    directory_path = "/Users/vtyagi/Desktop"
    pdf_text_data = read_pdf_files(directory_path)
    # if pdf_text_data:
    #     print(pdf_text_data)

    # Write a funciton to call interact_with_llm which does your work
    interact_with_llm(job_description, resume, github_context,pdf_text_data)
    # From function fetch_user_github_info, we need languages from the repo the user has contributed to

if __name__ == "__main__":
    snoopy()