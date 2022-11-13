import {loadProfile} from "../helpers/profile.service.js";

class ProfileDetail extends HTMLElement {
    constructor() {
        super();

        // prepare shadow DOM root
        this.root = this.attachShadow({mode:"open"});
        // css
        const linkElem = document.createElement("link");
        linkElem.setAttribute("rel", "stylesheet");
        linkElem.setAttribute("href", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css");
        this.root.appendChild(linkElem);
        // create container for post list
        this.wrapper = document.createElement("div");
        // fill container with data
        this.getProfileDetail().then(result => {
            this.root.innerHTML += result;
        });
    }

    getProfileDetail() {
        return loadProfile(this.getAttribute("user-id"));
    }
}

customElements.define("profile-detail", ProfileDetail);