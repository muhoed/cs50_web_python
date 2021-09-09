var profilePage = {
	
	init: function(settings) {
		profilePage.config = {
			allForms: $("table"),
			personalForm: $(".full-name-form"),
			deleteForms: $("tr").filter(":contains('Delete:')"),
			editForms: $(".edit-button"),
			emailForms: $(".email-address-form"),
			addressForms: $(".address-form"),
			addEmail: $("#addEmail"),
			addAddress: $("#addAddress"),
			emailTypeSelectors: $("tr:contains('Email type:')").find("select"),
			addressTypeSelectors: $("tr:contains('Address type:')").find("select")
		};
		$.extend(profilePage.config, settings);
		profilePage.setup();
	},
	
	setup: function(){
		//set form labels and input fields width
		$("tr").find("td:first-child, th:first-child").addClass("w-50");
		$("input").attr("size", "50");
		//copy disabled select values to hidden fields
		if (profilePage.config.action == "update") {
		    $("#title-value").val(profilePage.config.personalForm.find("select").val());
		    for (var i=0; i<2; i++) {
		        $("#email-type-value-"+i).val(profilePage.config.emailForms.eq(i).find("select").val());
		        $("#address-type-value-"+i).val(profilePage.config.addressForms.eq(i).find("select").eq(0).val());
		        $("#country-value-"+i).val(profilePage.config.addressForms.eq(i).find("select").eq(1).val());
		    }
		}
		//set remove form functionality
		profilePage.config.deleteForms
			.each(profilePage.setRemove);
		//set initial visibility
		profilePage.config.allForms
			.each(profilePage.setInitialState);
		//delete row should not be displayed for the first address form
		profilePage.config.deleteForms
			.filter(":contains('#id_address_set-0-DELETE')")
			.hide();
		//enable form editing in update view
		profilePage.config.editForms
		    .on("click", function (event) {
				profilePage.editForm(
					event.delegateTarget
				);
			});
		//configure add email function
		profilePage.config.addEmail
			.on("click", function (event) {
								profilePage.addForm(
										event.delegateTarget,
										profilePage.config.emailForms
										)
						});
		//configure add address function
		profilePage.config.addAddress
			.on("click", function (event) {
								profilePage.addForm(
										event.delegateTarget,
										profilePage.config.addressForms
										)
						});
		//set initial types
		profilePage.config.emailForms//[0])
			.on("change", function(event){
				profilePage.changeSelection(
									event.delegateTarget,
									profilePage.config.emailTypeSelectors.eq(0),
									profilePage.config.emailTypeSelectors.eq(1),
									profilePage.getTypes(profilePage.config.emailTypeSelectors.eq(0))
									);
								});
		profilePage.config.addressForms
			.on("change", function(event){
				profilePage.changeSelection(
									event.delegateTarget,
									profilePage.config.addressTypeSelectors.eq(0),
									profilePage.config.addressTypeSelectors.eq(1),
									profilePage.getTypes(profilePage.config.addressTypeSelectors.eq(0))
									);
								});
	},
	
	setRemove: function() {
		var item = $(this);
		item.find("label")
			.html("<h4 class='btn btn-primary text-left remove' title='Click to remove form.'>Remove</h4>")
			.click(profilePage.removeForm);
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
	
	setInitialState: function() {
		$(this).each(function(){
			if (profilePage.config.action === "create") {
				$(this).filter(":not(.full-name-form, #address-form-0)").hide();
				$(this).siblings("h4").show();
			} else {
				//if (!$(this).hasClass("full-name-form")) {
					var formInputs = $(this).find("input:visible")
											.filter(":not(:checkbox)");
					for (var i=0; i < formInputs.length; i++) {
						var parentTable = $(formInputs[i]).parents("table");
						parentTable.siblings("h4").hide();
						var inputValue = $(formInputs[i]).val();
						if (inputValue != null && inputValue != "") {
							parentTable.show();
						} else {
							parentTable.hide();
							parentTable.siblings("h4").show();
						}
					}
				//}
				if ($(this).hasClass("full-name-form" || (!err || err != "true")) {
					$(this).find("label, input:visible").attr("readonly", true);
					$(this).find("select").attr("disabled", true);
					$(".btn").filter(":not(span.edit-button)").hide();
				}
			}
		});
	},
	
	editForm: function(trigger) {
		var form = $(trigger).parent().next()
		form.find("label, input").attr("readonly", false);
		form.find("select").attr("disabled", false);
		form.find(".btn").not(".edit-button").show();
		if (profilePage.config.emailForms.eq(0).is(":visible") 
					&& profilePage.config.emailForms.eq(1).is(":visible")) {
			profilePage.config.addEmail.hide();
		}
		if (profilePage.config.addressForms.eq(0).is(":visible") 
					&& profilePage.config.addressForms.eq(1).is(":visible")) {
			profilePage.config.addAddress.hide();
		}
		$("input[type='submit']").show();
		$(trigger).hide();
	},
	
	addForm: function(trigger, forms) {
		var deleteForm1 = forms.eq(0).find("input[type='checkbox']");
		var deleteForm2 = forms.eq(1).find("input[type='checkbox']");
		var selectTypeForm1 = forms.eq(0).find("select:first");
		var selectTypeForm2 = forms.eq(1).find("select:first");
		var types = profilePage.getTypes(selectTypeForm1);
		if (forms.eq(0).is(":hidden")) {
			forms.eq(0).show();
			deleteForm1.prop("checked", false);
		} else {
			forms.eq(1).show();
			deleteForm2.prop("checked", false);
			//$(trigger).hide();
			profilePage.changeSelection(
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
				profilePage.changeSelection(
							event.delegateTarget,
							selectorForm1,
							selectorForm2,
							profilePage.getTypes(selectorForm1)
							);
				});
		}
};

var emailLinkPage = {
	
	init: function(settings) {
		emailLinkPage.config = {
			openLink: $("#show-message"),
			messageContainer: $("#message-text")
		};
		$.extend(emailLinkPage.config, settings);
		emailLinkPage.setup();
	},
	
	setup: function() {
		emailLinkPage.config.openLink
			.on("click", function(event){
					if(emailLinkPage.config.messageContainer.html() == "") {
						emailLinkPage.loadMessage();
					}
					emailLinkPage.config.messageContainer.get(0).scrollIntoView( {behavior: "smooth" });
				});
	},
	
	loadMessage: function() {
		$.ajax({
			url: "/get_email_filenames",
			data: {
			    uidb64: uid,
			    topic: emailLinkPage.config.topic
			},
			type: "GET",
			dataType: "json",
			cache: false
			
		}).done(function(json){
		    emailLinkPage.config.messageContainer.load(json[0]);
		}).fail(function(xhr, status, error){
		    var message = "<p>Sorry, there was a problem.</p><p>Error: " + error + "</p>";
		    emailLinkPage.config.messageContainer.html(message);
		});
	}
}

$(document).ready(function(){
	let pageTitle = $("title").text();
	switch(pageTitle) {
		case "Auction$ - Create profile":
			profilePage.init({'action': 'create'});
			break;
		case "Auction$ - Profile":
			profilePage.init({'action': 'update'});
			break;
		case "Auction$ - Password reset link sent":
			emailLinkPage.init({topic: "pwdreset"});
			break;
		case "Auction$ - Confirm registration":
		        emailLinkPage.init({topic: "regactivation"});
		        break;
		default:
			return false;
	}
});
