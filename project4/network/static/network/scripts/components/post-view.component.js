import {loadPost} from "../helpers/posts.service.js";

class PostView extends HTMLElement {

    render() {
        this.getPostWithComments(this.getAttribute("post-id"))
            .then((result) => {
                this.innerHTML = result;
                this.addEventListener("newcomment", () => {
                    let mdf = this.querySelector("comments-list")
                                    .getAttribute("modified");
                    this.querySelector("comments-list")
                        .setAttribute("modified", +mdf + 1);
                    this.querySelector("single-post")
                        .setAttribute("post-commented", "-1");
                });
                })
            .then((res) => {
                this.rendered = true;
            });
    }

    connectedCallback() {
        if (!this.rendered)
        {
            this.render();
        }
    }

    static get observedAttributes() {
        return ["post-id", "state"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (this.rendered)
        {
            // re-render component if new post-id is set or modal window is to be open
            if (
                (name == "post-id" && newValue != "" && oldValue != newValue && this.getAttribute("state") == "open") ||
                (name == "state" && newValue == "open" && oldValue != newValue)
                ) 
            {
                this.render();
            }
        }
    }

    async getPostWithComments(id) {
        return loadPost(id);
    }
}

customElements.define("post-view", PostView);