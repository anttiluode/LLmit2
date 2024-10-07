
# LLMit

LLMit is a social media satire platform inspired by websites like Stack Exchange and Reddit. It allows users to create subllmits and submit posts in a humorous and engaging way. 

## Features
- Create subllmits.
- Submit posts within subllmits.
- Voting on posts and comments.
- Search functionality for subllmits.

## Installation

### Clone the repository:

```bash
git clone https://github.com/anttiluode/LLmit2
```

### Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Initialize the database:

You need to run the following command to set up the database. (Ensure that you have LM Studio with a suitable AI model running in server mode.)

```bash
python initialize_db.py
```

### Run the application:

```bash
python app.py
```

### Access the app in your browser at 

http://127.0.0.1:5000.

## Usage

### Creating Subllmits and Posts
To create a subllmit, navigate to the main page and click on the "Create Subllmit" button (visible when logged in). To submit a post, go into a subllmit and click on the "Create Post" button (also visible when logged in).

## Issues
- **Visibility of Buttons**: The "Create Post" and "Create Subllmit" buttons currently show up even when a user is not logged in. This is a known issue that will be addressed in a future update.

## Image Generation
Images are currently generated using Stable Diffusion.

## Video Demonstration
[Insert your video link here]

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
Inspired by various social media platforms for the humorous approach. Special thanks to the contributors and community for their feedback.
