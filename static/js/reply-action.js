function showReplyForm(commentId, replyBtn) {
    // Сховати всі коментарі
    document.querySelectorAll('.comment-item, .sub-comment').forEach(function(comment) {
        comment.classList.add('hidden');
    });

    // Показати вибраний коментар і його підкоментарі та додати форму відповіді
    var selectedComment = document.getElementById('comment-' + commentId);
    showCommentWithSubcomments(selectedComment);
    var replyFormContainer = document.getElementById('comment-form-container');
    var replyForm = document.getElementById('comment-form');
    var addCommentTitle = document.getElementById('add-comment-title');
    var cancelReplyBtns = document.querySelectorAll('.cancel-reply');
    var allReplyBtns = document.querySelectorAll('.reply');
    allReplyBtns.forEach(function(btn) {
        btn.style.display = 'inline';
    });
    cancelReplyBtns.forEach(function(btn) {
        btn.style.display = 'none';
    });
    replyBtn.style.display = 'none';
    selectedComment.querySelector('.cancel-reply').style.display = 'inline';
    var subComments = document.getElementById('sub-comments-' + commentId);
    subComments.appendChild(replyFormContainer);
    replyFormContainer.style.display = 'block';
    replyForm.style.display = 'block';
    addCommentTitle.style.display = 'block';
    document.getElementById('parent-id-input').value = commentId;
}

function showCommentWithSubcomments(comment) {
    comment.classList.remove('hidden');
    var subComments = comment.querySelector('.sub-comments');
    if (subComments) {
        subComments.classList.remove('hidden');
        subComments.querySelectorAll('.sub-comment').forEach(function(subComment) {
            showCommentWithSubcomments(subComment);
        });
    }
}

function cancelReply() {
    // Показати всі коментарі та сховати форму відповіді
    document.querySelectorAll('.comment-item, .sub-comment').forEach(function(comment) {
        comment.classList.remove('hidden');
    });

    var replyFormContainer = document.getElementById('comment-form-container');
    var commentsSection = document.getElementById('comments-section');
    var cancelReplyBtns = document.querySelectorAll('.cancel-reply');
    var allReplyBtns = document.querySelectorAll('.reply');
    allReplyBtns.forEach(function(btn) {
        btn.style.display = 'inline';
    });
    cancelReplyBtns.forEach(function(btn) {
        btn.style.display = 'none';
    });
    commentsSection.appendChild(replyFormContainer);
    replyFormContainer.style.display = 'block';
    document.getElementById('parent-id-input').value = '';
}