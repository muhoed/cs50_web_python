var createProfilePage = {
	
	init: function(settings) {
		createProfilePage.config = {
			deleteForms: $("tr").filter(":contains('Delete:')"),
			emailForms: $(".email-address-form"),
			addressForms: $(".address-form"),
			addEmail: $("#addEmail"),
			addAddress: $("#addAddress"),
			emailTypeSelectors: $("tr:contains('Email type:')"),
			addressTypeSelectors: $("tr:contains('Address type:')")
		};
		$.extend(createProfilePage.config, settings);
		createProfilePage.setup();
	},
	
	setup: function(){
		//set form labels and input fields width
		$("tr").find("td:first-child, th:first-child").addClass("w-50");
		$("input").attr("size", "50");
		//set remove form functionality and display
		createProfilePage.config.deleteForms
			.each(createProfilePage.setRemove)
			.click(createProfilePage.removeForm);
		createProfilePage.config.deleteForms
			.each(createProfilePage.removeForm);
		//delete row should not be displayed for the first address form
		createProfilePage.config.deleteForms
			.filter(":contains('#id_address_set-0-DELETE')")
			.hide();
		//configure add email function
		createProfilePage.config.addEmail
			.click(createProfilePage.addForm(createProfilePage.config.emailForms));
		//configure add address function
		createProfilePage.config.addAddress
			.click(createProfilePage.addForm(createProfilePage.config.addressForms));
		//set initial types
		$(createProfilePage.config.emailForms[0])
			.on("change", function(event){
				createProfilePage.changeSelection(
									event.delegateTarget,
									$(createProfilePage.config.emailForms[0]).find("select"),
									$(createProfilePage.config.emailForms[1]).find("select"),
									createProfilePage.getTypes($(createProfilePage.config.emailForms[0]).find("select"))
									);
								});
		$(createProfilePage.config.addressForms[0])
			.on("change", function(event){
				createProfilePage.changeSelection(
									event.delegateTarget,
									$(createProfilePage.config.addressForms[0]).find("select"),
									$(createProfilePage.config.addressForms[1]).find("select"),
									createProfilePage.getTypes($(createProfilePage.config.addressForms[0]).find("select"))
									);
								});
		//change types when needed
		createProfilePage.config.emailTypeSelectors
			.each(createProfilePage.changeType);
		createProfilePage.config.addressTypeSelectors
			.each(createProfilePage.changeType);
	},
	
	setRemove: function() {
		var item = $(this);
		item.find("label")
			.html("<h4 class='btn btn-primary text-left remove' title='Click to remove form.'>Remove</h4>");
		item.find("input[type='checkbox']")
			.not("#id_address_set-0-DELETE")
			.prop("checked", true)
			.css("visibility", "hidden");
		item.has("#id_address_set-0-DELETE").hide();
	},
	
	removeForm: function() {
		$(this).not("tr:has('#id_address_set-0-DELETE')")
				.each(function(){
					let parentTable = $(this).parent();
					parentTable.hide();
					parentTable.siblings("h4").show();
				});
	},
	
	addForm: function(forms) {
		var deleteForm1 = $(forms[0]).find("input[type='checkbox']");
		var deleteForm2 = $(forms[1]).find("input[type='checkbox']");
		var selectTypeForm1 = $(forms[0]).find("select:first");
		var selectTypeForm2 = $(forms[1]).find("select:first");
		var types = createProfilePage.getTypes(selectTypeForm1);
		if ($(forms[0]).is(":hidden")) {
			$(forms[0]).show();
			deleteForm1.prop("checked", false); //input[type='checkbox']
		} else {
			$(forms[1]).show();
			deleteForm2.prop("checked", false); //input[type='checkbox']
			$(this).hide();
			createProfilePage.changeSelection(
				selectTypeForm1.attr("id"),
				selectTypeForm1,
				selectTypeForm2,
				types
				);
		}
	},
	
	getTypes: function(selector) {
		var types = new Array();
		selector.find("option")
						.each(function(){
							types.push($(this).val());
						});
		return types;
	},
	
	changeSelection: function(trigger, sel1, sel2, types) {
		let option1 = "option[value='" + types[1] + "']";
		let option2 = "option[value='" + types[0] + "']";
		let tmp_sel;
		if (trigger === sel2.get(0)){
			tmp_sel = sel1;
			sel1 = sel2;
			sel2 = tmp_sel;
		}
		if (sel1.val() == types[0]) {
				sel2.find(option1).prop("selected", true);
			} else {
				sel2.find(option2).prop("selected", true);
			};
	},
	
	changeType: function() {
		let selectorForm1 = $(this).find("select:first");
		let selectorForm2 = $(this).parent().siblings("table").find("select:first");
		selectorForm1 //"#id_emailaddress_set-0-email_type, #id_emailaddress_set-1-email_type").
			.on("change", function(event){
				createProfilePage.changeSelection(
							event.delegateTarget,
							selectorForm1,
							selectorForm2,
							createProfilePage.getTypes(selectorForm1)
							);
				});
		}
};
/*
/var addEmail = function() {
/		let form1 = $("#email-address-form-0");
/		let form2 = $("#email-address-form-1");
/		if (form1.is(":hidden")) {
/			form1.show();
/			form1.find("#id_emailaddress_set-0-DELETE").prop("checked", false); //input[type='checkbox']
/		} else {
/			form2.show();
/			form2.find("#id_emailaddress_set-1-DELETE").prop("checked", false); //input[type='checkbox']
/			$(this).hide();
/			changeSelection(
/				"#id_emailaddress_set-0-email_type",
/				$("#id_emailaddress_set-0-email_type"),
/				$("#id_emailaddress_set-1-email_type"),
/				"CT", "PT"
/				);
/		}
/};
/
/var addAddress = function() {
/		let form1 = $("#address-form-0");
/		let form2 = $("#address-form-1");
/		if (form2.is(":hidden")) {
/			form2.show();
/			form2.find("input[type='checkbox']").prop("checked", false);
/			$(this).hide();
/			changeSelection(
/				"#id_address_set-0-address_type",
/				$("#id_address_set-0-address_type"),
/				$("#id_address_set-1-address_type"),
/				"DL", "BL"
/				);
/		}
/};
/
/var changeEmailType = function() {
/	$("#id_emailaddress_set-0-email_type, #id_emailaddress_set-1-email_type").
/			on("change", function(event){changeSelection(
/							event.delegateTarget,
/							$("#id_emailaddress_set-0-email_type"),
/							$("#id_emailaddress_set-1-email_type"),
/							"CT", "PT"
/							);
/				});
/};
/
/var changeAddressType = function() {
/	$("#id_address_set-0-address_type, #id_address_set-1-address_type").
/			on("change", function(event){changeSelection(
/							event.delegateTarget,
/							$("#id_address_set-0-address_type"),
/							$("#id_address_set-1-address_type"),
/							"DL", "BL"
/							);
/				});
/};
/
/var changeSelection = function(trigger, sel1, sel2, val1, val2) {
/	let option1 = "option[value='" + val2 + "']";
/	let option2 = "option[value='" + val1 + "']";
/	let tmp_sel;
/	if (trigger === sel2.get(0)){
/		tmp_sel = sel1;
/		sel1 = sel2;
/		sel2 = tmp_sel;
/	}
/	if (sel1.val() == val1) {
/			sel2.find(option1).prop("selected", true);
/		} else {
/			sel2.find(option2).prop("selected", true);
/		};
/};
*/

$(document).ready(function(){
	let pageTitle = $("title").text();
	switch(pageTitle) {
		case "Auction$ - Create profile":
			//createProfilePage();
			createProfilePage.init();
			break;
		default:
			return false;
	}
});

/*
$(document).ready(function(){
	$("tr").find("td:first-child, th:first-child").addClass("w-50");
	$("input").attr("size", "50");
	let deleteForm = $("tr").filter(":contains('Delete:')");
	deleteForm.find("label")
		.html("<h4 class='btn btn-primary text-left remove' title='Click to remove form.'>Remove</h4>")
		.on("click", function(){
			//let inputId = "#" + $(this).attr("for");
			let parentTable = $(this).parents("table");
			//$("input[type='checkbox']").filter(inputId).prop("checked", true);
			//$(inputId).prop("checked", true);
			parentTable.hide();
			parentTable.siblings("h4").show();
			
		});
	deleteForm.find("input[type='checkbox']")
		.not("#id_address_set-0-DELETE")
		.prop("checked", true)
		.css("visibility", "hidden");
	deleteForm.filter(":contains('#id_address_set-0-DELETE')").hide(); //"#id_address_set-0-DELETE").hide();
});

$(document).ready(function(){
	$("#addEmail").click(function (){
		let form1 = $("#email-address-form-0");
		let form2 = $("#email-address-form-1");
		if (form1.is(":hidden")) {
			form1.show();
			form1.find("#id_emailaddress_set-0-DELETE").prop("checked", false); //input[type='checkbox']
		} else {
			form2.show();
			form2.find("#id_emailaddress_set-1-DELETE").prop("checked", false); //input[type='checkbox']
			$(this).hide();
			changeSelection(
				"#id_emailaddress_set-0-email_type",
				$("#id_emailaddress_set-0-email_type"),
				$("#id_emailaddress_set-1-email_type"),
				"CT", "PT"
				);
		}
	});
});

$(document).ready(function(){
	$("#addAddress").click(function (){
		let form1 = $("#address-form-0");
		let form2 = $("#address-form-1");
		if (form2.is(":hidden")) {
			form2.show();
			form2.find("input[type='checkbox']").prop("checked", false);
			$(this).hide();
			changeSelection(
				"#id_address_set-0-address_type",
				$("#id_address_set-0-address_type"),
				$("#id_address_set-1-address_type"),
				"DL", "BL"
				);
		}
	});
});

$(document).ready(function(){		
	$("#id_emailaddress_set-0-email_type, #id_emailaddress_set-1-email_type").
			on("change", function(event){changeSelection(
							event.delegateTarget,
							$("#id_emailaddress_set-0-email_type"),
							$("#id_emailaddress_set-1-email_type"),
							"CT", "PT"
							);
				});
});

$(document).ready(function(){		
	$("#id_address_set-0-address_type, #id_address_set-1-address_type").
			on("change", function(event){changeSelection(
							event.delegateTarget,
							$("#id_address_set-0-address_type"),
							$("#id_address_set-1-address_type"),
							"DL", "BL"
							);
				});
});
	
function changeSelection(trigger, sel1, sel2, val1, val2){
	let option1 = "option[value='" + val2 + "']";
	let option2 = "option[value='" + val1 + "']";
	let tmp_sel;
	if (trigger === sel2.get(0)){
		tmp_sel = sel1;
		sel1 = sel2;
		sel2 = tmp_sel;
	}
	if (sel1.val() == val1) {
			sel2.find(option1).prop("selected", true);
		} else {
			sel2.find(option2).prop("selected", true);
		};
}
*/
