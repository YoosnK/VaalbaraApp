const PREFIX = "items";

function updateExportLimits() {
	const typeField = document.querySelector('[name="transaction_type"]');
	if (!typeField) return;

	const type = typeField.value;
	const rows = document.querySelectorAll(".item-row");

	rows.forEach((row) => {
		const itemSelect = row.querySelector("select");
		const qtyInput = row.querySelector('input[type="number"]');

		if (itemSelect && qtyInput) {
			if (type === "Export") {
				const available = parseFloat(window.stockData[itemSelect.value] || 0);
				qtyInput.max = available;
				qtyInput.step = "0.001"; // Allow decimals
				qtyInput.placeholder = "Max: " + available;
			} else {
				qtyInput.removeAttribute("max");
				qtyInput.placeholder = "";
			}
		}
	});
}

function updateDiscountFields() {
	const typeField = document.querySelector('[name="transaction_type"]');
	if (!typeField) return;

	const isImport = typeField.value === "Import";
	const rows = document.querySelectorAll(".item-row");

	rows.forEach((row) => {
		const discountField = row.querySelector('[id$="-discount"]');
		if (!discountField) return;

		if (isImport) {
			discountField.value = "0.00";
			discountField.readOnly = true;
			discountField.style.opacity = "0.5";
			discountField.style.pointerEvents = "none";
		} else {
			discountField.readOnly = false;
			discountField.style.opacity = "1";
			discountField.style.pointerEvents = "auto";
		}
	});

	console.log(
		"Discount fields updated. Mode:",
		isImport ? "ReadOnly" : "Editable"
	);
}

function updatePartnerFields() {
	const partnerSelect = document.getElementById("partner_select");
	if (!partnerSelect) return;

	// Helper fields we want to toggle
	const newPartnerFieldNames = [
		"new_partner_name",
		"new_partner_tax_code",
		"new_partner_phone",
		"new_partner_email",
		"new_partner_address",
		"new_partner_contact_person",
	];

	const isNewPartner = !partnerSelect.value;

	newPartnerFieldNames.forEach((name) => {
		const input = document.querySelector(`[name="${name}"]`);
		if (input) {
			// Find the container (usually the div or p tag rendered by {{ form }})
			const container = input.closest("div") || input.parentElement;
			container.style.display = isNewPartner ? "grid" : "none";
		}
	});
}

document.getElementById("add-item-btn").addEventListener("click", function (e) {
	const totalForms = document.getElementById(`id_${PREFIX}-TOTAL_FORMS`);
	if (!totalForms) {
		console.error(
			"Management form 'TOTAL_FORMS' not found. Check your prefix."
		);
		return;
	}

	const formIdx = parseInt(totalForms.value);
	const template = document.getElementById("empty-form-template").innerHTML;

	const newRowHtml = template.replace(/__prefix__/g, formIdx);
	const itemList = document.getElementById("item-list");

	const wrapper = document.createElement("div");
	wrapper.innerHTML = newRowHtml;
	itemList.appendChild(wrapper.firstElementChild);

	totalForms.value = formIdx + 1;
});

function debounce(func, delay) {
	let timeoutId;
	return function (...args) {
		if (timeoutId) clearTimeout(timeoutId);
		timeoutId = setTimeout(() => {
			func.apply(this, args);
		}, delay);
	};
}

function updateGrandTotal() {
	const grandTotalElement = document.querySelector(".grand-total");
	if (!grandTotalElement) return;

	let totalSum = 0;

	document.querySelectorAll(".total-cell").forEach((cell) => {
		const value = parseFloat(cell.textContent.replace(/,/g, "")) || 0;
		console.log("cell value", value);
		totalSum += value;
	});

	grandTotalElement.textContent = totalSum.toLocaleString("en-US", {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	});
}

function calculateRowTotal(row) {
	const qtyInput = row.querySelector('input[id*="-quantity"]');
	const costInput = row.querySelector('input[id*="-unit_cost"]');
	const discountInput = row.querySelector('input[id*="-discount"]');

	const totalCell = row.querySelector(".total-cell");

	if (qtyInput && costInput && discountInput && totalCell) {
		const qty = parseFloat(qtyInput.value) || 0;
		const cost = parseFloat(costInput.value) || 0;
		const discount = parseFloat(discountInput.value) || 0;

		const finalCost = cost * qty * (1 - discount / 100);

		totalCell.textContent = finalCost.toLocaleString("en-US", {
			minimumFractionDigits: 0,
			maximumFractionDigits: 2,
		});
		totalCell.style.opacity = "1";
		updateGrandTotal();
	}
}

const debouncedCalc = debounce((row) => calculateRowTotal(row), 500);

document.addEventListener("input", function (e) {
	const target = e.target;

	if (
		target.id.includes("-quantity") ||
		target.id.includes("-unit_cost") ||
		target.id.includes("-discount")
	) {
		const row = target.closest(".item-row");
		if (row) {
			const totalCell = row.querySelector(".total-cell");
			if (totalCell) totalCell.style.opacity = "0.5";
			debouncedCalc(row);
		}
	}
});

document.addEventListener("change", function (e) {
	const target = e.target;

	if (e.target.id === "partner_select") {
		updatePartnerFields();
	}

	if (target.name.includes("-DELETE")) {
		const row = target.closest(".item-row");
		const totalCell = row.querySelector(".total-cell");

		if (target.checked) {
			totalCell.dataset.oldValue = totalCell.textContent;
			totalCell.textContent = "0.00";
		} else {
			totalCell.textContent = totalCell.dataset.oldValue || "0.00";
		}
		updateGrandTotal();
	}

	if (target.tagName === "SELECT" || target.name === "transaction_type") {
		updateExportLimits();
		updateDiscountFields();
	}
});

document.addEventListener("DOMContentLoaded", () => {
	updatePartnerFields();
	updateDiscountFields();
	document.querySelectorAll(".item-row").forEach((row) => {
		calculateRowTotal(row);
	});
	updateGrandTotal();
});
