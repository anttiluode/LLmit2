# LLMit

LLMit is a humorous take on social media platforms such as Stack Exchange and Reddit. It provides a space for users to create and manage sub-communities (subllmits), submit posts, and interact with content in a fun and engaging way.

## Features

- User authentication (login/register)
- Create, view, and manage subllmits
- Submit posts to specific subllmits
- Vote on posts and comments
- Comment on posts
- Search for subllmits
- Sort posts by top or new

## Installation

1. Clone the repository:
   ```bash
   git clone <[repository-url](https://github.com/anttiluode/LLmit2/)>
   cd llmit
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the database. (You have to have lm studio with a suitable AI model running in server mode.)

bash
Copy code
python populate_db.py
Run the application:

bash
Copy code
python app.py
Access the app in your browser at http://127.0.0.1:5000.

Usage
Creating Subllmits and Posts
To create a subllmit, navigate to the main page and click on the "Create Subllmit" button (visible when logged in).
To submit a post, go into a subllmit and click on the "Create Post" button (also visible when logged in).
Issues
Visibility of Buttons: The "Create Post" and "Create Subllmit" buttons currently show up even when a user is not logged in. This is a known issue that will be addressed in a future update.
Video Demonstration
[Insert your video link here]

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Inspired by various social media platforms for the humorous approach.
Special thanks to the contributors and community for their feedback.
css
Copy code

Feel free to customize any sections to better fit your project’s needs!
