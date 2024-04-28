# resume_improvement
Identification of Missing Skills and Generating Recommendations for Resume Improvement based on academic profile using Large Language Model.


# Setup Dev environment
Resume improvement tool snoopy is build using following python version
```
% python --version
Python 3.7.9
```
### Clone Github repo
TBD

### Create a virtual environment
```
python -m venv snoopy
```

### Activate the virtual environment
```
source snoopy/bin/activate
```

### install required python packages
TBD

### 

# How does snoopy works
```
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
