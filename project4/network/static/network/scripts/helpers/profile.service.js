async function loadProfile(id) {
    const url = '/profile/detail/' + id;
    let res = await fetch(url)
                    .then(response => response.text());
    return res;
}

export {loadProfile};