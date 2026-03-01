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

export default function ImportPassportData({ onImported = async () => {} }) {
	const [open, setOpen] = useState(false);
	const [file, setFile] = useState(null);
	const [isUploading, setIsUploading] = useState(false);
	const [summary, setSummary] = useState(null);
	const [error, setError] = useState("");
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const resetState = () => {
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

		if (!file) {
			setError("Please select an Excel file first.");
			return;
		}

		setIsUploading(true);
		try {
			const formData = new FormData();
			formData.append("file", file);

			const response = await fetch(`${API_BASE}/api/passport-data/upload/`, {
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
		} catch (importError) {
			const message = importError instanceof Error ? importError.message : "Unable to connect to server.";
			setError(message);
		} finally {
			setIsUploading(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogTrigger asChild>
				<Button type="button" variant="outline">Import Passport Data</Button>
			</DialogTrigger>

			<DialogContent className="sm:max-w-lg">
				<DialogHeader>
					<DialogTitle>Import Passport Data</DialogTitle>
					<DialogDescription>Upload an Excel file to import passport records.</DialogDescription>
				</DialogHeader>

				<div className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="passport-import-file">Excel File</Label>
						<Input
							id="passport-import-file"
							type="file"
							accept=".xlsx,.xls"
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
