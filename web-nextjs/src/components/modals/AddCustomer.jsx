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

const initialForm = {
	customerName: "",
	designation: "",
	office: "",
	contactInfo: "",
	emailAddress: "",
};

export default function AddCustomer({ onSave = async (_form) => ({ success: false }) }) {
	const [open, setOpen] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [saveError, setSaveError] = useState("");
	const [form, setForm] = useState(initialForm);

	const resetForm = () => {
		setForm(initialForm);
		setSaveError("");
	};

	const handleSave = async () => {
		setIsSaving(true);
		setSaveError("");

		try {
			const result = await onSave(form);
			if (!result?.success) {
				setSaveError(result?.message || "Failed to add customer.");
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
				if (!nextOpen) {
					resetForm();
				}
			}}
		>
			<DialogTrigger asChild>
				<Button type="button">Add Customer</Button>
			</DialogTrigger>

			<DialogContent className="sm:max-w-lg">
				<DialogHeader>
					<DialogTitle>Add Customer</DialogTitle>
					<DialogDescription>Fill in customer information.</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="add-customerName">Name</Label>
						<Input
							id="add-customerName"
							value={form.customerName}
							onChange={(event) => setForm((prev) => ({ ...prev, customerName: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="add-designation">Designation</Label>
						<Input
							id="add-designation"
							value={form.designation}
							onChange={(event) => setForm((prev) => ({ ...prev, designation: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="add-office">Office</Label>
						<Input
							id="add-office"
							value={form.office}
							onChange={(event) => setForm((prev) => ({ ...prev, office: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="add-contactInfo">Contact</Label>
						<Input
							id="add-contactInfo"
							value={form.contactInfo}
							onChange={(event) => setForm((prev) => ({ ...prev, contactInfo: event.target.value }))}
						/>
					</div>
					<div className="space-y-2">
						<Label htmlFor="add-emailAddress">Email</Label>
						<Input
							id="add-emailAddress"
							type="email"
							value={form.emailAddress}
							onChange={(event) => setForm((prev) => ({ ...prev, emailAddress: event.target.value }))}
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
