"use client";

import { useState } from "react";
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
import { Textarea } from "@/components/ui/textarea";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

const initialForm = {
	material: "",
	passportLookupType: "accession",
	passportLookupValue: "",
	description: "",
	unitPrice: "",
	remarks: "",
};

export default function AddProduct({ onSave = async (_form) => ({ success: false }) }) {
	const [open, setOpen] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [toast, setToast] = useState(null);
	const [form, setForm] = useState(initialForm);

	const showToast = (message, type) => {
		setToast({ message, type });
		setTimeout(() => {
			setToast(null);
		}, 3000);
	};

	const resetForm = () => {
		setForm(initialForm);
	};

	const handleSave = async () => {
		setIsSaving(true);

		if (!form.passportLookupValue.trim()) {
			showToast("Please enter a passport reference value.", "error");
			setIsSaving(false);
			return;
		}

		if (form.unitPrice !== "" && Number(form.unitPrice) < 0) {
			showToast("Unit price cannot be negative.", "error");
			setIsSaving(false);
			return;
		}

		try {
			const payload = {
				material: form.material,
				description: form.description,
				unitPrice: form.unitPrice,
				remarks: form.remarks,
				accessionNumber: "",
				gbNumber: "",
				oldAccessionNumber: "",
			};

			if (form.passportLookupType === "accession") {
				payload.accessionNumber = form.passportLookupValue.trim();
			} else if (form.passportLookupType === "gb") {
				payload.gbNumber = form.passportLookupValue.trim();
			} else {
				payload.oldAccessionNumber = form.passportLookupValue.trim();
			}

			const result = await onSave(payload);
			if (!result?.success) {
				showToast(result?.message || "Failed to add product.", "error");
				return;
			}

			showToast("Product added successfully.", "success");
			setOpen(false);
			resetForm();
		} catch {
			showToast("Unable to connect to the server.", "error");
		} finally {
			setIsSaving(false);
		}
	};

	return (
		<>
			{toast ? (
				<div
					className={`fixed right-4 top-4 z-[100] rounded-md px-4 py-3 text-sm text-white shadow-md ${toast.type === "success" ? "bg-green-600" : "bg-red-600"}`}
				>
					{toast.message}
				</div>
			) : null}

			<Dialog
				open={open}
				onOpenChange={(nextOpen) => {
					setOpen(nextOpen);
					if (!nextOpen) {
						resetForm();
					}
				}}
			>
				<DialogTrigger asChild>
					<Button type="button">Add Product</Button>
				</DialogTrigger>

				<DialogContent className="sm:max-w-lg">
					<DialogHeader>
						<DialogTitle>Add Product</DialogTitle>
						<DialogDescription>Enter product details.</DialogDescription>
					</DialogHeader>

				<div className="space-y-4">
					<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
						<div className="space-y-2">
							<Label>Reference Type</Label>
							<Select
								value={form.passportLookupType}
								onValueChange={(value) => setForm((prev) => ({ ...prev, passportLookupType: value }))}
							>
								<SelectTrigger>
									<SelectValue placeholder="Select reference type" />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="accession">Accession Number</SelectItem>
									<SelectItem value="gb">GB Number</SelectItem>
									<SelectItem value="old-accession">Old Accession Number</SelectItem>
								</SelectContent>
							</Select>
						</div>
						<div className="space-y-2">
							<Label htmlFor="add-passport-reference">Reference Value</Label>
							<Input
								id="add-passport-reference"
								value={form.passportLookupValue}
								onChange={(event) => setForm((prev) => ({ ...prev, passportLookupValue: event.target.value }))}
							/>
						</div>

					<div className="space-y-2">
						<Label htmlFor="add-material">Material</Label>
						<Input
							id="add-material"
							value={form.material}
							onChange={(event) => setForm((prev) => ({ ...prev, material: event.target.value }))}
						/>
					</div>
					</div>

					<div className="space-y-2">
						<Label htmlFor="add-unitPrice">Unit Price</Label>
						<Input
							id="add-unitPrice"
							type="number"
							min="0"
							step="0.01"
							value={form.unitPrice}
							onChange={(event) => setForm((prev) => ({ ...prev, unitPrice: event.target.value }))}
						/>
					</div>

					<div className="space-y-2">
						<Label htmlFor="add-description">Description</Label>
						<Textarea
							id="add-description"
							value={form.description}
							onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
						/>
					</div>

					<div className="space-y-2">
						<Label htmlFor="add-remarks">Remarks</Label>
						<Textarea
							id="add-remarks"
							value={form.remarks}
							onChange={(event) => setForm((prev) => ({ ...prev, remarks: event.target.value }))}
						/>
					</div>

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
		</>
	);
}
