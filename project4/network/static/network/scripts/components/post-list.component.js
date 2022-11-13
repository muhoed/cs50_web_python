import {loadPosts, updatePostList} from "../helpers/posts.service.js";
import {addPaginationLinks} from "../helpers/pagination.service.js";

class PostList extends HTMLElement {
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
        if (this.hasAttribute("scope")) {
            this.wrapper.setAttribute("id", this.getAttribute("scope"));
        }
        if (this.hasAttribute("classes")) {
            this.wrapper.setAttribute("class", this.getAttribute("classes"));
        }
        // fill container with data
        this.loadPostList().then(result => {
            this.wrapper.innerHTML = result;
            this.addPagination();
            // add event listener to collapse posts
            this.wrapper.addEventListener("post-opened", event => this.collapsePosts(event));
            // append posts list to shadow root
            shadow.appendChild(this.wrapper);
        });
    }

    connectedCallback() {
        if (this.getAttribute("refresh") && this.getAttribute("refresh") > 0)
        {
            // update posts lists every 10 sec
            setInterval(() => this.loadPostList().then(result => this.wrapper.innerHTML = result), this.getAttribute("refresh"));
        }
    }

    static get observedAttributes() {
        return ["modified", "commented"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        // if new post is posted by current user reload strip post list
        if (name == "modified" && newValue != 0 && oldValue !== newValue) {
            this.loadPostList().then(result => {
                this.wrapper.innerHTML = result;
                this.addPagination();
            });
        }
        if (name == "commented" && newValue != "0") {
            let posts = this.wrapper.querySelectorAll("single-post");
            posts.forEach(post => {
                if (post.getAttribute("post-id") == newValue) {
                    post.setAttribute("post-commented", Math.random() * 100);
                }
            });             
        }
    }

    loadPostList() {
        return loadPosts(
            this.hasAttribute("limit") ? this.getAttribute("scope") : undefined,
            this.hasAttribute("limit") ? this.getAttribute("limit") : 0
        );
    }

    addPagination() {
        // setup pagination
        let paginationLinks = this.wrapper.querySelectorAll("a.page-link");
        addPaginationLinks(
            this, // component instance
            paginationLinks, // HTML elements to add links to
            updatePostList // callback function
        );
    }

    collapsePosts(event) {
        this.wrapper.querySelectorAll("single-post")
            .forEach(post => {
                if (post.getAttribute("post-id") != event.detail) {
                    post.setAttribute("minimized", "true");
                }
            })
    }
}

customElements.define("post-list", PostList);