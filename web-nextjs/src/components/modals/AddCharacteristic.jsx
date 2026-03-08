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
import { apiFetch } from "@/lib/api";

const CROPS = [
	"Akapulko",
	"Banana",
	"Bittergourd",
	"Cashew",
	"Cassava",
	"Citronella",
	"Corn",
	"Cowpea",
	"Eggplant",
	"Fruits",
	"Garden Spurge",
	"Ginger",
	"Gotu Kola",
	"Guava",
	"Hyacinth",
	"Jatropha",
	"Lagundi",
	"Lima",
	"Luffa",
	"Malunggay",
	"Mangosteen",
	"Mung bea",
	"Peanut",
	"Pepper",
	"Pigeon pea",
	"Pole Sitao",
	"Ricebean",
	"Sabila",
	"Sambong",
	"Snap bean",
	"Soybean",
	"Squash",
	"Sweet potato",
	"Taro",
	"Tomato",
	"Turmeric",
	"Winged bean",
	"Xanthosoma",
	"Yam",
	"Yerba buena",
];

export default function AddCharacteristic({ onImported = async () => {} }) {
	const [open, setOpen] = useState(false);
	const [cropName, setCropName] = useState("");
	const [file, setFile] = useState(null);
	const [isUploading, setIsUploading] = useState(false);
	const [summary, setSummary] = useState(null);
	const [error, setError] = useState("");
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const resetState = () => {
		setCropName("");
		setFile(null);
		setSummary(null);
		setError("");
	};

	const handleOpenChange = (nextOpen) => {
		setOpen(nextOpen);
		if (!nextOpen) {
			resetState();
		}
	};

	const handleImport = async () => {
		setError("");
		setSummary(null);

		if (!API_BASE) {
			setError("API base URL is not configured.");
			return;
		}

		if (!cropName) {
			setError("Please select a crop.");
			return;
		}

		if (!file) {
			setError("Please select an .xlsx file.");
			return;
		}

		const fileName = (file.name || "").toLowerCase();
		if (!fileName.endsWith(".xlsx")) {
			setError("Only .xlsx files are allowed.");
			return;
		}

		setIsUploading(true);
		try {
			const formData = new FormData();
			formData.append("file", file);
			formData.append("crop_name", cropName);

			const response = await apiFetch(`${API_BASE}/api/characterization-data/upload/`, {
				method: "POST",
				body: formData,
			});

			const raw = await response.text();
			let data = null;
			try {
				data = raw ? JSON.parse(raw) : null;
			} catch {
				data = null;
			}

			if (!response.ok || !data?.success) {
				setError(data?.message || (raw && raw.length < 300 ? raw : "Import failed."));
				return;
			}

			setSummary(data.summary || null);
			await onImported();
		} catch (uploadError) {
			const message = uploadError instanceof Error ? uploadError.message : "Unable to connect to server.";
			setError(message);
		} finally {
			setIsUploading(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogTrigger asChild>
				<Button type="button">Add Characteristic</Button>
			</DialogTrigger>

			<DialogContent className="sm:max-w-lg">
				<DialogHeader>
					<DialogTitle>Add Characteristic</DialogTitle>
					<DialogDescription>
						Select crop and upload an .xlsx file. Duplicate checks use accession_number, then gb_number, then old_accession_number.
					</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="characteristic-crop">Crop</Label>
						<select
							id="characteristic-crop"
							value={cropName}
							onChange={(event) => setCropName(event.target.value)}
							className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
						>
							<option value="">Select crop</option>
							{CROPS.map((crop) => (
								<option key={crop} value={crop}>
									{crop}
								</option>
							))}
						</select>
					</div>

					<div className="space-y-2">
						<Label htmlFor="characteristic-import-file">Excel File (.xlsx only)</Label>
						<Input
							id="characteristic-import-file"
							type="file"
							accept=".xlsx"
							onChange={(event) => setFile(event.target.files?.[0] || null)}
						/>
					</div>

					{error ? (
						<div className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
							{error}
						</div>
					) : null}

					{summary ? (
						<div className="rounded-md border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-700 space-y-1">
							<p>Import completed.</p>
							<p>Sheet: {summary.sheet || "-"}</p>
							<p>Total rows: {summary.total ?? 0}</p>
							<p>Successful: {summary.successful ?? 0}</p>
							<p>Failed: {summary.failed ?? 0}</p>
						</div>
					) : null}

					<div className="flex justify-end gap-2">
						<Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isUploading}>
							Cancel
						</Button>
						<Button type="button" onClick={handleImport} disabled={isUploading}>
							{isUploading ? "Importing..." : "Import"}
						</Button>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
}
