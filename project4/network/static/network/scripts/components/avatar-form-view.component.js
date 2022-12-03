import {loadAvatar, updateAvatar} from "../helpers/profile.service.js";

class AvatarFormView extends HTMLElement {
    
    constructor() {
        super();

        this.id = this.getAttribute("id");
        this.rendered = false;
    }
    
    render(formdata = null) {
        let request = formdata ? updateAvatar(this.id, formdata) : loadAvatar(this.id);
        request.then((response) => {
            this.innerHTML = response;
            if (this.querySelector("#id_avatar")) {
                this.querySelector("#id_avatar")
                            .addEventListener("change", (event) => this.updateAvatar());
            }
            this.rendered = true;
        });
    }

    connectedCallback() {
        if (!this.rendered) {
            this.render();
        }
    }

    updateAvatar() {
        var formdata = new FormData();
        var image = this.querySelector("#id_avatar").files[0];
        formdata.append('avatar', image ); 
        var csrf = this.querySelector('input[name="csrfmiddlewaretoken"]').value;
        formdata.append('csrfmiddlewaretoken', csrf);
        var id = this.querySelector('input[name="id"]').value;
        formdata.append('id', id);
        this.render(formdata);
    }
}

customElements.define("avatar-form-view", AvatarFormView);