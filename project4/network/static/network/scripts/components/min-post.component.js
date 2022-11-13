class MinPost extends HTMLElement {
    constructor() {
        super();

        // prepare a shadow DOM root
        const shadow = this.attachShadow({mode:"open"});
        // css
        const linkElem = document.createElement("link");
        linkElem.setAttribute("rel", "stylesheet");
        linkElem.setAttribute("href", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css");
        shadow.appendChild(linkElem);
        const styleElem = document.createElement("style");
        styleElem.innerText = ` .minimized-post:hover { background-color: lightgrey; cursor: pointer; } `;
        shadow.appendChild(styleElem);
        // create a container for a post
        this.wrapper = document.createElement("div");
        this.wrapper.setAttribute("class", "w-100 mt-2 p-0");
        this.wrapper.setAttribute("id", "post-" + this.getAttribute("post-id"));
        // create a post preview view
        let postPreviewHTML = `<div class="w-100 border m-0 post-preview" id="${this.getAttribute("post-id")}" style="height: 40px; overflow: hidden;">
                                    <div class="minimized-post d-flex nowrap">
                                        <p class="m-2">Posted by <b>${this.getAttribute("post-author") ? this.getAttribute("post-author") + ' ' : "an user "}</b> on ${this.getAttribute("post-date").slice(0,this.getAttribute("post-date").length-12)}</p>
                                    </div>
                                </div>`
        this.wrapper.innerHTML = postPreviewHTML;

        this.wrapper.querySelector(".minimized-post")
            .addEventListener("click", evt => {
                let event = new CustomEvent("comment", {
                    bubbles: true, 
                    composed: true,
                    detail: {"postId": this.getAttribute("post-id")}
                })
                this.wrapper.dispatchEvent(event);
            });
    
        // add a post to the shadow DOM
        shadow.appendChild(this.wrapper);
    }
}

customElements.define("min-post", MinPost);