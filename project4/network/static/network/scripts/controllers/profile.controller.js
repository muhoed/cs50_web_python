document.addEventListener("DOMContentLoaded", () => {

    // components initialization
    let ownPosts = document.querySelector("post-list[scope='own-posts']");
    
    // handle postForm component events
    if (ownPosts) {
        document.querySelector("body")
            .addEventListener("posted", (event) => {
                let state = ownPosts.getAttribute("modified");
                ownPosts.setAttribute("modified", +state + 1);
            });
    }
});