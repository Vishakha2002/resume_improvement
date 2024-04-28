# resume_improvement
Identification of Missing Skills and Generating Recommendations for Resume Improvement based on academic profile using Large Language Model.


# Setup Dev environment
Resume improvement tool snoopy is build using following python version
```
$ python --version
Python 3.7.9
```
### Clone Github repo
TBD

### Create a virtual environment
```
$ python -m venv snoopy
```

### Activate the virtual environment
```
$ source snoopy/bin/activate
```

### install required python packages
```
$ pip install -r requirements.txt
```

### Fetch github token

Use [this](https://docs.github.com/en/enterprise-server@3.9/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens) document to fetch your personal github token.

Then set it as environment variable using following command
```
$ export GITHUB_API_KEY=<REPLACE THIS WITH YOUR GITHUB TOKEN>
```

### Fetch openai token
Use [this](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key) tutorial to fetch and set the Open AI API Key 
```
$ export OPEN_AI_API_KEY=<REPLACE THIS WITH YOUR OPENAI API KEY>
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
  --help                       Show this message and exit.
```
