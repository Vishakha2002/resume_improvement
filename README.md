# resume_improvement
Identification of Missing Skills and Generating Recommendations for Resume Improvement based on academic profile using Large Language Model.


# Setup Dev environment for snoopy
Resume improvement tool snoopy need Python version > `3.9+`
Currently built on following python version:
```
$ python --version
Python 3.12.3
```

### Clone Github repo
Clone this repo on your local machine
```
git clone https://github.com/Vishakha2002/resume_improvement.git
```

### Create a virtual environment
```
python3 -m venv snoopy
```

### Activate the virtual environment
```
source snoopy/bin/activate
```

### install required python packages
```
pip install -r requirements.txt
```

### Fetch github token

Use [this](https://docs.github.com/en/enterprise-server@3.9/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens) document to fetch your personal github token.

Then set it as environment variable using following command
```
export GITHUB_API_KEY=<REPLACE THIS WITH YOUR GITHUB TOKEN>
```

### Fetch openai token
Use [this](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key) tutorial to fetch and set the Open AI API Key
```
export OPEN_AI_API_KEY=<REPLACE THIS WITH YOUR OPENAI API KEY>
```

### (Optional) Setup your Gemini Pro API key
Before you can use the Gemini API, you must first obtain an API key. If you don't already have one, create a key with one click in Google AI Studio.
[Generate API Key](https://makersuite.google.com/app/apikey)

Once you have the API key, Put the key in the GOOGLE_API_KEY environment variable
```
export GOOGLE_API_KEY=<REPLACE THIS WITH YOUR GOOGLE_API_KEY>
```

# How does snoopy works
```
$ python snoopy.py --help
Usage: snoopy.py [OPTIONS]

Options:
  --job-description TEXT       Job description for skill extraction
  --job-description-path FILE  Path to job description file. File Must be txt
                               or pdf file
  --resume TEXT                Resume for skill matching
  --resume-path FILE           Path to resume file. File Must be txt or pdf
                               file
  --assignment-path DIRECTORY  Path to assignment file. File Must be txt or
                               pdf file. It is needed to get the missing
                               skills  [required]
  --github-userid TEXT         GitHub user ID
  --debug                      Enable verbose/debug mode
  --model [Gemini|Chatgpt]     Choose the model: Gemini(to use Gemini Pro) or
                               Chatgpt(to use Chat GPT 3.5 Turbo). [Default:
                               Chatgpt]
  --help                       Show this message and exit.
```

For Example try following command to fetch recommendation using ChatGpt 3.5 turbo:
```
python snoopy.py --job-description-path=test_jd.txt --resume-path=test_resume.txt --assignment-path /Users/vtyagi/Desktop
```

and following command to leverage gemini pro instead
```
python snoopy.py --job-description-path=test_jd.txt --resume-path=test_resume.txt --assignment-path /Users/vtyagi/Desktop --model Gemini
```

While debugging it good to leverage `--debug` flag. It will add additional logging for each step.