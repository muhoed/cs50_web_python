function getPageLink(el, lmt) {
    const elId = el.id.split("_");
    let scope = elId[0];
    let pageNumber = elId[1];
    if (pageNumber) {
        return `${scope}/${lmt}?page=${pageNumber}`;
    }
    return pageNumber;
}

function addPaginationLinks(obj, links, loader) {
    links.forEach(function(link) {
            let url = getPageLink(link, obj.hasAttribute("limit") ? obj.getAttribute("limit") : 0);
            if (url) {
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    loader(obj, url)
                });
            }
        });
}

export {addPaginationLinks};