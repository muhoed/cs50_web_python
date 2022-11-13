async function loadComments(postId) {
    const url = '/comments/' + postId;
    let res = await fetch(url)
                    .then(response => response.text());
    return res;
}

async function updateCommentList(obj, link) {
    let res = await fetch(link)
                .then(response => response.text())
                .then(result => {
                    obj.wrapper.innerHTML = result;
                    obj.addPagination();
                    window.location.href = "#";
                });
}

async function createComment(postId, commentText) {
    let res = await fetch(`/comments/${postId}/create`, {
                        method: "POST",
                        body: JSON.stringify(commentText)
                    }).then(response => response.json());
    return res;
}

export {loadComments, updateCommentList, createComment};