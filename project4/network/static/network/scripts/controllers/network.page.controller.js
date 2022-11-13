document.addEventListener("DOMContentLoaded", () => {

    // components initialization
    let messageContainer = document.querySelector("#message");
    let modal = document.querySelector("modal-popup");
    
    // handle postForm component events
    document.querySelector("body")
        .addEventListener("posted", (event) => {
            messageContainer.style.color = "green";
            messageContainer.innerHTML = event.detail;
            setTimeout(() => {
                messageContainer.innerHTML = "";
            }, 5000);
        });

    document.querySelector("body")
        .addEventListener("notposted", (event) => {
            messageContainer.style.color = "red";
            messageContainer.innerHTML = event.detail;
            setTimeout(() => {
                messageContainer.innerHTML = "";
            }, 5000);
        });

    // open modal window with post and comments on 'comment' event occurs
    document.querySelector("body")
        .addEventListener("comment", (event) => {
            event.currentTarget.classList.add("modal-open");
            modal.setAttribute("post-id", event.detail.postId);
            modal.setAttribute("state", "open");
        });
});