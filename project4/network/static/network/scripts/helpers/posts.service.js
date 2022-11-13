async function loadPosts(scope="strip", limit) {
    const url = '/posts/get/' + scope + '/'+ limit;
    let res = await fetch(url)
                    .then(response => response.text());
    return res;
}

async function updatePostList(obj, link) {
    const url = '/posts/get/' + link;
    let res = await fetch(url)
                .then(response => response.text())
                .then(result => {
                    obj.wrapper.innerHTML = result;
                    obj.addPagination();
                    window.location.href = "#";
                });
}

async function createPost(post_text) {
    const new_post = {
        text: post_text.value
    };
    let res = await fetch("/posts/create/", {
                        method: "POST",
                        body: JSON.stringify(new_post)
                    }).then(response => response.json());
    return res;
}

async function markViewed(id) {
    const url = "/posts/viewed/" + id;
    const reqType = {type: "viewed"};
    let res = await fetch(url, {
                        method: "PUT",
                        body: JSON.stringify(reqType)
                    }).then(response => response.text());
    return res;
}

async function postReaction(id, type) {
    const url = `/posts/reaction/${type}/${id}`;
    let res = await fetch(url, {
                    method: "POST"
                }).then(response => response.json())
                .then(result => result.count);
    return res;
}

async function loadPost(id) {
    const url = `/posts/get/${id ? id : 1}`;
    let res = await fetch(url)
                    .then(response => response.text());
    return res;
}

async function savePost(id, text) {
    const url = "/posts/update/" + id;
    const postText = {postText: text};
    return await fetch(url, {
                        method: "PUT",
                        body: JSON.stringify(postText)
                    }).then(response => response.text());
}

export {loadPosts, updatePostList, createPost, markViewed, postReaction, loadPost, savePost};