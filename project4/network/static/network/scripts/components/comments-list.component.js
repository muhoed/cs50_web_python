import {loadComments, updateCommentList} from "../helpers/comments.service.js";
import {addPaginationLinks} from "../helpers/pagination.service.js";

class CommentsList extends HTMLElement {
    constructor() {
        super();

        // prepare shadow DOM root
        const shadow = this.attachShadow({mode:"open"});
        // css
        const linkElem = document.createElement("link");
        linkElem.setAttribute("rel", "stylesheet");
        linkElem.setAttribute("href", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css");
        shadow.appendChild(linkElem);
        // create container for post list
        this.wrapper = document.createElement("div");
        if (this.hasAttribute("classes")) {
            this.wrapper.setAttribute("class", this.getAttribute("classes"));
        }
        // fill container with data
        this.loadCommentList().then(result => {
            this.wrapper.innerHTML = result;
            this.addPagination();
            // append posts list to shadow root
            shadow.appendChild(this.wrapper);
        });
    }

    static get observedAttributes() {
        return ["modified"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        // if new post is posted by current user reload strip post list
        if (name == "modified" && newValue != 0 && oldValue !== newValue) {
            this.loadCommentList().then(result => {
                this.wrapper.innerHTML = result;
                this.addPagination();
            });
        }
    }

    loadCommentList() {
        return loadComments(this.getAttribute("post-id"));
    }

    addPagination() {
        // setup pagination
        let paginationLinks = this.wrapper.querySelectorAll("a.page-link");
        addPaginationLinks(
            this, // component instance
            paginationLinks, // HTML elements to add links to
            updateCommentList // callback function
        );
    }
}

customElements.define("comments-list", CommentsList);