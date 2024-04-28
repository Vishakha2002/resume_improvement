import click
import os
import requests
import PyPDF2

from llm import get_assignment_skills, interact_with_llm_to_fetch_skills, interact_with_llm_to_get_recommendation, get_closest_skill_recommendation

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

def fetch_user_github_info(username):
    """
    API: https://api.github.com/users/<username>/repos
    Vishakha2002

    Contributions: `contributors_url`. returns a list looks for `contributions`.
    """
    github_api = os.environ['GITHUB_API_KEY']
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "Authorization": f"Bearer {github_api}"}
    distinct_language = []
    try:
        url = f"https://api.github.com/users/{username}/repos"
        # fetch all repos of the current username.
        # NOTE: Only public repos will be available here.
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

        distinct_language = get_all_distinct_language(temp_data['languages_urls'], headers)


    except Exception as exc:
        print(f"Unable to contact github API due to {exc}.\n")
        print(exc)

    return distinct_language

def read_pdf_files(directory_path, debug):
    # Step 1: Check if directory exists
    if not os.path.isdir(directory_path):
        print("Invalid directory path.")
        return None

    text_data = []
    # Step 2: Read PDF files and convert to text
    if debug:
        print(f"Reading all PDF files in {directory_path} and converting them to text to extract assignment soft and hard skills")
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

                text_data.append(pdf_text)

    return str(text_data)

def pretty_print_list(list_to_print):
    if list_to_print:
        for item in list_to_print:
            print(f" - {item}")
    else:
        print(" - Not Specified")

def pretty_print_context(context):

    print("** Resume | Hard Skills **")
    pretty_print_list(context.get("resume").get("hard_skills"))
    print("\n")

    print("** Resume | Soft Skills **")
    pretty_print_list(context.get("resume").get("soft_skills"))
    print("\n")

    print("** Job Description | Hard Skills **")
    pretty_print_list(context.get("job_description").get("hard_skills"))
    print("\n")

    print("** Job Description | Soft Skills **")
    pretty_print_list(context.get("job_description").get("soft_skills"))
    print("\n")
    print("** Missing | Hard Skills **")
    pretty_print_list(context.get("missing_skills").get("hard_skills"))
    print("\n")

    print("** Missing | Soft Skills **")
    pretty_print_list(context.get("missing_skills").get("soft_skills"))
    print("\n")

    print("** GitHub Skills | Hard Skills **")
    pretty_print_list(context.get("github_skills").get("hard_skills"))
    print("\n")

    print("** Assignment Skills | Hard Skills **")
    pretty_print_list(context.get("assignment_skills").get("hard_skills"))
    print("\n")

    print("** Assignment Skills | Soft Skills**")
    pretty_print_list(context.get("assignment_skills").get("soft_skills"))
    print("\n")


# Command-line interface using Click and main function calling all other functions
@click.command()
@click.option("--job-description", type=str, help="Job description for skill extraction")
@click.option("--job-description-path", type=click.Path(exists=True, file_okay=True, dir_okay=False), help="Path to job description file. File Must be txt or pdf file")
@click.option("--resume", type=str, help="Resume for skill matching")
@click.option("--resume-path", type=click.Path(exists=True, file_okay=True, dir_okay=False), help="Path to resume file. File Must be txt or pdf file")
@click.option("--assignment-path", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True), help="Path to assignment file. File Must be txt or pdf file. It is needed to get the missing skills")
@click.option("--github-userid", required=False, type=str, help="GitHub user ID")
@click.option('--debug', is_flag=True, help="Enable verbose/debug mode")
def snoopy(job_description, job_description_path, resume, resume_path, assignment_path, github_userid, debug):
    github_skills = None

    if debug:
        print("Validating if the job description/job_description_path is provided")
    if not job_description and not job_description_path:
        print("Neither --job-description nor --job-description-path was provided.")
        print_help_and_exit()

    if debug:
        print("Validating if the resume/resume_path is provided and is valid")
    if not resume and not resume_path:
        print("Neither --resume or --resume_path was provided.")
        print_help_and_exit()

    if debug and job_description_path:
        print("Validating if the provided job_description_path is valid")
    if job_description_path and not is_valid_file(job_description_path):
        print_help_and_exit()

    if debug and resume_path:
        print("Validating if the provided resume_path is valid")
    if resume_path and not is_valid_file(resume_path):
        print_help_and_exit()

    if debug and assignment_path:
        print("Validating if the provided assignment_path is valid")
    if assignment_path and not os.path.isdir(assignment_path):
        print("Invalid directory path {assignment_path}.")
        print_help_and_exit()

    # Prompt user for GitHub user ID if not provided
    if not github_userid:
        will_provide_github_userid = click.prompt("Do you want to provide your github id to fetch soft and hard skills?", default="N", type=click.Choice(['Y', 'N']))
        if not will_provide_github_userid == "N":
            github_userid = click.prompt("Github Userid")
            if debug:
                print("Validating if the github user is provided is valid")
            if not user_exists(github_userid):
                print(f"Please ensure `{github_userid}` is the correct github id or try again later. For now, skipping pulling information github")
            # Fetch the user repos
            github_skills = fetch_user_github_info(github_userid)
            if debug:
                print(f"Extracted distint languages for github user({github_userid}) are {github_skills}")
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

    assignment_context = read_pdf_files(assignment_path, debug)
    assignment_skills = get_assignment_skills(assignment_context, debug)

    jd_resume_skills = interact_with_llm_to_fetch_skills(job_description, resume, debug)
    llm_input_json = {**assignment_skills, **jd_resume_skills, "github_skills": {"hard_skills" : github_skills}}

    pretty_print_context(llm_input_json)
    print("Skills extraction is complete.")
    print("Now, fetching recommendations for the user.")

    llm_response = interact_with_llm_to_get_recommendation(str(llm_input_json), job_description, debug)
    print(llm_response)

    myskills = list(llm_input_json["github_skills"]["hard_skills"]) + llm_input_json["assignment_skills"]["hard_skills"]

    print('\n'+'***********************'+'\n')
    for skill in llm_input_json["missing_skills"]["hard_skills"]:
        llm_closest_skill_response = get_closest_skill_recommendation(myskills, skill, debug)
        print('\n' + llm_closest_skill_response)

    # llm_closest_skill_response = get_closest_skill_recommendation(str(llm_input_closest_skill), job_description, debug)



if __name__ == "__main__":
    snoopy()