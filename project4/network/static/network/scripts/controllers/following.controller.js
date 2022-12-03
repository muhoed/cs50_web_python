document.addEventListener("DOMContentLoaded", () => {

    // components initialization
    let postList = document.querySelector("post-list[scope='strip']");
    
    // handle postForm component events
    document.querySelector("body")
        .addEventListener("posted", (event) => {
            let state = postList.getAttribute("modified");
            postList.setAttribute("modified", +state + 1);
        });

    // update post list if new comment was added
    document.querySelector("body")
        .addEventListener("newcomment", (event) => {
            // trigger modification of strip post-list
            if (event.detail) {
                postList.setAttribute("commented", event.detail);
            }
        })
});