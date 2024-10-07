document.addEventListener('DOMContentLoaded', () => {
    const postList = document.getElementById('post-list');
    const llmitNavigation = document.getElementById('llmit-navigation');
    const backButton = document.getElementById('back-button');
    const sortTopButton = document.getElementById('sort-top');
    const sortNewButton = document.getElementById('sort-new');
    const searchSubllmitsInput = document.getElementById('search-subllmits');

    const createSubllmitBtn = document.getElementById('create-subllmit-btn');
    const createPostBtn = document.getElementById('create-post-btn');
    const postFormContainer = document.getElementById('post-form-container');
    const postForm = document.getElementById('post-form');

    let currentGroup = null;
    let groups = [];

    // Function to determine if we're on the main page
    function isMainPage() {
        return currentGroup === null || currentGroup === 'frontpage';
    }

    // Show or hide buttons based on the current context (main page or subllmit)
    function updateActionButtons() {
        if (isMainPage()) {
            createSubllmitBtn.style.display = 'block';
            createPostBtn.style.display = 'none';
        } else {
            createSubllmitBtn.style.display = 'none';
            createPostBtn.style.display = 'block';
        }
    }

    // Load default subllmits for navigation
    function loadDefaultSubllmits() {
        fetch('/get_default_subllmits')
            .then(response => response.json())
            .then(data => {
                groups = data;
                llmitNavigation.innerHTML = '';
                groups.forEach(group => {
                    const groupItem = document.createElement('li');
                    groupItem.innerHTML = `<a href="#" data-group="${group}">${group}</a>`;
                    llmitNavigation.appendChild(groupItem);
                });
            })
            .catch(error => console.error('Error loading subllmits:', error));
    }

    // Handle Subllmit creation
    createSubllmitBtn.addEventListener('click', () => {
        window.location.href = '/create_subllmit';
    });

    // Handle Post creation
    createPostBtn.addEventListener('click', () => {
        postFormContainer.style.display = 'block';
    });

    llmitNavigation.addEventListener('click', (event) => {
        if (event.target.tagName === 'A') {
            const group = event.target.getAttribute('data-group');
            loadGroupPosts(group);
        }
    });

    sortTopButton.addEventListener('click', () => {
        loadGroupPosts(currentGroup || 'frontpage', 'top');
    });

    sortNewButton.addEventListener('click', () => {
        loadGroupPosts(currentGroup || 'frontpage', 'new');
    });

    backButton.addEventListener('click', () => {
        backButton.style.display = 'none';
        loadGroupPosts('frontpage');
    });

    searchSubllmitsInput.addEventListener('input', () => {
        const query = searchSubllmitsInput.value;
        fetch(`/search_subllmits?query=${query}`)
            .then(response => response.json())
            .then(subllmits => {
                llmitNavigation.innerHTML = '';
                subllmits.forEach(subllmit => {
                    const groupItem = document.createElement('li');
                    groupItem.innerHTML = `<a href="#" data-group="${subllmit.name}">${subllmit.name}</a>`;
                    llmitNavigation.appendChild(groupItem);
                });
            })
            .catch(error => console.error('Error searching subllmits:', error));
    });

    // Submit post form logic
    postForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(postForm);

        fetch(`/submit_post/${currentGroup}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            postForm.reset();
            postFormContainer.style.display = 'none';
            loadGroupPosts(currentGroup || 'frontpage');  // Reload posts after submission
        })
        .catch(error => console.error('Error submitting post:', error));
    });

    // Load posts for a specific group or the frontpage
    function loadGroupPosts(group, sort = 'top') {
        currentGroup = group;
        updateActionButtons();  // Update buttons based on the group context
        let url = `/get_posts?group=${group}&sort=${sort}`;
        fetch(url)
            .then(response => response.json())
            .then(posts => {
                postList.innerHTML = '';
                if (posts.length === 0) {
                    postList.innerHTML = '<p>No posts available for this group.</p>';
                    return;
                }
                posts.forEach(post => {
                    const postElement = document.createElement('div');
                    postElement.className = 'post';

                    let postContent = `
                        <div class="post-header">
                            <span class="title">${post.title}</span>
                            <span class="group">in ${post.group}</span>
                            <span class="votes">${post.upvotes} upvotes, ${post.downvotes} downvotes</span>
                        </div>
                        <div class="post-body">
                    `;

                    if (post.image_url) {
                        postContent += `<img src="${post.image_url}" alt="Post Image" class="post-image">`;
                    }

                    if (post.content) {
                        postContent += `<p>${post.content}</p>`;
                    }

                    postContent += `
                        </div>
                        <div class="vote-buttons">
                            <button class="upvote-btn" data-post-id="${post.id}">Upvote</button>
                            <button class="downvote-btn" data-post-id="${post.id}">Downvote</button>
                        </div>
                        <button class="load-comments-btn" data-post-id="${post.id}">Comments</button>
                        <div class="comments" id="comments-${post.id}"></div>
                    `;

                    postElement.innerHTML = postContent;
                    postList.appendChild(postElement);
                });
            })
            .catch(error => console.error('Error loading posts:', error));
    }

    // Voting and comment interaction
    postList.addEventListener('click', (event) => {
        if (event.target.classList.contains('upvote-btn')) {
            const postId = event.target.getAttribute('data-post-id');
            votePost(postId, 'upvote');
        }

        if (event.target.classList.contains('downvote-btn')) {
            const postId = event.target.getAttribute('data-post-id');
            votePost(postId, 'downvote');
        }

        if (event.target.classList.contains('load-comments-btn')) {
            const postId = event.target.getAttribute('data-post-id');
            loadComments(postId);
        }
    });

    function votePost(postId, voteType) {
        fetch('/vote_post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                vote_type: voteType
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            loadGroupPosts(currentGroup);  // Reload the posts after voting
        })
        .catch(error => console.error('Error voting on post:', error));
    }

    function loadComments(postId) {
        fetch(`/get_comments?post_id=${postId}`)
            .then(response => response.json())
            .then(comments => {
                const commentsContainer = document.getElementById(`comments-${postId}`);
                commentsContainer.innerHTML = '';
                if (comments.length === 0) {
                    commentsContainer.innerHTML = '<p>No comments yet.</p>';
                    return;
                }
                comments.forEach(comment => {
                    const commentElement = document.createElement('div');
                    commentElement.className = 'comment';
                    commentElement.innerHTML = `
                        <p>${comment.content}</p>
                        <div class="vote-buttons">
                            <button class="upvote-comment-btn" data-comment-id="${comment.id}">Upvote</button>
                            <button class="downvote-comment-btn" data-comment-id="${comment.id}">Downvote</button>
                        </div>
                    `;
                    commentsContainer.appendChild(commentElement);
                });
            })
            .catch(error => console.error('Error loading comments:', error));
    }

    postList.addEventListener('click', (event) => {
        if (event.target.classList.contains('upvote-comment-btn')) {
            const commentId = event.target.getAttribute('data-comment-id');
            voteComment(commentId, 'upvote');
        }

        if (event.target.classList.contains('downvote-comment-btn')) {
            const commentId = event.target.getAttribute('data-comment-id');
            voteComment(commentId, 'downvote');
        }
    });

    function voteComment(commentId, voteType) {
        fetch('/vote_comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comment_id: commentId,
                vote_type: voteType
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            loadGroupPosts(currentGroup);  // Reload the posts after voting on a comment
        })
        .catch(error => console.error('Error voting on comment:', error));
    }

    // Initial load of the main page (frontpage)
    loadGroupPosts('frontpage');
    loadDefaultSubllmits();
});
