"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";

function toInputType(fieldName = "") {
	return fieldName.toLowerCase().includes("date") ? "date" : "text";
}

export default function EditCharacteristic({
	open,
	onOpenChange,
	data,
	onSave,
}) {
	const [formValues, setFormValues] = useState({});
	const [photoFile, setPhotoFile] = useState(null);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState("");

	const fields = useMemo(() => (Array.isArray(data?.fields) ? data.fields : []), [data?.fields]);
	const editableFields = useMemo(
		() => fields.filter((field) => (field?.name || "") !== "photo"),
		[fields]
	);
	const photoField = useMemo(
		() => fields.find((field) => (field?.name || "") === "photo") || null,
		[fields]
	);

	useEffect(() => {
		if (!open) {
			return;
		}

		const nextValues = {};
		fields.forEach((field) => {
			nextValues[field.name] = field.value ?? "";
		});
		setFormValues(nextValues);
		setPhotoFile(null);
		setError("");
	}, [open, fields]);

	const handleSave = async () => {
		if (!data?.id || typeof onSave !== "function") {
			return;
		}

		setIsSaving(true);
		setError("");
		const result = await onSave(data.id, formValues, photoFile);
		setIsSaving(false);

		if (!result?.success) {
			setError(result?.message || "Failed to save changes.");
			return;
		}

		onOpenChange(false);
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-4xl h-[85vh] max-h-[85vh] overflow-hidden p-0 flex flex-col">
				<div className="p-6 pb-0">
					<DialogHeader>
						<DialogTitle>Edit Characteristic</DialogTitle>
						<DialogDescription>
							Update crop-specific characteristic fields.
						</DialogDescription>
					</DialogHeader>
				</div>

				<div className="px-6 pt-4 pb-2 border-b flex justify-end gap-2">
					<Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSaving}>
						Cancel
					</Button>
					<Button type="button" onClick={handleSave} disabled={isSaving}>
						{isSaving ? "Saving..." : "Save"}
					</Button>
				</div>

				<div className="p-6 pt-4 overflow-y-auto space-y-4 flex-1 min-h-0">
					<div className="grid gap-3 md:grid-cols-2">
						<div className="rounded-md border px-3 py-2 text-sm">
							<p className="text-muted-foreground text-xs">Crop</p>
							<p className="font-medium">{data?.crop_name || "-"}</p>
						</div>
						<div className="rounded-md border px-3 py-2 text-sm">
							<p className="text-muted-foreground text-xs">Source Model</p>
							<p className="font-medium">{data?.source_model || "-"}</p>
						</div>
					</div>

					{error ? (
						<div className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
							{error}
						</div>
					) : null}

					<div className="rounded-md border p-4 space-y-3">
						<p className="text-sm font-medium">Characteristic Fields</p>
						{editableFields.length > 0 ? (
							<div className="grid gap-3 md:grid-cols-2">
								{editableFields.map((field, index) => {
									const fieldName = field.name || `field_${index}`;
									return (
										<div key={`${fieldName}-${index}`} className="space-y-1">
											<label className="text-xs text-muted-foreground">{field.label || fieldName}</label>
											<input
												type={toInputType(fieldName)}
												value={formValues[fieldName] ?? ""}
												onChange={(event) =>
													setFormValues((prev) => ({ ...prev, [fieldName]: event.target.value }))
												}
												className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
											/>
										</div>
									);
								})}
							</div>
						) : (
							<p className="text-sm text-muted-foreground">No characteristic fields available.</p>
						)}

						<div className="space-y-1 md:col-span-2">
							<label className="text-xs text-muted-foreground">Photo</label>
							<input
								type="file"
								accept="image/*"
								onChange={(event) => setPhotoFile(event.target.files?.[0] || null)}
								className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
							/>
							<p className="text-xs text-muted-foreground">
								Current: {photoField?.value || "-"}
							</p>
						</div>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
}
