//function sendRequest(targetUrl, onDone) {
//	    $.ajax({
//			    url: targetUrl
//		    }).done(function(json){
//				if (onDone == "reload") {
//					location.reload();
//				} else {
//					window.location.href = json;
//				}
//		    }).fail(function(json){
//				location.reload();
//			});
//};

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
		// set form labels and input fields width
		$("tr").find("td:first-child, th:first-child").addClass("w-50");
		$("input").attr("size", "50");
		// copy disabled select values to hidden fields in update view
		if (profilePage.config.action == "update") {
		    $("#title-value").val(profilePage.config.personalForm.find("select").val());
		    for (var i=0; i<2; i++) {
		        $("#email-type-value-"+i).val(profilePage.config.emailForms.eq(i).find("select").val());
		        $("#address-type-value-"+i).val(profilePage.config.addressForms.eq(i).find("select").eq(0).val());
		        $("#country-value-"+i).val(profilePage.config.addressForms.eq(i).find("select").eq(1).val());
		    }
			// setup edit form buttons in update view
			profilePage.config.editForms
				.on("click", function (event) {
					profilePage.editForm(
						event.delegateTarget
					);
				});
			}
		// setup remove form buttons
		profilePage.config.deleteForms
			.each(function() {
				$(this).find("label")
					.html("<h4 class='btn btn-primary text-left remove' title='Click to remove form.'>Remove</h4>")
					.click(profilePage.removeForm);
			});
		// setup add email form button
		profilePage.config.addEmail
			.on("click", function (event) {
								profilePage.addForm(
										event.delegateTarget,
										profilePage.config.emailForms
									)
					});
		// setup add address form button
		profilePage.config.addAddress
			.on("click", function (event) {
								profilePage.addForm(
										event.delegateTarget,
										profilePage.config.addressForms
									)
					});
		// setup types switch handler
		profilePage.config.emailForms
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
		// setup initial state
		profilePage.setInitialState(profilePage.config.allForms);
	},
	
	removeForm: function() {
			let parentTable = $(this).parents("table");
			parentTable.hide();
			parentTable.siblings("h4").show();
	},
	
	setInitialState: function(forms) {
		// common display settings
		// delete row should not be displayed for the first address form
		//$("tr:contains('#id_address_set-0-DELETE')").hide();
		$("tr").has('#id_address_set-0-DELETE').hide();
		if (profilePage.config.action == "create" && err !== "true") {
		    // display settings for create profile view
			$("input[type='checkbox']")
				.not("#id_address_set-0-DELETE")
				.prop("checked", true)
				.css("visibility", "hidden");
			forms.filter(":not(.full-name-form, #address-form-0)").hide();
			forms.siblings("h4").show();
		} else if (profilePage.config.action == "update" && err !== "true") {
			// display settings for update profile view
			forms.each(function() {
				var self = $(this);
				// hide if form has only empty fields and mark it for deletion
				var formInputs = self.find("input:visible").not("[type='checkbox']");
				var test = false;
				for (var i=0; i<formInputs.length; i++) {
					var value = formInputs.eq(i).prop("value");
					if (value && value != "") {
						test = true;
						break;
					}
				}
				if (!test) {
					self.find("input[type='checkbox']")
						.prop('checked', true);
					self.siblings("h4").show();
					self.hide();
				} else {
					self.siblings("h4").hide();
					self.show();
					self.find("input[type='checkbox']")
						.prop('checked', false)
						.hide();
				}
				// make visible input/select fields readonly/disabled and hide all but edit buttons
				//self.find("label, input:visible").attr("readonly", true);
				//self.find("select").attr("disabled", true);
				profilePage.disableInputs(self);
				$(".btn").filter(":not(span.edit-button, [name='search'])").hide();
			});
		} else {
			// display settings in case of invalid form(-s) on POST
			if (profilePage.config.action === "update") {
				$(".btn").filter("span.edit-button").hide();
				profilePage.disableInputs(profilePage.config.personalForm);
			}
			forms.has("input[type='checkbox']:checked")
				.hide();
			$("input[type='checkbox']").css("visibility", "hidden");
			profilePage.setAddButton(profilePage.config.emailForms);
			profilePage.setAddButton(profilePage.config.addressForms);
		}
	},
	
	disableInputs: function(form) {
		// make visible input/select fields readonly/disabled
		form.find("label, input:visible").attr("readonly", true);
		form.find("select").attr("disabled", true);
	},
	
	editForm: function(trigger) {
		var forms = $(trigger).parent().nextAll("div").eq(0).find("table");
		console.log(forms);
		forms.each(function (i, el) {
			$(el).find("label, input").attr("readonly", false);
			$(el).find("select").attr("disabled", false);
			$(el).not("#address-form-0").find(".btn").not(".edit-button").show();
			$(el).find("input[type='checkbox']").css('visibility', 'hidden');
		});
		profilePage.setAddButton(forms);
		//var addButton = forms.eq(0).siblings("h4");
		//if (forms.eq(0).is(":visible") 
		//			&& forms.eq(1).is(":visible")) {
		//	addButton.hide();
		//} else {
		//	addButton.show();
		//}
		$("input[type='submit']").show();
		$(trigger).hide();
	},
	
	setAddButton: function(forms) {
		var addButton = forms.eq(0).siblings("h4");
		if (forms.eq(0).is(":visible") 
					&& forms.eq(1).is(":visible")) {
			addButton.hide();
		} else {
			addButton.show();
		}
	},
	
	addForm: function(trigger, forms) {
		var deleteForm1 = forms.eq(0).find("input[type='checkbox']");
		var deleteForm2 = forms.eq(1).find("input[type='checkbox']");
		var selectTypeForm1 = forms.eq(0).find("select:first");
		var selectTypeForm2 = forms.eq(1).find("select:first");
		var types = profilePage.getTypes(selectTypeForm1);
		if (forms.eq(0).is(":hidden")) {
			forms.eq(0).find(".errorlist").hide();
			forms.eq(0).show();
			deleteForm1.prop("checked", false);
		} else {
			forms.eq(1).find(".errorlist").hide();
			forms.eq(1).show();
			deleteForm2.prop("checked", false);
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

var credentialsPage = {
	
	init: function(settings) {
		credentialsPage.config = {
			updateButton: $(".update"),
			inputFields: $(".full_name_form").find("input")
		};
		$.extend(credentialsPage.config, settings);
		credentialsPage.setup();
	},
	
	setup: function() {
		credentialsPage.config.inputFields
			.attr("readonly", true);
		credentialsPage.config.updateButton
			.one("click", function(event){
				event.preventDefault();
				credentialsPage.config.updateButton.prop("value", "Update");
				credentialsPage.config.inputFields
					.attr("readonly", false);
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
};

var createListingPage = {
	
	init: function(settings) {
		createListingPage.config = {
			newProduct: $("#create-product"),
			productForm: $(".new-product"),
			productsList: $(".products-list"),
			productListError: $(".product-list-error")
		};
		$.extend(createListingPage.config, settings);
		createListingPage.setup();
	},
	
	setup: function() {
		createListingPage.config.newProduct
			.on("click", function(event){
					createListingPage.createProduct(event);
				});
		//createListingPage.config.productForm.hide();
		createListingPage.boundedProductForm();
		createListingPage.handleProductListErrors();
	},
	
	createProduct: function(trigger) {
		createListingPage.config.productForm.show();
		//createListingPage.config.productForm.each(function(){
		    //$(this).find("input select").attr("disabled", false);
		//});
		createListingPage.config.productForm.find("input[name='name']").prop("disabled", false);
	    createListingPage.config.productForm.find("select").prop("disabled", false);
		createListingPage.config.productsList.find("select").prop('disabled', true); //.hide();
		createListingPage.config.newProduct.hide();
		$(".select-text").hide();
		createOrUpdateProductPage.init();
	},
	
	boundedProductForm: function() {
	    var checkHasValue = false;
	    var productFormInputs = createListingPage.config
												.productForm.find("input, select")
												.not("input[type='checkbox']");
	    productFormInputs.each(function(){
	        if ($(this).prop("value") && $(this).prop("value") != "") {
	            checkHasValue = true;
	        }
	    });
	    if (createListingPage.config.productForm.has(".errorlist").get(0) || checkHasValue) {
	        createListingPage.config.newProduct.click();
	    } else {
	        createListingPage.config.productForm.find("input[name='name']").attr("disabled", true);
	        createListingPage.config.productForm.find("select").prop("disabled", true);
	        createListingPage.config.productForm.hide();
	    }
	},
	
	handleProductListErrors: function() {
		var productListSelect = createListingPage.config.productsList.find("select");
		if (productListSelect.prop("disabled")) {
			createListingPage.config.productListError.hide();
		}
	}
};

var modifyListingPage = {
	
	init: function(settings) {
		modifyListingPage.config = {
			allInput: $("label, input, select, textarea").not("input[placeholder='Search product']"),
			editableInput: $("input, textarea"),
			editButton: $(".edit")
		};
		$.extend(modifyListingPage.config, settings);
		modifyListingPage.setup();
	},
	
	setup: function() {
		modifyListingPage.config.editButton
			.one("click", function(event){
					modifyListingPage.allowModify(event);
				});
		modifyListingPage.config.allInput.attr("readonly", true);
	},
	
	allowModify: function(trigger) {
	    trigger.preventDefault();
		modifyListingPage.config.editableInput.attr("readonly", false);
		modifyListingPage.config.editButton.prop("value", "Save");
	}
};

var createOrUpdateProductPage = {
	
	init: function(settings) {
		createOrUpdateProductPage.config = {
			updatePictures: $(".update-picture"),
			imageUrl: $(".image-url").find("input"),
			removePictures: $(".remove-img"),
			deleteProductBtn: $(".product-delete")
		};
		$.extend(createOrUpdateProductPage.config, settings);
		createOrUpdateProductPage.setup();
	},
	
	setup: function() {
		createOrUpdateProductPage.config.updatePictures
			.on("click", function(event){
					createOrUpdateProductPage.updatePicture(event);
				});
		createOrUpdateProductPage.config.imageUrl.on("change", function(event){
		    createOrUpdateProductPage.reactivatePicture(event);
		});
		createOrUpdateProductPage.config.removePictures.on("click", function(event){
		    createOrUpdateProductPage.removePicture(event);
		});
//		createOrUpdateProductPage.config.deleteProductBtn.on("click", function(event){
//		    createOrUpdateProductPage.deleteProduct(event);
//		});
	},
	
	updatePicture: function(trigger) {
	    let imgId = $(trigger.target).parent().get(0).id;
	    let imgUrlId = "#image-url-" + imgId.split("-")[1];
	    $(trigger.target).attr("src", $(imgUrlId).find("input[type='url']").val());
	},
	
	reactivatePicture: function(trigger){
		let imgUrlId = $(trigger.target).parents(".image-url").get(0).id;
		let num = imgUrlId.split("-")[2];
		let urlId = "#" + imgUrlId
	    let delId = "#id_image_set-" + (num - 1) + "-DELETE";
	    let imgId = "#picture-" + num;
	    $(imgId).find("img").attr("src", $(urlId).find("input[type='url']").val());
	    $(delId).prop("checked", false);
	},
	
	removePicture: function(trigger){
	    let imgId = trigger.target.id.split("-")[2];
	    let imgUrlContainerId = "#image-url-" + imgId;
	    let imgContainerId = "#picture-" + imgId;
	    $(imgContainerId).find("img").attr("src", "");
	    $(imgUrlContainerId).find("input[type='url']").val("");
	    $("#id_image_set-"+(imgId-1)+"-DELETE").prop("checked", true);
	},
	
	deleteProduct: function(trigger) {
	    trigger.preventDefault();
	    let confirmation = confirm("Do you really want to delete the product? The deletion is unrevertable.");
	    if (confirmation) {
	        let pks = trigger.target.id.split("-");
	        let url = "/account/" + pks[1] + "/delete_product/" + pks[3] + "/";
		    sendRequest(url, "url");
	    }
	}
};


var sellingActivitiesPage = {
	
	init: function(settings) {
		sellingActivitiesPage.config = {
			cancelAll: $(".cancel-all"),
			cancelOne: $(".cancel-listing"),
			relistAll: $(".relist-all"),
			relistOne: $(".relist-product"),
			sellOne: $(".sell-product")
		};
		$.extend(sellingActivitiesPage.config, settings);
		sellingActivitiesPage.setup();
	},
	
	setup: function() {
		sellingActivitiesPage.config.cancelAll.on("click", function(event){
					sellingActivitiesPage.cancelAllListings(event);
				});
		sellingActivitiesPage.config.cancelOne.on("click", function(event){
		    sellingActivitiesPage.cancelOneListing(event);
		});
		sellingActivitiesPage.config.relistAll.on("click", function(event){
		    sellingActivitiesPage.relistAllListings(event);
		});
		sellingActivitiesPage.config.relistOne.on("click", function(event){
		    sellingActivitiesPage.relistOneListing(event);
		});
		sellingActivitiesPage.config.sellOne.on("click", function(event){
		    sellingActivitiesPage.sellOneProduct(event);
		});
	},
	
	cancelAllListings: function(trigger) {
		trigger.preventDefault();
	    var confirmation = confirm("All your active listings will be cancelled. Bidders who placed the highest bids up to the moment become winners automatically. Do you want to continue?");
	    if (confirmation) {
	        let user = trigger.target.id.split("-");
	        var url = "/account/" + user[2] + "/cancel_listings/";
		    sellingActivitiesPage.sendRequest(url);
	    }
	},
	
	cancelOneListing: function(trigger) {
		trigger.preventDefault();
		var confirmation = confirm("The listing will be cancelled. Bidder who placed the highest bid up to the moment becomes a winner automatically. Do you want to continue?");
	    if (confirmation) {
	        let pks = trigger.target.id.split("-");
		    var url = "/account/" + pks[1] + "/listing/" + pks[2] + "/cancel/";
		    sellingActivitiesPage.sendRequest(url);
	    }
	},
	
	relistAllListings: function(trigger) {
		trigger.preventDefault();
	    var confirmation = confirm("All your unsold produsts will be relisted. Do you want to continue?");
	    if (confirmation) {
	        let user = trigger.target.id.split("-");
	        var url = "/account/" + user[2] + "/relist_listings/";
		    sellingActivitiesPage.sendRequest(url);
	    }
	},
	
	relistOneListing: function(trigger) {
		trigger.preventDefault();
		var confirmation = confirm("The product will be relisted. Do you want to continue?");
	    if (confirmation) {
	        let pks = trigger.target.id.split("-");
		    var url = "/account/" + pks[1] + "/listing/" + pks[2] + "/relist/";
		    sellingActivitiesPage.sendRequest(url);
	    }
	},
	
	sellOne: function(trigger) {
		trigger.preventDefault();
		var confirmation = confirm("The product will be listed. Do you want to proceed with the listing creation?");
	    if (confirm) {
	        let pks = trigger.target.id.split("-");
		    var url = "/account/" + pks[1] + "/product/" + pks[2] + "/sell/";
		    sellingActivitiesPage.sendRequest(url);
	    } 
	},
	
	sendRequest: function(targetUrl) {
	    $.ajax({
			    url: targetUrl
		    }).done(function(json){
		        location.reload(true);
		    });
	}
};

$(document).ready(function(){
	let pageTitle = $("title").text();
	switch(pageTitle) {
		case "Auction$ - Create profile":
			profilePage.init({'action': 'create'});
			break;
		case "Auction$ - Profile":
			profilePage.init({'action': 'update'});
			break;
		case "Auction$ - Credentials":
			credentialsPage.init();
			break;
		case "Auction$ - Password reset link sent":
			emailLinkPage.init({topic: "pwdreset"});
			break;
		case "Auction$ - Confirm registration":
		        emailLinkPage.init({topic: "regactivation"});
		        break;
		case "Auction$ - Create listing":
		        createListingPage.init();
		        break;
		case "Auction$ - Modify listing":
		        modifyListingPage.init();
		        break;
		case "Auction$ - Create product":
		        createOrUpdateProductPage.init();
		        break;
		case "Auction$ - Modify product":
		        createOrUpdateProductPage.init();
		        break;
		case "Auction$ - Selling activities":
		        sellingActivitiesPage.init();
		        break;
		default:
			return false;
	}
});
