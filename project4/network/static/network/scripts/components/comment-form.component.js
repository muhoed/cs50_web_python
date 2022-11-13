import {createComment} from "../helpers/comments.service.js";

class CommentForm extends HTMLElement {
    constructor() {
        super();

        // prepare a shadow DOM root
        const shadow = this.attachShadow({mode:"open"});
        // css
        const linkElem = document.createElement("link");
        linkElem.setAttribute("rel", "stylesheet");
        linkElem.setAttribute("href", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css");
        shadow.appendChild(linkElem);
        // create a form
        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("class", "w-100 d-flex add-comment m-2");
        let addCommentHTML = `<input class="flex-grow-1" type="text" maxlength="500" placeholder="Type your comment here and press Add." />
                            <button class="btn btn-secondary">Add</button>`
        this.wrapper.innerHTML = addCommentHTML;

        let button = this.wrapper.querySelector("button");
        let textInput = this.wrapper.querySelector("input");
        button.disabled = true;
        textInput.addEventListener("input", (event) => {
                if (textInput.value.length > 0) {
                    button.disabled = false;
                } else {
                    button.disabled = true;
                }
            });
        button.addEventListener("click", (event) => {
            if (textInput.value.length > 0) {
                this.newComment(event, textInput.value);
                textInput.value = "";
                button.disabled = true;
            }
        });
    
        // add a post to the shadow DOM
        shadow.appendChild(this.wrapper);
    }

    newComment(event, text) {
        let res = createComment(this.getAttribute("post-id"), text);
        res.then((resolve) => {
            console.log(resolve.message);
            this.dispatchEvent(new CustomEvent(
                "newcomment",
                {
                    bubbles: true, 
                    composed: true,
                    detail: this.getAttribute("post-id")
                }
            ));
        },
        (reject) => { console.log(reject); })
    }
}

customElements.define("comment-form", CommentForm);