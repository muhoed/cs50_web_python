import {markViewed, postReaction, savePost} from "../helpers/posts.service.js";

class SinglePost extends HTMLElement {
    constructor() {
        super();

        // initial post text
        this.postText = this.getAttribute("post-text");

        // prepare a shadow DOM root
        const shadow = this.attachShadow({mode:"open"});

        // css
        const linkElem = document.createElement("link");
        linkElem.setAttribute("rel", "stylesheet");
        linkElem.setAttribute("href", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css");
        shadow.appendChild(linkElem);

        const linkElem1 = document.createElement("link");
        linkElem1.setAttribute("rel", "stylesheet");
        linkElem1.setAttribute("href", "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css");
        shadow.appendChild(linkElem1);

        // view type specific css
        const styleElem = document.createElement("style");
        if (this.getAttribute("post-view") == "full")
        {
            styleElem.innerText = ".post-comments:hover, .post-like:hover, .post-dislike:hover { cursor: pointer; }";
        }
        else if (this.getAttribute("post-view") == "short")
        {
            styleElem.innerText = ".comment-sign:hover, .like-sign:hover, .dislike-sign:hover { cursor: pointer; }";
        }
        else
        {
            styleElem.innerText = ` .post-full { transition: height 0.5s; }
                                    .short-post-block:hover { background-color: lightgrey; cursor: pointer; }
                                    .post-full .post-header:hover { cursor: pointer; } 
                                    .post-comments:hover, .post-like:hover, .post-dislike:hover { cursor: pointer; } `;
        }
        shadow.appendChild(styleElem);

        // create a container for a post
        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("class", "w-100 mt-2 p-0");
        this.wrapper.setAttribute("id", "post-" + this.getAttribute("post-id"));

        if (this.getAttribute("post-view") == "short" || this.getAttribute("post-view") == "collapsed")
        {
            // create a post preview view
            let postPreviewHTML = `<div class="w-100 border m-0 post-preview" id="post-preview-${this.getAttribute('post-id')}" style="height: ${this.getAttribute('post-minimized') == 'true' ? '40px' : '0' }; overflow: hidden;">
                    <div class="short-post-block d-flex nowrap" title="View post">
                        <p class="flex-grow-1 m-2"><b>${this.getAttribute('post-date').slice(0,this.getAttribute('post-date').length-12)}
                        ${this.getAttribute('post-author') ? 'by ' + this.getAttribute('post-author') + ':' : ""} </b>
                        ${this.getAttribute('post-text-short')}</p>
                        <p class="comment-sign mt-2 mb-2 mr-4" ${this.getAttribute('post-view') == 'short' ? 'title="Add / view comments"' : ''}><i class="bi bi-chat-text"></i> ${this.getAttribute('post-comments-num') ? this.getAttribute('post-comments-num') : 0}</p>
                        <p class="like-sign m-2" ${this.getAttribute('post-view') == 'short' ? 'title="Add like"' : ''}><i class="bi bi-hand-thumbs-up"></i><span>${this.getAttribute('post-likes-num') ? this.getAttribute('post-likes-num') : 0}</span></p>
                        <p class="dislike-sign m-2" ${this.getAttribute('post-view') == 'short' ? 'title="Add dislike"' : ''}><i class="bi bi-hand-thumbs-down"></i><span>${this.getAttribute('post-dislikes-num') ? this.getAttribute('post-dislikes-num') : 0}</span></p>
                    </div>
                </div>`;
            this.wrapper.innerHTML = postPreviewHTML;

            if (this.getAttribute("post-view") == "short")
            {
                this.wrapper.querySelector(".like-sign")
                    .addEventListener("click", (event) => this.addReaction(event.currentTarget, "like"));
                this.wrapper.querySelector(".dislike-sign")
                    .addEventListener("click", (event) => this.addReaction(event.currentTarget, "dislike"));
                
                this.wrapper.querySelector(".comment-sign")
                    .addEventListener("click", (event) => this.viewPostComments(event.currentTarget));
            }
        }
        if (this.getAttribute("post-view") == "full" || this.getAttribute("post-view") == "collapsed")
        {
            // create a post full view
            let postHTML = `<div class="w-100 border m-0 post-full" id="post-full-${this.getAttribute('post-id')}" style="height: ${this.getAttribute('post-minimized') == 'true' ? '0' : '154px'}; overflow: hidden;">
                                <div class="post-header d-flex nowrap border-bottom-2 bg-light"${this.getAttribute('post-view') == 'collapsed' ? ' title="Collapse"' : ''}>
                                    <div class="post-author flex-grow-1 align-self-start m-2">
                                        Posted by: ${this.getAttribute('post-author') ? this.getAttribute('post-author') : ''}
                                    </div>
                                    <div class="post-date align-self-end m-2">
                                        On: ${this.getAttribute('post-date')}
                                    </div>
                                </div>
                                <textarea class="post-text w-100 p-2 bg-white" row="1" maxlength="500" disabled>${this.getAttribute('post-text')}</textarea>
                                <div class="post-footer d-flex nowrap border-top-2 bg-light">
                                    <div title="${this.getAttribute('post-comment-open') == 'enabled' ? 'View / add comments' : ''}" class="post-comments align-self-start flex-grow-1 m-2">Comments: ${this.getAttribute('post-comments-num') ? this.getAttribute('post-comments-num') : 0}</div>
                                    ${this.getAttribute('post-own') == 'true' ? '<div class="post-edit m-2"><i class="bi bi-pencil-square" title="Edit post"></i></div>' : ''}
                                    <div class="post-like m-2" title="Add like">Like <span class="likes-count">${this.getAttribute('post-likes-num') ? this.getAttribute('post-likes-num') : 0}</span></div>
                                    <div class="post-dislike m-2" title="Add dislike">Dislike <span class="dislikes-count">${this.getAttribute('post-dislikes-num') ? this.getAttribute('post-dislikes-num') : 0}</span></div>
                                </div>
                            </div>`;
            this.wrapper.innerHTML += postHTML;
            
            if (this.getAttribute("post-view") == "collapsed")
            {
                this.preview = this.wrapper.querySelector(".short-post-block");
                this.preview.addEventListener("click", (event) => this.openFullPost(event));
                this.full = this.wrapper.querySelector(".post-full .post-header");
                this.full.addEventListener("click", (event) => this.closeFullPost(event));
            }

            this.wrapper.querySelector(".post-like")
                .addEventListener("click", (event) => this.addReaction(event.currentTarget, "like"));
            this.wrapper.querySelector(".post-dislike")
                .addEventListener("click", (event) => this.addReaction(event.currentTarget, "dislike"));
            
            if (this.getAttribute("post-comment-open") == "enabled"){
                this.wrapper.querySelector(".post-comments")
                    .addEventListener("click", (event) => this.viewPostComments(event.currentTarget));
            }

            if (this.getAttribute("post-own") == "true") {
                let editButton = this.wrapper.querySelector(".post-edit");
                editButton.style.cursor = "pointer";
                editButton.addEventListener("click", (event) => this.editPost(event));
            }
        }
    
        // add a post to the shadow DOM
        shadow.appendChild(this.wrapper);
    }

    static get observedAttributes() {
        return ["minimized", "post-commented"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name == "minimized" && newValue != oldValue && newValue == "true")
        {
            // minimize post
            this.full.firstChild.dispatchEvent(new MouseEvent("click", {bubbles: true}));
        }
        if (name == "post-commented" && oldValue && newValue != oldValue && newValue != "-1") {
            // increase number of comments
            let comNum = this.getAttribute("post-comments-num");
            this.setAttribute("post-comments-num", +comNum + 1);
            if (this.wrapper.querySelector(".comment-sign")) {
                this.wrapper.querySelector(".comment-sign").innerHTML = `<i class="bi bi-chat-text"></i> ${this.getAttribute('post-comments-num')}`;
            }
            if (this.wrapper.querySelector(".post-comments")) {
                this.wrapper.querySelector(".post-comments").innerText = `Comments: ${this.getAttribute('post-comments-num')}`;
            }
        } else if (name == "post-commented" && newValue != oldValue && newValue == "-1") {
            if (this.wrapper.querySelector(".post-comments")) {
                this.wrapper.querySelector(".post-comments").innerText = `Comments: ${+this.getAttribute('post-comments-num') + 1}`;
            }
        }
    }

    openFullPost(event) {
        this.full.parentNode.style.height = "154px";
        event.currentTarget.parentNode.style.height = 0;
        
        this.setAttribute("minimized", "false");
        let viewed = markViewed(this.getAttribute("post-id"));
        viewed.then(function(resolve) {
            console.log(resolve);
        });
        
        this.full.dispatchEvent(new CustomEvent(
            "post-opened",
            {
                bubbles: true,
                composed: true,
                detail: this.getAttribute("post-id")
            }
        ));
    }

    closeFullPost(event) {
        event.currentTarget.parentNode.style.height = 0;
        setTimeout(() => {this.preview.parentNode.style.height = "40px";}, 500);
        this.setAttribute("minimized", "true");
    }

    addReaction(el, type) {
        let self = this;
        let likes = postReaction(self.getAttribute("post-id"), type);
        likes.then(function(res) {
            self.setAttribute(`post-${type}s-num`, res);
            if (self.getAttribute("post-view") === "collapsed" || self.getAttribute("post-view") === "full")
            {
                self.wrapper.querySelector(`.${type}s-count`).innerText = res;
            }
            if (self.getAttribute("post-view") === "collapsed" || self.getAttribute("post-view") === "short")
            {
                self.wrapper.querySelector(`.${type}-sign span`).innerText = res;
            }
        });
    }

    viewPostComments(el) {
        let event = new CustomEvent("comment", {
            bubbles: true, 
            composed: true,
            detail: {"postId": this.getAttribute("post-id")}
        })
        el.dispatchEvent(event);
    }

    editPost(event) {
        let editArea = this.wrapper.querySelector(".post-text");
        editArea.disabled = false;
        editArea.focus();
        editArea.addEventListener("blur", (event) => {
            this.updatePost(event.currentTarget);
            event.currentTarget.disabled = true;
        });
    }

    updatePost(editArea) {
        if (this.postText !== editArea.value) {
            let confirm = window.confirm("Do you want to save changes?");
            if (confirm) {
                let res = savePost(this.getAttribute("post-id"), editArea.value);
                res.then((resolve) => {
                    let parsedResolve = JSON.parse(resolve);
                    this.postText = parsedResolve.text;
                    console.log(parsedResolve);
                },
                (reject) => {
                    let parsedReject = JSON.parse(reject);
                    editArea.value = parsedReject.text;
                    console.log(parsedReject.error);
                });
            } else {
                editArea.value = this.postText;
            }
        }
    }
}

customElements.define("single-post", SinglePost);