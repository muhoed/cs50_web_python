$(document).ready(function(){
	$("tr").find("td:first-child, th:first-child").addClass("w-50");
	$("input").attr("size", "50");
	let deleteForm = $("tr").filter(":contains('Delete:')");
	deleteForm.find("label")
		.html("<h4 class='btn btn-primary text-left' id='removeForm' title='Click to remove address.'>Remove</h4>")
		.on("click", function(){
			let inputId = "#" + $(this).attr("for");
			let parentTable = $(this).parents("table");
			$("input[type='checkbox']").filter(inputId).prop("checked", true);
			parentTable.hide();
			parentTable.siblings("h4").show();
			
		});
	deleteForm.filter("#address-form-0 tr").hide();
	deleteForm.find("input[type='checkbox']")
		.not("#id_address_set-0-DELETE")
		.prop("checked", true)
		.hide();
});

$(document).ready(function(){
	$("#addEmail").click(function (){
		let form1 = $("#email-address-form-0");
		let form2 = $("#email-address-form-1");
		if (form1.is(":hidden")) {
			form1.show();
			form1.find("input[type='checkbox']").prop("checked", false);
		} else {
			form2.show();
			form2.find("input[type='checkbox']").prop("checked", false);
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

