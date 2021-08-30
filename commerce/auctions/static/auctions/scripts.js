var createProfilePage = {
	
	init: function(settings) {
		createProfilePage.config = {
			deleteForms: $("tr").filter(":contains('Delete:')"),
			emailForms: $(".email-address-form"),
			addressForms: $(".address-form"),
			addEmail: $("#addEmail"),
			addAddress: $("#addAddress"),
			emailTypeSelectors: $("tr:contains('Email type:')").find("select"),
			addressTypeSelectors: $("tr:contains('Address type:')").find("select")
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
			.each(createProfilePage.setRemove);
		createProfilePage.config.deleteForms
			.each(createProfilePage.removeForm);
		//delete row should not be displayed for the first address form
		createProfilePage.config.deleteForms
			.filter(":contains('#id_address_set-0-DELETE')")
			.hide();
		//configure add email function
		createProfilePage.config.addEmail
			.on("click", function (event) {
								createProfilePage.addForm(
										event.delegateTarget,
										createProfilePage.config.emailForms
										)
						});
		//configure add address function
		createProfilePage.config.addAddress
			.on("click", function (event) {
								createProfilePage.addForm(
										event.delegateTarget,
										createProfilePage.config.addressForms
										)
						});
		//set initial types
		createProfilePage.config.emailForms//[0])
			.on("change", function(event){
				createProfilePage.changeSelection(
									event.delegateTarget,
									createProfilePage.config.emailTypeSelectors.eq(0),
									createProfilePage.config.emailTypeSelectors.eq(1),
									createProfilePage.getTypes(createProfilePage.config.emailTypeSelectors.eq(0))
									);
								});
		createProfilePage.config.addressForms//[0])
			.on("change", function(event){
				createProfilePage.changeSelection(
									event.delegateTarget,
									createProfilePage.config.addressTypeSelectors.eq(0),
									createProfilePage.config.addressTypeSelectors.eq(1),
									createProfilePage.getTypes(createProfilePage.config.addressTypeSelectors.eq(0))
									);
								});
	},
	
	setRemove: function() {
		var item = $(this);
		item.find("label")
			.html("<h4 class='btn btn-primary text-left remove' title='Click to remove form.'>Remove</h4>")
			.click(createProfilePage.removeForm);
		item.find("input[type='checkbox']")
			.not("#id_address_set-0-DELETE")
			.prop("checked", true)
			.css("visibility", "hidden");
		item.has("#id_address_set-0-DELETE").hide();
	},
	
	removeForm: function() {
		$(this).not("tr:has('#id_address_set-0-DELETE')")
				.each(function(){
					let parentTable = $(this).parents("table");
					parentTable.hide();
					parentTable.siblings("h4").show();
				});
	},
	
	addForm: function(trigger, forms) {
		var deleteForm1 = forms.eq(0).find("input[type='checkbox']");
		var deleteForm2 = forms.eq(1).find("input[type='checkbox']");
		var selectTypeForm1 = forms.eq(0).find("select:first");
		var selectTypeForm2 = forms.eq(1).find("select:first");
		var types = createProfilePage.getTypes(selectTypeForm1);
		if (forms.eq(0).is(":hidden")) {
			forms.eq(0).show();
			deleteForm1.prop("checked", false);
		} else {
			forms.eq(1).show();
			deleteForm2.prop("checked", false);
			//$(trigger).hide();
			createProfilePage.changeSelection(
				selectTypeForm1.attr("id"),
				selectTypeForm1,
				selectTypeForm2,
				types
				);
		}
		if (!forms.eq(0).is(":hidden") && !forms.eq(1).is(":hidden")) {
			$(trigger).hide();
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
	
	changeType: function(selectors) {
		let selectorForm1 = $(this).find("select:first");
		let selectorForm2 = $(this).parent().siblings("table").find("select:first");
		selectorForm1
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

var passwordResetDonePage = {
	
	init: function(settings) {
		passwordResetDonePage.config = {
			openLink: $("#auth-password-reset-show"),
			messageContainer: $(".auth-password-reset-email")
		};
		$.extend(passwordResetDonePage.config, settings);
		passwordResetDonePage.setup();
	},
	
	setup: function() {
		passwordResetDonePage.config.openLink
			.on("click", passwordResetDonePage.loadMessage());
	},
	
	loadMessage: function() {
		$.ajax({
			url: "/get_email_filenames",
			
		});
	}
}

$(document).ready(function(){
	let pageTitle = $("title").text();
	switch(pageTitle) {
		case "Auction$ - Create profile":
			createProfilePage.init();
			break;
		case "Auction$ - Password reset sent":
			passwordResetDonePage.init();
			break;
		default:
			return false;
	}
});
