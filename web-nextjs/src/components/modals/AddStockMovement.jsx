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
import { Textarea } from "@/components/ui/textarea";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api";

const initialForm = {
	movementType: "ACQUISITION",
	quantity: "",
	unit: "",
	movementDate: new Date().toISOString().slice(0, 10),
	location: "",
	shelfNo: "",
	trayNo: "",
	bottleNo: "",
	packetNo: "",
	activeBase: "",
	batchReference: "",
	pollType: "",
	remarks: "",
};

export default function AddStockMovement({
	productId,
	onCreated = async () => {},
	open: openProp,
	onOpenChange,
}) {
	const [internalOpen, setInternalOpen] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState("");
	const [toast, setToast] = useState(null);
	const [form, setForm] = useState(initialForm);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;
	const open = openProp !== undefined ? openProp : internalOpen;

	const showToast = (message, type) => {
		setToast({ message, type });
		setTimeout(() => {
			setToast(null);
		}, 3000);
	};

	const setOpen = (nextOpen) => {
		if (openProp === undefined) {
			setInternalOpen(nextOpen);
		}
		onOpenChange?.(nextOpen);
	};

	const isDisabled = useMemo(() => !productId || isSaving, [productId, isSaving]);

	const resetForm = () => {
		setForm(initialForm);
		setError("");
	};

	const handleSave = async () => {
		if (!API_BASE) {
			setError("API base URL is not configured.");
			showToast("API base URL is not configured.", "error");
			return;
		}
		if (!productId) {
			setError("Product ID is missing.");
			showToast("Product ID is missing.", "error");
			return;
		}
		if (!form.quantity.trim()) {
			setError("Quantity is required.");
			showToast("Quantity is required.", "error");
			return;
		}
		if (Number(form.quantity) < 0) {
			setError("Quantity cannot be negative.");
			showToast("Quantity cannot be negative.", "error");
			return;
		}
		if (!form.movementDate) {
			setError("Movement date is required.");
			showToast("Movement date is required.", "error");
			return;
		}

		setIsSaving(true);
		setError("");
		try {
			const response = await apiFetch(`${API_BASE}/api/product/${productId}/stock-movement/create/`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(form),
			});

			const raw = await response.text();
			let data = null;
			try {
				data = raw ? JSON.parse(raw) : null;
			} catch {
				data = null;
			}

			if (!response.ok || !data?.success) {
				const message = data?.message || "Failed to add stock movement.";
				setError(message);
				showToast(message, "error");
				return;
			}

			await onCreated();
			showToast("Stock movement added successfully.", "success");
			setOpen(false);
			resetForm();
		} catch {
			setError("Unable to connect to the server.");
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
					<Button type="button" size="sm" disabled={!productId}>
						Add Stock Movement
					</Button>
				</DialogTrigger>
				<DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-2xl">
					<DialogHeader>
						<DialogTitle>Add Stock Movement</DialogTitle>
						<DialogDescription>Select type and enter movement details.</DialogDescription>
					</DialogHeader>

				<div className="space-y-4">
					<div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
						<div className="space-y-2">
							<Label>Type</Label>
							<Select
								value={form.movementType}
								onValueChange={(value) => setForm((prev) => ({ ...prev, movementType: value }))}
							>
								<SelectTrigger>
									<SelectValue placeholder="Select movement type" />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="ACQUISITION">Acquisition</SelectItem>
									<SelectItem value="DISPOSAL">Disposal</SelectItem>
									<SelectItem value="STOCK_TAKE">Stock Takes</SelectItem>
								</SelectContent>
							</Select>
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-quantity">Quantity</Label>
							<Input
								id="stock-quantity"
								type="number"
								min="0"
								step="0.01"
								value={form.quantity}
								onChange={(event) => setForm((prev) => ({ ...prev, quantity: event.target.value }))}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-date">Movement Date</Label>
							<Input
								id="stock-date"
								type="date"
								value={form.movementDate}
								onChange={(event) => setForm((prev) => ({ ...prev, movementDate: event.target.value }))}
							/>
						</div>
					</div>

					<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
						<div className="space-y-2">
							<Label htmlFor="stock-unit">Unit</Label>
							<Input id="stock-unit" value={form.unit} onChange={(event) => setForm((prev) => ({ ...prev, unit: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-location">Location</Label>
							<Input id="stock-location" value={form.location} onChange={(event) => setForm((prev) => ({ ...prev, location: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-shelf">Shelf No</Label>
							<Input id="stock-shelf" value={form.shelfNo} onChange={(event) => setForm((prev) => ({ ...prev, shelfNo: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-tray">Tray No</Label>
							<Input id="stock-tray" value={form.trayNo} onChange={(event) => setForm((prev) => ({ ...prev, trayNo: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-bottle">Bottle No</Label>
							<Input id="stock-bottle" value={form.bottleNo} onChange={(event) => setForm((prev) => ({ ...prev, bottleNo: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-packet">Packet No</Label>
							<Input id="stock-packet" value={form.packetNo} onChange={(event) => setForm((prev) => ({ ...prev, packetNo: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-active-base">Active Base</Label>
							<Input id="stock-active-base" value={form.activeBase} onChange={(event) => setForm((prev) => ({ ...prev, activeBase: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-batch">Batch Reference</Label>
							<Input id="stock-batch" value={form.batchReference} onChange={(event) => setForm((prev) => ({ ...prev, batchReference: event.target.value }))} />
						</div>
						<div className="space-y-2">
							<Label htmlFor="stock-poll">Poll Type</Label>
							<Input id="stock-poll" value={form.pollType} onChange={(event) => setForm((prev) => ({ ...prev, pollType: event.target.value }))} />
						</div>
					</div>

					<div className="space-y-2">
						<Label htmlFor="stock-remarks">Remarks</Label>
						<Textarea id="stock-remarks" value={form.remarks} onChange={(event) => setForm((prev) => ({ ...prev, remarks: event.target.value }))} />
					</div>

					{error ? <p className="text-sm text-red-600">{error}</p> : null}

					<div className="flex justify-end gap-2">
						<Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isDisabled}>
							Cancel
						</Button>
						<Button type="button" onClick={handleSave} disabled={isDisabled}>
							{isSaving ? "Saving..." : "Save"}
						</Button>
					</div>
				</div>
				</DialogContent>
			</Dialog>
		</>
	);
}
