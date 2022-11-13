import {createPost} from "../helpers/posts.service.js";

// path to component template
const template = "/static/network/views/components/post_form.html"
// link html template and js component class
fetch(template)
    .then(response => response.text())
    .then(text => define(text));

function define(html) {
    class PostForm extends HTMLElement {
        constructor() {
            super();
            // prepare a shadow DOM root
            this.root = this.attachShadow({mode:"open"});
            // fill with html
            this.root.innerHTML = html;
        }

        connectedCallback() {
            // initialize post form
            this.post_form = this.root.querySelector("#post-form");
            this.post_button = this.root.querySelector("#create-post");
            this.post_text = this.root.querySelector("#new-post-text");
            this.error_message = this.root.querySelector("#post-error");

            this.post_button.disabled = true;
            
            this.post_text.addEventListener("input", this.enableButton.bind(this));
            // let self = this;
            this.post_text.addEventListener("keypress", (event) => this.keypressEnter(event));
            this.post_button.addEventListener("click", this.newPost.bind(this));
        }

        disconnectedCallback() {
            this.post_text.removeEventListener("input", this.enableButton);
            //this.post_text.removeEventListener("keypress", this.keypressEnter);
            this.post_button.removeEventListener("click", this.newPost);
        }

        enableButton() {
            if (this.post_text.value.length > 2) {
                this.post_button.disabled = false;
            } else {
                this.post_button.disabled = true;
            }
        }

        keypressEnter(event) {
            if (event.keyCode == 13) {
                event.preventDefault();
                if (this.post_text.value.length > 2 && this.post_text.value.length < 500) {
                    this.newPost();
                }
            }
        }

        newPost() {
            if (this.post_text.value.length && (this.post_text.value.length < 3 || this.post_text.value.length > 500)) {
                this.error_message.innerHTML = this.post_text.validationMessage;
            } else if (!this.post_text.value.length) {
                this.error_message.innerHTML = "Enter some text to post.";
            } else {
                let result = this.addPost()
                result.then(res => {
                    if (res.message) {
                        this.dispatchEvent(new CustomEvent(
                            "posted",
                            {
                                bubbles: true,
                                composed: true,
                                detail: res.message
                            }))
                    } else if (res.error) {
                        this.dispatchEvent(new CustomEvent(
                            "notposted",
                            {
                                bubbles: true,
                                composed: true,
                                detail: res.error
                            }))
                    } else if (res.validationError) {
                        this.error_message.innerHTML = res.validationError;
                    }
                });
                this.post_text.value = "";
            }
        }

        addPost() {
            return createPost(this.post_text)
        }
    }

    customElements.define("post-form", PostForm);
}