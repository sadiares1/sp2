"use client";

import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api";

const initialForm = {
	customerId: "",
	gbNumber: "",
	purpose: "",
	projectTitle: "",
	useOfMaterials: "",
	supplyName: "",
	quantity: "",
	unit: "",
	sourceAcquisitionId: "",
};

function formatAcquisitionLabel(acq) {
	const dateText = acq?.movementDate ? new Date(acq.movementDate).toLocaleDateString() : "No date";
	const quantityText = acq?.quantity ?? "0";
	return `${dateText} - Available: ${quantityText}`;
}

export default function AddRequest({
	onSave = async (_form) => ({ success: false }),
	apiBase,
}) {
	const [open, setOpen] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [isLookupLoading, setIsLookupLoading] = useState(false);
	const [saveError, setSaveError] = useState("");
	const [lookupInfo, setLookupInfo] = useState(null);
	const [customers, setCustomers] = useState([]);
	const [acquisitions, setAcquisitions] = useState([]);
	const [form, setForm] = useState(initialForm);

	const selectedCustomerName = useMemo(() => {
		if (!form.customerId) return "";
		const selected = customers.find((item) => String(item.id) === String(form.customerId));
		return selected?.customerName || "Selected Customer";
	}, [customers, form.customerId]);

	const selectedAcquisitionLabel = useMemo(() => {
		if (!form.sourceAcquisitionId) return "";
		const selected = acquisitions.find((item) => String(item.id) === String(form.sourceAcquisitionId));
		return selected ? formatAcquisitionLabel(selected) : "Selected acquisition";
	}, [acquisitions, form.sourceAcquisitionId]);

	const resetForm = () => {
		setForm(initialForm);
		setSaveError("");
		setLookupInfo(null);
		setAcquisitions([]);
	};

	const loadCustomers = async () => {
		if (!apiBase) return;
		try {
			const response = await apiFetch(`${apiBase}/api/customer/list/?page=1&page_size=100`);
			const data = await response.json();
			if (response.ok && data?.success && Array.isArray(data.customers)) {
				setCustomers(data.customers);
			}
		} catch {
			return;
		}
	};

	const loadAcquisitions = async (productId) => {
		if (!apiBase || !productId) {
			setAcquisitions([]);
			return;
		}

		try {
			const response = await apiFetch(`${apiBase}/api/request/acquisitions/?product_id=${productId}`);
			const data = await response.json();
			if (response.ok && data?.success && Array.isArray(data.acquisitions)) {
				setAcquisitions(data.acquisitions);
				return;
			}
			setAcquisitions([]);
		} catch {
			setAcquisitions([]);
		}
	};

	const handleLookupGb = async () => {
		if (!apiBase) {
			setSaveError("API base URL is not configured.");
			return;
		}

		const passportReference = form.gbNumber.trim();
		if (!passportReference) {
			setSaveError("Passport reference is required.");
			return;
		}

		setIsLookupLoading(true);
		setSaveError("");
		setLookupInfo(null);
		setAcquisitions([]);
		setForm((prev) => ({ ...prev, sourceAcquisitionId: "" }));

		try {
			const encodedReference = encodeURIComponent(passportReference);
			const response = await apiFetch(
				`${apiBase}/api/request/validate-gb/?accession_number=${encodedReference}&gb_number=${encodedReference}&old_accession_number=${encodedReference}&accessionNumber=${encodedReference}&gbNumber=${encodedReference}&oldAccessionNumber=${encodedReference}`
			);
			const data = await response.json();

			if (!response.ok || !data?.success || !data?.data) {
				setSaveError(data?.message || "Unable to validate passport reference.");
				return;
			}

			setLookupInfo(data.data);
			await loadAcquisitions(data.data.product_id);
		} catch {
			setSaveError("Unable to validate passport reference.");
		} finally {
			setIsLookupLoading(false);
		}
	};

	const handleSave = async () => {
		setIsSaving(true);
		setSaveError("");

		if (!form.customerId || !form.gbNumber.trim() || !form.purpose.trim() || !form.useOfMaterials.trim() || !form.supplyName.trim() || !form.quantity || !form.sourceAcquisitionId) {
			setSaveError("Customer, passport reference, Purpose, Use of Materials, Supply Name, Quantity, and Source Acquisition are required.");
			setIsSaving(false);
			return;
		}

		if (Number(form.quantity) <= 0) {
			setSaveError("Quantity must be greater than 0.");
			setIsSaving(false);
			return;
		}

		try {
			const passportReference = form.gbNumber.trim();
			const payload = {
				...form,
				accessionNumber: passportReference,
				gbNumber: passportReference,
				oldAccessionNumber: passportReference,
			};

			const result = await onSave(payload);
			if (!result?.success) {
				setSaveError(result?.message || "Failed to add request.");
				return;
			}

			setOpen(false);
			resetForm();
		} catch {
			setSaveError("Unable to connect to the server.");
		} finally {
			setIsSaving(false);
		}
	};

	return (
		<Dialog
			open={open}
			onOpenChange={(nextOpen) => {
				setOpen(nextOpen);
				if (nextOpen) {
					loadCustomers();
				} else {
					resetForm();
				}
			}}
		>
			<DialogTrigger asChild>
				<Button type="button">Add Request</Button>
			</DialogTrigger>

			<DialogContent className="sm:max-w-2xl">
				<DialogHeader>
					<DialogTitle>Add Request</DialogTitle>
					<DialogDescription>Fill out request details and select source acquisition.</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label>Customer</Label>
						<Select value={form.customerId} onValueChange={(value) => setForm((prev) => ({ ...prev, customerId: value || "" }))}>
							<SelectTrigger>
								<SelectValue>
									{selectedCustomerName || "Select customer"}
								</SelectValue>
							</SelectTrigger>
							<SelectContent>
								{customers.map((customer) => (
									<SelectItem key={customer.id} value={String(customer.id)}>
										{customer.customerName || "Unnamed Customer"}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					<div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto]">
						<div className="space-y-2">
							<Label htmlFor="add-request-gb">Seed Identity</Label>
							<Input
								id="add-request-gb"
								placeholder="Accession / GB / Old accession"
								value={form.gbNumber}
								onChange={(event) => setForm((prev) => ({ ...prev, gbNumber: event.target.value }))}
							/>
						</div>
						<Button type="button" variant="outline" className="self-end" onClick={handleLookupGb} disabled={isLookupLoading}>
							{isLookupLoading ? "Checking..." : "Check"}
						</Button>
					</div>

					{lookupInfo ? (
						<div className="rounded-md border p-3 text-sm">
							<p><span className="font-medium">Crop:</span> {lookupInfo.crop_name || "-"}</p>
							<p><span className="font-medium">Material:</span> {lookupInfo.material_needed || "-"}</p>
							<p><span className="font-medium">Accession:</span> {lookupInfo.accession_number || "-"}</p>
						</div>
					) : null}

					<div className="space-y-2">
						<Label>Source Acquisition</Label>
						<Select value={form.sourceAcquisitionId} onValueChange={(value) => setForm((prev) => ({ ...prev, sourceAcquisitionId: value || "" }))}>
							<SelectTrigger>
								<SelectValue>
									{selectedAcquisitionLabel || "Select source acquisition"}
								</SelectValue>
							</SelectTrigger>
							<SelectContent>
								{acquisitions.map((acq) => (
									<SelectItem key={acq.id} value={String(acq.id)}>
										{formatAcquisitionLabel(acq)}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
						<div className="space-y-2">
							<Label htmlFor="add-request-purpose">Purpose</Label>
							<Input
								id="add-request-purpose"
								value={form.purpose}
								onChange={(event) => setForm((prev) => ({ ...prev, purpose: event.target.value }))}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="add-request-projectTitle">Project Title</Label>
							<Input
								id="add-request-projectTitle"
								value={form.projectTitle}
								onChange={(event) => setForm((prev) => ({ ...prev, projectTitle: event.target.value }))}
							/>
						</div>
					</div>

					<div className="space-y-2">
						<div className="space-y-2">
							<Label htmlFor="add-request-use">Use of Materials</Label>
							<Input
								id="add-request-use"
								value={form.useOfMaterials}
								onChange={(event) => setForm((prev) => ({ ...prev, useOfMaterials: event.target.value }))}
							/>
						</div>
					</div>

					<div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
						<div className="space-y-2 sm:col-span-2">
							<Label htmlFor="add-request-supply">Supply Name</Label>
							<Input
								id="add-request-supply"
								value={form.supplyName}
								onChange={(event) => setForm((prev) => ({ ...prev, supplyName: event.target.value }))}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="add-request-quantity">Quantity</Label>
							<Input
								id="add-request-quantity"
								type="number"
								min="0.01"
								step="0.01"
								value={form.quantity}
								onChange={(event) => setForm((prev) => ({ ...prev, quantity: event.target.value }))}
							/>
						</div>
					</div>

					<div className="space-y-2">
						<Label htmlFor="add-request-unit">Unit</Label>
						<Input
							id="add-request-unit"
							placeholder="Optional (auto-uses source acquisition unit if empty)"
							value={form.unit}
							onChange={(event) => setForm((prev) => ({ ...prev, unit: event.target.value }))}
						/>
					</div>

					{saveError ? <p className="text-sm text-red-600">{saveError}</p> : null}

					<div className="flex justify-end gap-2">
						<Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isSaving}>
							Cancel
						</Button>
						<Button type="button" onClick={handleSave} disabled={isSaving}>
							{isSaving ? "Saving..." : "Save"}
						</Button>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
}
