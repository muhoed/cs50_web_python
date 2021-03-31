function resetForm(formId){
	var check = confirm("All unsaved changes will be lost! Continue?");
	if (check){
		var f = document.forms[formId];
		var i;
		for (i = 0; i < f.length; i++){
			if (f.elements[i].className == "form-control"){
				f.elements[i].value = f.elements[i].defaultValue || "";
			}
		}
	}
}

function cancelForm(){
	var check = confirm("All unsaved changes will be lost! Continue?");
	if (check){
		var title = document.getElementById('id_title').defaultValue;
		title ? location.href = "/article/"+title+"/" : location.href = "/";	
	}
}
