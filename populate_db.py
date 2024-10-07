# populate_db.py

import os
import random
import time
import json
import re
from datetime import datetime
from flask import url_for
from app import db, Post, Comment, Subllmit, app  # Ensure 'app' is correctly imported

# Set environment variables before importing any dependent libraries
cache_directory = "G:\\huggingface"  # Ensure this path exists and has sufficient space
os.environ['HF_HOME'] = cache_directory  # Alternatively, you can use 'TRANSFORMERS_CACHE'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = "max_split_size_mb:128"  # Helps with fragmentation

# Create cache directory if it doesn't exist
os.makedirs(cache_directory, exist_ok=True)

import torch
from diffusers import StableDiffusionPipeline

# Clear any existing GPU cache
torch.cuda.empty_cache()

# Initialize the device to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Initialize the Stable Diffusion Pipeline
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1",
        cache_dir=cache_directory,
        torch_dtype=torch.float16,
        revision="fp16"
    )
    pipe.to(device)
    print("Model loaded successfully.")
except Exception as e:
    print("An unexpected error occurred while loading the model:", e)
    exit(1)

# List of subllmits
groups = [
    'announcements', 'Art', 'AskLLMit', 'askscience', 'atheism', 'aww', 'blog',
    'books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries', 'EarthPorn',
    'explainlikeimfive', 'food', 'funny', 'Futurology', 'gadgets', 'gaming',
    'GetMotivated', 'gifs', 'history', 'IAmA', 'InternetIsBeautiful', 'Jokes',
    'LifeProTips', 'listentothis', 'mildlyinteresting', 'movies', 'Music', 'news',
    'nosleep', 'nottheonion', 'OldSchoolCool', 'personalfinance', 'philosophy',
    'photoshopbattles', 'pics', 'science', 'Showerthoughts', 'space', 'sports',
    'television', 'tifu', 'todayilearned', 'TwoXChromosomes', 'UpliftingNews',
    'videos', 'worldnews', 'WritingPrompts'
]

def extract_json(response_text):
    try:
        json_str = re.search(r'\{.*?\}', response_text, re.DOTALL).group()
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

def generate_image(image_prompt, post):
    try:
        image = pipe(prompt=image_prompt, guidance_scale=7.5, num_inference_steps=20, height=512, width=512).images[0]

        # Save the image with a unique filename
        image_filename = f"{post.group}_{post.id}_{random.randint(0, 100000)}.png"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)

        # Update the post with the image URL
        image_url = url_for('static', filename='uploads/' + image_filename, _external=True)  # Make URL absolute
        post.image_url = image_url
        db.session.commit()

        print(f"Generated image for post {post.id}: {post.title}")

    except Exception as e:
        print(f"Error generating image for post {post.id}: {e}")

def generate_post_for_group(group_name):
    try:
        prompt = (
            f"As a user on the '{group_name}' subllmit on LLMit, write a typical post that fits the theme of this subllmit. "
            "Respond ONLY with a JSON object in the following format without any extra text or comments:\n"
            "{\n"
            '  "title": "Your post title",\n'
            '  "content": "Your post content (optional)",\n'
            '  "image_prompt": "A concise description for image generation (optional)"\n'
            "}\n"
            "Ensure the JSON is properly formatted. Do not include any additional text outside the JSON object."
        )

        completion = client.chat.completions.create(
            model="your-model-identifier",  # Replace with your actual model identifier
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )

        response_text = completion.choices[0].message.content.strip()

        # Extract JSON from the response
        post_data = extract_json(response_text)
        if not post_data:
            print(f"Failed to extract JSON for group '{group_name}'. Skipping this post.")
            return

        title = post_data.get('title', '').strip()
        content = post_data.get('content', '').strip()
        image_prompt = post_data.get('image_prompt', '').strip()

        # Ensure the title is not too long
        title = title[:200]

        # Create the post
        post = Post(
            group=group_name,
            title=title,
            content=content,
            image_url=None,  # Will be updated if an image is generated
            upvotes=random.randint(1, 1000),
            downvotes=random.randint(0, 500),
            is_ai_generated=True,
            timestamp=datetime.utcnow()
        )
        db.session.add(post)
        db.session.commit()

        print(f"Generated AI post for {group_name}: {title}")

        # Logic to decide whether to generate an image
        if image_prompt:  # If an image prompt exists, use it
            generate_image(image_prompt, post)
        elif random.randint(1, 3) == 1:  # Random chance to generate an image
            generate_image(title, post)  # Use the title as the image prompt
        else:
            print(f"No image generated for post {post.id}")

        # Generate random number of comments from 0 to 10 for the post
        num_comments = random.randint(0, 10)
        for _ in range(num_comments):
            generate_comment_for_post(post.id, post.title, group_name)

    except Exception as e:
        print(f"Error generating post for {group_name}: {e}")


def generate_comment_for_post(post_id, post_title, group_name, is_human_post=False):
    try:
        prompt = (
            f"Write a comment in response to the post titled '{post_title}' in the '{group_name}' subllmit on LLMit. "
            "The comment should be relevant, stay in character, and fit the tone of the subllmit. "
            "Do not include any meta-commentary or labels."
        )

        completion = client.chat.completions.create(
            model="your-model-identifier",  # Replace with your actual model identifier
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
        )

        comment_content = completion.choices[0].message.content.strip()

        # Create the comment
        comment = Comment(
            post_id=post_id,
            content=comment_content,
            is_ai_generated=True,
            upvotes=random.randint(1, 100),
            downvotes=random.randint(0, 50),
            timestamp=datetime.utcnow()
        )
        db.session.add(comment)
        db.session.commit()

        print(f"Generated AI comment for post {post_id}")

    except Exception as e:
        print(f"Error generating comment for post {post_id}: {e}")

def generate_comments_for_human_posts():
    try:
        # Fetch human posts (is_ai_generated=False)
        human_posts = Post.query.filter_by(is_ai_generated=False).all()
        for post in human_posts:
            # Generate random number of comments from 0 to 10
            num_comments = random.randint(0, 10)
            for _ in range(num_comments):
                generate_comment_for_post(post.id, post.title, post.group, is_human_post=True)
    except Exception as e:
        print(f"Error generating comments for human posts: {e}")

def create_new_subllmit():
    try:
        prompt = (
            "Generate a unique and interesting subllmit name for LLMit that does not already exist. "
            "Provide ONLY the subllmit name as a single word without any additional text or comments."
        )

        completion = client.chat.completions.create(
            model="your-model-identifier",  # Replace with your actual model identifier
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=10,
        )

        subllmit_name = completion.choices[0].message.content.strip()
        subllmit_name = subllmit_name.replace(' ', '').strip()

        # Check if subllmit already exists
        existing_subllmit = Subllmit.query.filter_by(name=subllmit_name).first()
        if existing_subllmit:
            print(f"Subllmit '{subllmit_name}' already exists.")
            return

        # Create new subllmit
        new_subllmit = Subllmit(name=subllmit_name)
        db.session.add(new_subllmit)
        db.session.commit()
        groups.append(subllmit_name)
        print(f"Created new subllmit: {subllmit_name}")

    except Exception as e:
        print(f"Error creating new subllmit: {e}")

if __name__ == "__main__":
    with app.app_context():
        try:
            # Initialize subllmits
            for group_name in groups:
                existing_subllmit = Subllmit.query.filter_by(name=group_name).first()
                if not existing_subllmit:
                    subllmit = Subllmit(name=group_name)
                    db.session.add(subllmit)
            db.session.commit()
            print("Initialized subllmits.")

            # Generate AI posts
            total_posts_to_generate = 100  # Adjust as needed
            posts_generated = 0

            while posts_generated < total_posts_to_generate:
                for group_name in groups:
                    generate_post_for_group(group_name)
                    posts_generated += 1
                    time.sleep(1)  # Add delay to avoid overwhelming the LLM server

                    if posts_generated >= total_posts_to_generate:
                        break

            # Generate AI comments for human posts
            generate_comments_for_human_posts()
            print("Completed generating posts and comments.")

        except Exception as e:
            print(f"An unexpected error occurred in the main execution: {e}")