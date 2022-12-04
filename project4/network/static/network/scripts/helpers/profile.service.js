async function loadProfile(id) {
    const url = '/profile/detail/' + id;
    let res = await fetch(url)
                    .then(response => response.text());
    return res;
}

async function saveProfileInfo(text, id) {
    const url = `/profile/detail/${id}/update/about`;
    const aboutText = {aboutText: text};
    return await fetch(url, {
                        method: "PUT",
                        body: JSON.stringify(aboutText)
                    }).then(response => response.text());
}

async function loadAvatar(id) {
    const url = `/profile/detail/${id}/update/avatar`;
    return await fetch(url)
                    .then(response => response.text());
}

async function updateAvatar(id, formdata) {
    const url = `/profile/detail/${id}/update/avatar`;
    return await fetch(url, {
            method: 'POST',
            mode: 'same-origin',  
            headers:{
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest', 
                'X-CSRFToken': formdata.csrfmiddlewaretoken,
                },
            body: formdata 
        }).then(response => response.text());
}

async function loadUserList(obj, link) {
    const url = `/profile/${obj.id}/${link}`;
    return await fetch(url)
                .then(response => response.text());
}

async function switchFollowingStatus(id) {
    const url = `/profile/follow/${id}`;
    return await fetch(url, {
        method: 'PUT'
    }).then(response => response.text());
}

async function getFollowCountsByUserId(id) {
    const url = `/profile/follow/${id}/followers`;
    return await fetch(url).then(response => response.json());
}

export {loadProfile, saveProfileInfo, loadAvatar, updateAvatar, loadUserList, switchFollowingStatus, getFollowCountsByUserId};