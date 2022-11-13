
// path to component template
const template = "/static/network/views/components/modal_popup.html"
// link html template and js component class
fetch(template)
    .then(response => response.text())
    .then(text => define(text));

function define(html) {
    class ModalPopup extends HTMLElement {
        constructor() {
            super();
            // prepare a shadow DOM root
            this.root = this.attachShadow({mode:"open"});
            // fill with html
            this.root.innerHTML = html;
        }

        static get observedAttributes() {
            return ["post-id", "state"];
        }

        connectedCallback() {
            // select modal container
            this.modal = this.root.querySelector(".modal");
            // add Event listener on close button
            this.root.querySelector("button.close")
                    .addEventListener("click", this.changeState.bind(this));
        }
    
        attributeChangedCallback(name, oldValue, newValue) {
            if (name == "post-id" && newValue !== "") {
                this.root.querySelector("post-view").setAttribute("post-id", newValue);
            }
            if (name == "state" && oldValue && oldValue !== newValue) {
                this.root.querySelector("post-view").setAttribute("state", newValue);
                if (newValue == "open") {  
                    this.openModal(); 
                } else {
                    this.closeModal();
                }
            }
        }

        disconnectedCallback() {
            this.root.querySelector("button.close")
                        .removeEventListener("click", this.changeState);
        }

        changeState() {
            if (this.getAttribute("state") === "open") {
                this.setAttribute("state", "closed");
            }
        }

        openModal() {
            //let md = this.root.querySelector(".modal");
            this.modal.style.display = "block";
            this.modal.style.paddingRight = "17px";
            this.modal.classList.add(["modal", "fade", "show"]);
            this.root.querySelector(".modal-dialog").classList.add("shadow-lg");
        }

        closeModal() {
            this.root.querySelector(".modal-dialog").classList.remove("shadow-lg");
            this.modal.style.display = "none";
            this.modal.classList.remove("show");
            document.querySelector("body").classList.remove("modal-open");
        }
    }

    customElements.define("modal-popup", ModalPopup);
}