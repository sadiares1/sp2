"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const initialForm = {
	material: "",
	gbNumber: "",
	accessionNumber: "",
	description: "",
	unitPrice: "",
	remarks: "",
};

export default function EditProduct({
	open,
	onOpenChange,
	data,
	onSave = async (_id, _form) => ({ success: false }),
}) {
	const [isSaving, setIsSaving] = useState(false);
	const [saveError, setSaveError] = useState("");
	const [form, setForm] = useState(initialForm);

	useEffect(() => {
		if (open) {
			setForm({
				material: data?.material ?? "",
				gbNumber: data?.gbNumber ?? "",
				accessionNumber: data?.accessionNumber ?? "",
				description: data?.description ?? "",
				unitPrice: data?.unitPrice ?? "",
				remarks: data?.remarks ?? "",
			});
			setSaveError("");
		}
	}, [open, data]);

	const handleSave = async () => {
		if (!data?.id) {
			setSaveError("Product ID is missing.");
			return;
		}

		setIsSaving(true);
		setSaveError("");
		try {
			const result = await onSave(data.id, form);
			if (!result?.success) {
				setSaveError(result?.message || "Failed to update product.");
				return;
			}
			onOpenChange(false);
		} catch {
			setSaveError("Unable to connect to the server.");
		} finally {
			setIsSaving(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-lg">
				<DialogHeader>
					<DialogTitle>Edit Product</DialogTitle>
					<DialogDescription>Update product details.</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="edit-material">Material</Label>
						<Input
							id="edit-material"
							value={form.material}
							onChange={(event) => setForm((prev) => ({ ...prev, material: event.target.value }))}
						/>
					</div>

					<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
						<div className="space-y-2">
							<Label htmlFor="edit-accession">Accession Number</Label>
							<Input
								id="edit-accession"
								value={form.accessionNumber}
								onChange={(event) => setForm((prev) => ({ ...prev, accessionNumber: event.target.value }))}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="edit-gb">GB Number</Label>
							<Input
								id="edit-gb"
								value={form.gbNumber}
								onChange={(event) => setForm((prev) => ({ ...prev, gbNumber: event.target.value }))}
							/>
						</div>
					</div>

					<div className="space-y-2">
						<Label htmlFor="edit-unitPrice">Unit Price</Label>
						<Input
							id="edit-unitPrice"
							type="number"
							step="0.01"
							value={form.unitPrice}
							onChange={(event) => setForm((prev) => ({ ...prev, unitPrice: event.target.value }))}
						/>
					</div>

					<div className="space-y-2">
						<Label htmlFor="edit-description">Description</Label>
						<Textarea
							id="edit-description"
							value={form.description}
							onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
						/>
					</div>

					<div className="space-y-2">
						<Label htmlFor="edit-remarks">Remarks</Label>
						<Textarea
							id="edit-remarks"
							value={form.remarks}
							onChange={(event) => setForm((prev) => ({ ...prev, remarks: event.target.value }))}
						/>
					</div>

					{saveError ? <p className="text-sm text-red-600">{saveError}</p> : null}

					<div className="flex justify-end gap-2">
						<Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSaving}>
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
