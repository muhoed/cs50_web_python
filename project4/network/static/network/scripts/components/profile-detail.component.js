import {loadProfile, saveProfileInfo, switchFollowingStatus, getFollowCountsByUserId} from "../helpers/profile.service.js";

class ProfileDetail extends HTMLElement {
    constructor() {
        super();
        // prepare shadow DOM shadowRoot
        this.attachShadow({mode:"open"});
        this.rendered = false;
    }

    render() {
        // fill container with data
        this.getProfileDetail().then(result => {
            this.shadowRoot.innerHTML = result;
            this.textField = this.shadowRoot.querySelector("textarea");
            // save copy of initial about info text
            this.aboutText = this.textField.value;
            this.saveButton = this.shadowRoot.querySelector(".save-button");
            this.cancelButton = this.shadowRoot.querySelector(".cancel-button");
            this.followersBadge = this.shadowRoot.querySelector("#followers-count");
            this.followingBadge = this.shadowRoot.querySelector("#following-count");
            this.followButton = this.shadowRoot.querySelector("#follow-btn");
            this.unfollowButton = this.shadowRoot.querySelector("#unfollow-btn");
            this.userList = this.shadowRoot.querySelector("user-list");
            this.textField.addEventListener("input", (event) => this.validateProfileInput());
            this.saveButton.addEventListener("click", (event) => this.saveAboutInfo());
            this.cancelButton.addEventListener("click", (event) => this.cancelAboutInfoChange());
            if (this.shadowRoot.querySelector("#editInfo")) {
                this.shadowRoot.querySelector("#editInfo")
                    .addEventListener("click", (event) => this.editProfileInfo());
            }
            this.shadowRoot.querySelector(".followers")
                .addEventListener("click", (event) => this.getUsersList('followers'));
            this.shadowRoot.querySelector(".following")
                .addEventListener("click", (event) => this.getUsersList('following'));
            if (this.shadowRoot.querySelector(".follow-switcher")) {
                this.shadowRoot.querySelector(".follow-switcher")
                    .addEventListener("click", (event) => this.followSwitcher());
            }
            this.rendered = true;
        });
    }

    connectedCallback() {
        if (!this.rendered) {
            this.render();
        }
    }

    getProfileDetail() {
        return loadProfile(this.getAttribute("user-id"));
    }

    editProfileInfo() {
        this.textField.disabled = false;
        this.toFocus();
        this.saveButton.classList.remove("d-none");
        this.cancelButton.classList.remove("d-none");
    }

    validateProfileInput() {
        this.textField.value.length > 2 ? this.saveButton.classList.remove("disabled") : this.saveButton.classList.add("disabled");
    }

    saveAboutInfo() {
        let id = this.getAttribute("user-id");
        if (!id || this.saveButton.classList.contains("disabled")) {
            this.toFocus();
        } else {
            let text = this.textField.value; 
            if (text !== this.aboutText) {
                let confirm = window.confirm("Do you want to save changes?");
                if (confirm) {
                    let res = saveProfileInfo(text, id);
                    res.then((resolve) => {
                        let parsedResolve = JSON.parse(resolve);
                        this.aboutText = parsedResolve.text;
                        this.exitEditMode();
                        console.log(parsedResolve);
                    },
                    (reject) => {
                        let parsedReject = JSON.parse(reject);
                        this.textField.value = parsedReject.text;
                        console.log(parsedReject.error);
                    });
                } else {
                    this.cancelAboutInfoChange();
                }
            }
        }
    }

    cancelAboutInfoChange() {
        let confirm = window.confirm("Do you want to discard changes?");
        if (confirm) {
            this.exitEditMode();  
        } else {
            this.toFocus();
        }
    }

    toFocus() {
        this.textField.focus;
        this.textField.setActive;
        this.textField.select();
    }

    exitEditMode() {
        this.textField.value = this.aboutText;
        this.textField.disabled = true;
        this.saveButton.classList.add("d-none");
        this.cancelButton.classList.add("d-none");
    }

    getUsersList(type) {
        this.shadowRoot.querySelector("user-list").setAttribute("type", type);
        this.shadowRoot.querySelector(".following").classList.remove('border-bottom', 'border-primary');
        this.shadowRoot.querySelector(".followers").classList.remove('border-bottom', 'border-primary');
        this.shadowRoot.querySelector("." + type).classList.add('border-bottom', 'border-primary');
    }

    followSwitcher() {
        switchFollowingStatus(this.getAttribute("user-id"))
            .then(result => {
                let res = JSON.parse(result);
                this.updateFollow(res.action);
            });
    }

    updateFollow(action) {
        if (action === "follow") {
            this.followButton.classList.add("d-none");
            this.unfollowButton.classList.remove("d-none");
        } else {
            this.unfollowButton.classList.add("d-none");
            this.followButton.classList.remove("d-none");
        }
        getFollowCountsByUserId(this.getAttribute("user-id"))
            .then(res => {
                this.followersBadge.innerText = res.message;
                this.userList.setAttribute("updated", +this.userList.getAttribute("updated")+1);
            });
    }
}

customElements.define("profile-detail", ProfileDetail);