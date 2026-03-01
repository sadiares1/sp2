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

const initialForm = {
	customerName: "",
	designation: "",
	office: "",
	contactInfo: "",
	emailAddress: "",
};

export default function EditCustomer({
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
				customerName: data?.customerName ?? "",
				designation: data?.designation ?? "",
				office: data?.office ?? "",
				contactInfo: data?.contactInfo ?? "",
				emailAddress: data?.emailAddress ?? "",
			});
			setSaveError("");
		}
	}, [open, data]);

	const handleSave = async () => {
		if (!data?.id) {
			setSaveError("Customer ID is missing.");
			return;
		}

		setIsSaving(true);
		setSaveError("");
		try {
			const result = await onSave(data.id, form);
			if (!result?.success) {
				setSaveError(result?.message || "Failed to update customer.");
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
					<DialogTitle>Edit Customer</DialogTitle>
					<DialogDescription>Update customer information.</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="edit-customerName">Name</Label>
						<Input
							id="edit-customerName"
							value={form.customerName}
							onChange={(event) => setForm((prev) => ({ ...prev, customerName: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="edit-designation">Designation</Label>
						<Input
							id="edit-designation"
							value={form.designation}
							onChange={(event) => setForm((prev) => ({ ...prev, designation: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="edit-office">Office</Label>
						<Input
							id="edit-office"
							value={form.office}
							onChange={(event) => setForm((prev) => ({ ...prev, office: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="edit-contactInfo">Contact</Label>
						<Input
							id="edit-contactInfo"
							value={form.contactInfo}
							onChange={(event) => setForm((prev) => ({ ...prev, contactInfo: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="edit-emailAddress">Email</Label>
						<Input
							id="edit-emailAddress"
							type="email"
							value={form.emailAddress}
							onChange={(event) => setForm((prev) => ({ ...prev, emailAddress: event.target.value }))}
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
