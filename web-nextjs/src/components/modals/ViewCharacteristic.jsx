"use client";

import { useState } from "react";

import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

function DetailRow({ label, value }) {
	const safeValue = value === null || value === undefined || String(value).trim() === "" ? "-" : String(value);

	return (
		<div className="rounded-md border px-3 py-2 text-sm">
			<p className="text-muted-foreground text-xs">{label}</p>
			<p className="font-medium break-words">{safeValue}</p>
		</div>
	);
}

export default function ViewCharacteristic({ open, onOpenChange, data }) {
	const fields = Array.isArray(data?.fields) ? data.fields : [];
	const [expandedImageUrl, setExpandedImageUrl] = useState(null);
	const apiBase = process.env.NEXT_PUBLIC_API_URL || "";

	const resolvePhotoUrl = (value) => {
		if (!value || typeof value !== "string") {
			return null;
		}

		if (value.startsWith("http://") || value.startsWith("https://") || value.startsWith("data:image/")) {
			return value;
		}

		const normalizedBase = apiBase.replace(/\/$/, "");
		const normalizedValue = value.startsWith("/") ? value : `/${value}`;

		if (normalizedValue.startsWith("/media/")) {
			return normalizedBase ? `${normalizedBase}${normalizedValue}` : normalizedValue;
		}

		return normalizedBase ? `${normalizedBase}/media${normalizedValue}` : `/media${normalizedValue}`;
	};
	const photoUrl = resolvePhotoUrl(data?.photo);
	const hasPhotoField = fields.some((field) => field?.name === "photo");
	const displayFields = hasPhotoField || !photoUrl
		? fields
		: [
			...fields,
			{
				name: "photo",
				label: "Photo",
				value: photoUrl,
			},
		];

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-4xl h-[85vh] max-h-[85vh] overflow-hidden p-0 flex flex-col">
				{expandedImageUrl ? (
					<div className="fixed inset-0 z-[70] bg-black/70 flex items-center justify-center p-4" onClick={() => setExpandedImageUrl(null)}>
						<div className="max-w-5xl max-h-[90vh]" onClick={(event) => event.stopPropagation()}>
							<img
								src={expandedImageUrl}
								alt="Characteristic photo"
								className="max-h-[85vh] max-w-[90vw] object-contain rounded-md"
							/>
							<div className="mt-2 flex justify-end">
								<Button type="button" variant="outline" onClick={() => setExpandedImageUrl(null)}>
									Close image
								</Button>
							</div>
						</div>
					</div>
				) : null}

				<div className="p-6 pb-0">
					<DialogHeader>
						<DialogTitle>View Characteristic</DialogTitle>
						<DialogDescription>
							Review crop-specific characteristic details.
						</DialogDescription>
					</DialogHeader>
				</div>

				<div className="p-6 pt-4 overflow-y-auto space-y-4 flex-1 min-h-0">
					<div className="grid gap-3 md:grid-cols-2">
						<DetailRow label="Crop" value={data?.crop_name} />
						<DetailRow label="Source Model" value={data?.source_model} />
						<DetailRow label="Accession Number" value={data?.passport?.accession_number} />
						<DetailRow label="GB Number" value={data?.passport?.gb_number} />
						<DetailRow label="Old Accession Number" value={data?.passport?.old_accession_number} />
					</div>

					<div className="rounded-md border p-4 space-y-3">
						<p className="text-sm font-medium">Characteristic Fields</p>
						{displayFields.length > 0 ? (
							<div className="grid gap-3 md:grid-cols-2">
								{displayFields.map((field, index) => {
									if (field?.name === "photo") {
										const fieldPhotoUrl = resolvePhotoUrl(field?.value);
										return (
											<div key={`${field.name ?? "field"}-${index}`} className="rounded-md border px-3 py-2 text-sm md:col-span-2">
												<p className="text-muted-foreground text-xs">{field.label || "Photo"}</p>
												{fieldPhotoUrl ? (
													<button
														type="button"
														onClick={() => setExpandedImageUrl(fieldPhotoUrl)}
														className="inline-flex flex-col items-start gap-2 mt-2"
													>
														<img
															src={fieldPhotoUrl}
															alt="Characteristic photo"
															className="h-24 w-24 rounded-md border object-cover"
														/>
														<span className="text-xs text-muted-foreground">Click image to expand</span>
													</button>
												) : (
													<p className="font-medium">-</p>
												)}
											</div>
										);
									}

									return (
										<DetailRow
											key={`${field.name ?? "field"}-${index}`}
											label={field.label || field.name || "Field"}
											value={field.value}
										/>
									);
								})}
							</div>
						) : (
							<p className="text-sm text-muted-foreground">No characteristic fields available.</p>
						)}
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
}
