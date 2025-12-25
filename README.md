# create venv
python -m venv .venv

# activate venv
.venv\Scripts\Activate.ps1
# or
1. ctrl + shift + p
2. Write 'Python Select interpreter'
3. Select .venv

# exit
deactivate

# install with pip
pip install requests huggingface_hub pillow python-dotenv
# or 
pip install -r requirements.txt

# Extend page access token expiration date
https://stackoverflow.com/questions/53510296/never-expiring-facebook-page-access-token

# install deepl for api client
pip install --upgrade deepl