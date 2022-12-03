import {loadUserList} from "../helpers/profile.service.js";
import {addPaginationLinks} from "../helpers/pagination.service.js";

class UserList extends HTMLElement {
    
    constructor() {
        super();
    }

    get id() {
        return this.getAttribute("current-user");
    }

    get type() {
        return this.getAttribute("type");
    }

    get limit() {
        return this.getAttribute("limit");
    }
    
    render() {
        let link = `${this.type}/${this.limit}`;
        let request = loadUserList(this, link);
        request.then((response) => {
            this.innerHTML = response;
            this.addPagination();
            this.rendered = true;
        });
    }

    connectedCallback() {
        if (!this.rendered && this.type) {
            this.render();
        }
    }

    static get observedAttributes() {
        return ["type"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        // if new type of users is selected, show respective list
        if (name == "type" && newValue !== "" && oldValue !== newValue) {
            this.render();
        }
    }

    addPagination() {
        // setup pagination
        let paginationLinks = this.querySelectorAll("a.page-link");
        addPaginationLinks(
            this, // component instance
            paginationLinks, // HTML elements to add links to
            loadUserList // callback function
        );
    }
}

customElements.define("user-list", UserList);