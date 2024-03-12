// filter_posts.js
console.log('The script is loading correctly.');

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.article-tag-badge').forEach(function(tagBadge) {
        tagBadge.addEventListener('click', function() {
            const selectedTag = this.getAttribute('data-tag');
            document.querySelectorAll('.post').forEach(function(post) {
                const postTags = post.getAttribute('data-tags').split(',');
                if (postTags.includes(selectedTag)) {
                    post.style.display = '';
                } else {
                    post.style.display = 'none';
                }
            });
        });
    });

    document.querySelector('#show-all-posts').addEventListener('click', function() {
        document.querySelectorAll('.post').forEach(function(post) {
            post.style.display = '';
        });
    });
});
