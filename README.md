# ContriHUB - 22

ContriHUB is an event where we are expecting to get more and more people involved in Open Source activities.


## How to run locally?
* [Install Python](https://www.wikihow.com/Install-Python)
* Clone this repository
    ```
    git clone https://github.com/ContriHUB/ContriHUB-22.git
    ```
* Create Virtual Environment
    ```
    python -m venv <env_name>
    ```
* Activate the environment
    * On Windows, run: `<env_name>\Scripts\activate`
    * On Linux/Mac, run: `source <env_name>/bin/activate`  
    
* Change directory to *ContriHUB-22*
    ```
    cd ContriHUB-22
    ```
* Install the dependencies
    ```
    pip install -r requirements.txt
    ```

* Create a **.env** file
    * In Windows, Right Click, Open Git Bash here, and run: `touch .env`
    * In Linux/Mac, run: `touch .env`
* Fill the contents of **.env** by following the format given in *sample_env_file.txt*
    * You can use [this](https://stackoverflow.com/a/16630719/11671368) to generate **SECRET_KEY**, otherwise just remove that from **.env** file and it should work fine.
    * You will need to create a [Github OAuth App](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app) in order to fill **SOCIAL_AUTH_GITHUB_KEY** and **SOCIAL_AUTH_GITHUB_SECRET** fields.
    * Put both *Homepage URL* and *Authorization callback URL* as `http://127.0.0.1:8000/`.
    * If you want to work on Email Sending Issue, you also need to fill you Email (GMail) in **EMAIL_HOST_USER** and your Email password in **EMAIL_HOST_PASSWORD**. (*Now you know why you should never push .env file to remote*).
    * You will also need to **Allow Access to Less Secure Apps** in your GMail Account.
    * You can also create a new G-Mail account to avoid using your personal account.
* To apply the migrations run,
    ```
    python manage.py migrate
    ```
* Now to run the server, and visit `http://127.0.0.1:8000/`.
    ```
    python manage.py runserver
    ```
* To access admin panel, you need to be superuser. Follow [this](https://www.geeksforgeeks.org/how-to-create-superuser-in-django/) link for instructions.

## Points to keep in mind

* SMTP protocol will not work with proxy. Kindly use mobile data while requesting an assignment/ submitting PR link/ testing out email functionality.
* Every python project will be following some linting rules - Flake8 in this case. Kindly run Flake8 tests before submitting your code.
    To install Flake8, run this command:
    ```
    python<version> -m pip install flake8
    ```
    
    To run Flake8 tests on a file, run this command:
    ```
    flake8 path/to/your_code/main.py #check particular file
    ```
        
    or for an entire repository, run this command:
    ```
    flake8 path/to/your_project/ #check the entire project repo
    ```

# Maintainers

- [Divyansh Upadhyay](https://github.com/DuP-491)
- [Shreya Yadav](https://github.com/hackko-20)

### CAUTION: Website is currently under development.
