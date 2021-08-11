# Stalkback

> ### Table of Contents
>   1. [About](#about)
>       - [Features](#features)
>       - [Technology Stack](#technology-stack)
>   2. [Running this Project](#running-this-project)
>       - [Requirements](#requirements)
>       - [Setup](#setup)
>       - [Running the app](#running-the-app)
>   3. [Contributors](#contributors)
>   4. [Acknowlegement](#acknowlegement)

## About

On the surface, Stalkback is your typical social media site. However, there's a small, yet significant, difference — Stalkback allows users to categorize their posts and better tailor their feed by stalking only categories they are interested in (think subreddits in Reddit, but for personal content.)

This means you have more control over what you want to see, and as a creator, you no longer need to manage multiple accounts to organize your posts.

### Features

- Create custom categories for your posts.
- Curate your feed by following only content you are interested in.
- Not interested in a friend's posts, but want to avoid the awkwardness of unfollowing them? Unfollow their categories instead while staying on their stalklist!
- Everything you'd expect from your ordinary social media site - follow users, interact with posts, and share your own content.

### Technology Stack

- **Languages:** [Python][1], [JavaScript][2], [HTML][3], [CSS][4]
- **Framework:** [Flask][5]
- **Template engine:** [Jinja][6]
- **Database engine:** [SQLite][7]
- **Libraries:** [SQLAlchemy][8], [Flask-WTF][9], [Flask-Login][10], [Flask-Avatars][11]

## Running this Project

### Requirements

1. Clone this repo!

        git clone https://github.com/Alindah/stalkback.git


2. [conda](https://docs.conda.io/en/latest/miniconda.html) (or your environment manager of choice)

### Setup

1. In your console, change the directory to the root of the project folder.

        cd path/to/project/folder/here

2. Create a virtual environment.

        conda create --name myenv

3. Activate your new environment.

        conda activate myenv

4. Install Stalkback's dependencies.

        conda install --file requirements.txt

### Running the app

1. Run the app.

        python app/main.py

2. By default, Stalkback is set to run on localhost on port 5000. Assuming no conflicts, open your browser and visit http://localhost:5000/.

   - Note: Stalkback is best run on Mozilla Firefox; compatibility is not guaranteed with other browsers.

3. You're all done. Get stalking!

## Contributors

- **Alinda Heng** - [GitHub](https://github.com/Alindah/) | [Website](https://alinda.dev)
- **Jose Valdez** - [GitHub](https://github.com/Finkage)

## Acknowlegement

- [The Flask Mega-Tutorial][12]

[1]: https://www.python.org/
[2]: https://www.javascript.com/
[3]: https://developer.mozilla.org/en-US/docs/Web/HTML
[4]: https://developer.mozilla.org/en-US/docs/Web/CSS
[5]: https://flask.palletsprojects.com/en/2.0.x/
[6]: https://jinja.palletsprojects.com/en/3.0.x/
[7]: https://www.sqlite.org/index.html
[8]: https://www.sqlalchemy.org/
[9]: https://flask-wtf.readthedocs.io/en/0.15.x/
[10]: https://flask-login.readthedocs.io/en/latest/
[11]: https://flask-avatars.readthedocs.io/en/latest/
[12]: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world