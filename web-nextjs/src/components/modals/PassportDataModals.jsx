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
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";

const tabSections = [
	"Passport Data",
	"Crop",
	"Location",
	"Donor",
	"Topography",
	"Availability",
	"Photo",
	"Usage Information",
];

const CROP_GROUPS = [
	"Cereals",
	"Vegetables",
	"Legumes",
	"Root Crops",
	"Medicinal Crops",
	"Fruits",
	"Tree Nuts",
	"Plantation Crops",
	"Pasture and Forage",
	"Ornamentals",
];

const toTabValue = (label) => label.toLowerCase().replace(/\s+/g, "-");

const initialForm = {
	collection_country_code: "",
	accession_number: "",
	old_accession_number: "",
	gb_number: "",
	collection_number: "",
	collecting_date: "",
	acquisition_date: "",
	collector: "",

	crop_group: "",
	crop_name: "",
	genus: "",
	species: "",
	local_name: "",
	species_authority: "",
	subtaxon: "",
	accession_name: "",
	biologicalStatus: "",
	storage: "",
	samplingMethod: "",
	materialCollected: "",
	sampleType: "",

	available_in_the_field: false,
	available_at_in_vitro: false,
	available_for_distribution: false,
	status_of_harvest: "",
	characterized: "",
	field: "",

	donor_name: "",
	growers_name: "",
	growers_contact_number: "",
	donor_code: "",
	donor_accession_number: "",
	location_duplicate_site: "",
	duplicate_institution_name: "",
	other_donor_code_name: "",

	country: "",
	province: "",
	nearest_town: "",
	barangay: "",
	purok_or_sitio: "",
	latitude: "",
	longitude: "",
	altitude: "",

	photo_name: "",
	photos: [],

	site: "",
	topography: "",
	soil_texture: "",
	soil_color: "",
	drainage: "",
	stoniness: "",
	diseases_and_pests: "",
	remarks: "",
	cultural_practice: "",
	herbarium_specimen: false,

	usage_rows: [{ plant_part: "", usage_description: "" }],
};

function Field({ id, label, value, onChange, type = "text", required = false }) {
	return (
		<div className="space-y-2">
			<Label htmlFor={id}>
				{label}
				{required ? <span className="text-red-500">*</span> : null}
			</Label>
			<Input id={id} type={type} value={value} onChange={onChange} required={required} />
		</div>
	);
}

export default function PassportDataModals({ onCreated = (_passport) => {} }) {
	const [open, setOpen] = useState(false);
	const [activeTab, setActiveTab] = useState(toTabValue(tabSections[0]));
	const [form, setForm] = useState(initialForm);
	const [isSaving, setIsSaving] = useState(false);
	const [toast, setToast] = useState(null);

	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const updateField = (key, value) => {
		setForm((prev) => ({ ...prev, [key]: value }));
	};

	const showToast = (message, type) => {
		setToast({ message, type });
		setTimeout(() => {
			setToast(null);
		}, 3000);
	};

	const handleAddPhotos = (event) => {
		const selected = Array.from(event.target.files || []);
		if (selected.length === 0) {
			return;
		}

		setForm((prev) => ({
			...prev,
			photos: [...prev.photos, ...selected],
		}));

		event.target.value = "";
	};

	const handleRemovePhoto = (indexToRemove) => {
		setForm((prev) => ({
			...prev,
			photos: prev.photos.filter((_, index) => index !== indexToRemove),
		}));
	};

	const handleUsageRowChange = (index, key, value) => {
		setForm((prev) => ({
			...prev,
			usage_rows: prev.usage_rows.map((row, rowIndex) =>
				rowIndex === index ? { ...row, [key]: value } : row
			),
		}));
	};

	const handleAddUsageRow = () => {
		setForm((prev) => ({
			...prev,
			usage_rows: [...prev.usage_rows, { plant_part: "", usage_description: "" }],
		}));
	};

	const handleRemoveUsageRow = (indexToRemove) => {
		setForm((prev) => {
			if (prev.usage_rows.length <= 1) {
				return prev;
			}

			return {
				...prev,
				usage_rows: prev.usage_rows.filter((_, index) => index !== indexToRemove),
			};
		});
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		if (!API_BASE) {
			showToast("NEXT_PUBLIC_API_URL is not configured.", "error");
			return;
		}

		if (!form.accession_number.trim()) {
			showToast("Accession number is required.", "error");
			return;
		}

		setIsSaving(true);
		try {
			const formData = new FormData();
			Object.entries(form).forEach(([key, value]) => {
				if (key === "usage_rows") {
					value.forEach((row) => {
						const plantPart = String(row.plant_part || "").trim();
						const usageDescription = String(row.usage_description || "").trim();

						if (plantPart || usageDescription) {
							formData.append("usage_plant_part", plantPart);
							formData.append("usage_description", usageDescription);
						}
					});
					return;
				}

				if (key === "photos") {
					value.forEach((photoFile) => {
						formData.append("photos", photoFile);
					});
					return;
				}

				if (typeof value === "boolean") {
					formData.append(key, value ? "true" : "false");
					return;
				}

				if (value !== null && value !== undefined && String(value).trim() !== "") {
					formData.append(key, String(value).trim());
				}
			});

			const response = await fetch(`${API_BASE}/api/passport-data/create/`, {
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
				const serverMessage =
					data?.message ||
					data?.error ||
					(raw && raw.length < 300 ? raw : "Failed to create passport data.");
				showToast(serverMessage, "error");
				return;
			}

			showToast("Passport data saved successfully.", "success");
			onCreated(data.passport);
			setForm(initialForm);
			setActiveTab(toTabValue(tabSections[0]));
			setOpen(false);
		} catch (error) {
			const message = error instanceof Error ? error.message : "Unable to connect to the server.";
			showToast(`Unable to connect to the server: ${message}`, "error");
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

		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger type="button" className="inline-flex h-8 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground hover:bg-primary/90">
				Add Passport Data
			</DialogTrigger>

			<DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-hidden p-0">
				<div className="p-6 pb-0">
					<DialogHeader>
						<DialogTitle>Add Passport Data</DialogTitle>
						<DialogDescription>
							Fill in the details by section using the tabs below.
						</DialogDescription>
					</DialogHeader>
				</div>

				<form onSubmit={handleSubmit} className="flex h-full flex-col">
					<div className="px-6 pt-4 pb-2 border-b flex justify-end gap-2">
						<Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={isSaving}>
							Cancel
						</Button>
						<Button type="submit" disabled={isSaving}>
							{isSaving ? "Saving..." : "Save Passport Data"}
						</Button>
					</div>

					<div className="p-6 pt-4 overflow-y-auto">
						<Tabs value={activeTab} onValueChange={setActiveTab}>
						<TabsList className="w-full justify-start overflow-x-auto h-auto p-1">
							{tabSections.map((section) => (
								<TabsTrigger key={section} value={toTabValue(section)} className="shrink-0">
									{section}
								</TabsTrigger>
							))}
						</TabsList>

						<TabsContent value="passport-data" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="accession_number" label="Accession Number" required value={form.accession_number} onChange={(e) => updateField("accession_number", e.target.value)} />
								<Field id="gb_number" label="GB Number" value={form.gb_number} onChange={(e) => updateField("gb_number", e.target.value)} />
								<Field id="old_accession_number" label="Old Accession Number" value={form.old_accession_number} onChange={(e) => updateField("old_accession_number", e.target.value)} />
								<Field id="collection_number" label="Collection Number" value={form.collection_number} onChange={(e) => updateField("collection_number", e.target.value)} />
								<Field id="collection_country_code" label="Collection Country Code" value={form.collection_country_code} onChange={(e) => updateField("collection_country_code", e.target.value)} />
								<Field id="collector" label="Collector" value={form.collector} onChange={(e) => updateField("collector", e.target.value)} />
								<Field id="collecting_date" label="Collecting Date" type="date" value={form.collecting_date} onChange={(e) => updateField("collecting_date", e.target.value)} />
								<Field id="acquisition_date" label="Acquisition Date" type="date" value={form.acquisition_date} onChange={(e) => updateField("acquisition_date", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="crop" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<div className="space-y-2">
									<Label htmlFor="crop_group">Crop Group</Label>
									<Select value={form.crop_group} onValueChange={(value) => updateField("crop_group", value)}>
										<SelectTrigger id="crop_group" className="w-full">
											<SelectValue placeholder="Select crop group" />
										</SelectTrigger>
										<SelectContent>
											{CROP_GROUPS.map((group) => (
												<SelectItem key={group} value={group}>
													{group}
												</SelectItem>
											))}
										</SelectContent>
									</Select>
								</div>
								<Field id="crop_name" label="Crop Name" value={form.crop_name} onChange={(e) => updateField("crop_name", e.target.value)} />
								<Field id="genus" label="Genus" value={form.genus} onChange={(e) => updateField("genus", e.target.value)} />
								<Field id="species" label="Species" value={form.species} onChange={(e) => updateField("species", e.target.value)} />
								<Field id="local_name" label="Local Name" value={form.local_name} onChange={(e) => updateField("local_name", e.target.value)} />
								<Field id="species_authority" label="Species Authority" value={form.species_authority} onChange={(e) => updateField("species_authority", e.target.value)} />
								<Field id="subtaxon" label="Subtaxon" value={form.subtaxon} onChange={(e) => updateField("subtaxon", e.target.value)} />
								<Field id="accession_name" label="Accession Name" value={form.accession_name} onChange={(e) => updateField("accession_name", e.target.value)} />
								<Field id="biologicalStatus" label="Biological Status" value={form.biologicalStatus} onChange={(e) => updateField("biologicalStatus", e.target.value)} />
								<Field id="storage" label="Storage" value={form.storage} onChange={(e) => updateField("storage", e.target.value)} />
								<Field id="samplingMethod" label="Sampling Method" value={form.samplingMethod} onChange={(e) => updateField("samplingMethod", e.target.value)} />
								<Field id="materialCollected" label="Material Collected" value={form.materialCollected} onChange={(e) => updateField("materialCollected", e.target.value)} />
								<Field id="sampleType" label="Sample Type" value={form.sampleType} onChange={(e) => updateField("sampleType", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="availability" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<label className="flex items-center gap-2 text-sm">
									<input type="checkbox" checked={form.available_in_the_field} onChange={(e) => updateField("available_in_the_field", e.target.checked)} />
									Available in the Field
								</label>
								<label className="flex items-center gap-2 text-sm">
									<input type="checkbox" checked={form.available_at_in_vitro} onChange={(e) => updateField("available_at_in_vitro", e.target.checked)} />
									Available at In Vitro
								</label>
								<label className="flex items-center gap-2 text-sm md:col-span-2">
									<input type="checkbox" checked={form.available_for_distribution} onChange={(e) => updateField("available_for_distribution", e.target.checked)} />
									Available for Distribution
								</label>
								<Field id="status_of_harvest" label="Status of Harvest" value={form.status_of_harvest} onChange={(e) => updateField("status_of_harvest", e.target.value)} />
								<Field id="characterized" label="Characterized" value={form.characterized} onChange={(e) => updateField("characterized", e.target.value)} />
								<Field id="field" label="Field" value={form.field} onChange={(e) => updateField("field", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="donor" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="donor_name" label="Donor Name" value={form.donor_name} onChange={(e) => updateField("donor_name", e.target.value)} />
								<Field id="growers_name" label="Grower's Name" value={form.growers_name} onChange={(e) => updateField("growers_name", e.target.value)} />
								<Field id="growers_contact_number" label="Grower's Contact Number" value={form.growers_contact_number} onChange={(e) => updateField("growers_contact_number", e.target.value)} />
								<Field id="donor_code" label="Donor Code" value={form.donor_code} onChange={(e) => updateField("donor_code", e.target.value)} />
								<Field id="donor_accession_number" label="Donor Accession Number" value={form.donor_accession_number} onChange={(e) => updateField("donor_accession_number", e.target.value)} />
								<Field id="location_duplicate_site" label="Location Duplicate Site" value={form.location_duplicate_site} onChange={(e) => updateField("location_duplicate_site", e.target.value)} />
								<Field id="duplicate_institution_name" label="Duplicate Institution Name" value={form.duplicate_institution_name} onChange={(e) => updateField("duplicate_institution_name", e.target.value)} />
								<Field id="other_donor_code_name" label="Other Donor Code Name" value={form.other_donor_code_name} onChange={(e) => updateField("other_donor_code_name", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="location" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="country" label="Country" value={form.country} onChange={(e) => updateField("country", e.target.value)} />
								<Field id="province" label="Province" value={form.province} onChange={(e) => updateField("province", e.target.value)} />
								<Field id="nearest_town" label="Nearest Town" value={form.nearest_town} onChange={(e) => updateField("nearest_town", e.target.value)} />
								<Field id="barangay" label="Barangay" value={form.barangay} onChange={(e) => updateField("barangay", e.target.value)} />
								<Field id="purok_or_sitio" label="Purok/Sitio" value={form.purok_or_sitio} onChange={(e) => updateField("purok_or_sitio", e.target.value)} />
								<Field id="latitude" label="Latitude" value={form.latitude} onChange={(e) => updateField("latitude", e.target.value)} />
								<Field id="longitude" label="Longitude" value={form.longitude} onChange={(e) => updateField("longitude", e.target.value)} />
								<Field id="altitude" label="Altitude" value={form.altitude} onChange={(e) => updateField("altitude", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="photo" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4">
								<Field id="photo_name" label="Photo Name" value={form.photo_name} onChange={(e) => updateField("photo_name", e.target.value)} />
								<div className="space-y-2">
									<Label htmlFor="photo">Photo Files</Label>
									<Input
										id="photo"
										type="file"
										accept="image/*"
										multiple
										onChange={handleAddPhotos}
									/>
									{form.photos.length > 0 ? (
										<div className="space-y-2 rounded-md border p-3">
											{form.photos.map((photoFile, index) => (
												<div key={`${photoFile.name}-${index}`} className="flex items-center justify-between gap-2 text-sm">
													<span className="truncate">{photoFile.name}</span>
													<Button type="button" variant="outline" size="sm" onClick={() => handleRemovePhoto(index)}>
														Delete
													</Button>
												</div>
											))}
										</div>
									) : null}
								</div>
							</div>
						</TabsContent>

						<TabsContent value="topography" className="mt-4 rounded-md border p-4 max-h-[52vh] overflow-y-auto">
							<div className="space-y-4">
								<div className="grid gap-4 md:grid-cols-2">
									<Field id="site" label="Site" value={form.site} onChange={(e) => updateField("site", e.target.value)} />
									<Field id="topography" label="Topography" value={form.topography} onChange={(e) => updateField("topography", e.target.value)} />
									<Field id="soil_texture" label="Soil Texture" value={form.soil_texture} onChange={(e) => updateField("soil_texture", e.target.value)} />
									<Field id="soil_color" label="Soil Color" value={form.soil_color} onChange={(e) => updateField("soil_color", e.target.value)} />
									<Field id="drainage" label="Drainage" value={form.drainage} onChange={(e) => updateField("drainage", e.target.value)} />
									<Field id="stoniness" label="Stoniness" value={form.stoniness} onChange={(e) => updateField("stoniness", e.target.value)} />
									<label className="flex items-center gap-2 text-sm md:col-span-2">
										<input type="checkbox" checked={form.herbarium_specimen} onChange={(e) => updateField("herbarium_specimen", e.target.checked)} />
										Herbarium Specimen
									</label>
									<div className="space-y-2 md:col-span-2">
										<Label htmlFor="cultural_practice">Cultural Practice</Label>
										<Textarea id="cultural_practice" value={form.cultural_practice} onChange={(e) => updateField("cultural_practice", e.target.value)} />
									</div>
									<div className="space-y-2 md:col-span-2">
										<Label htmlFor="diseases_and_pests">Diseases and Pests</Label>
										<Textarea id="diseases_and_pests" value={form.diseases_and_pests} onChange={(e) => updateField("diseases_and_pests", e.target.value)} />
									</div>
									<div className="space-y-2 md:col-span-2">
										<Label htmlFor="remarks">Remarks</Label>
										<Textarea id="remarks" value={form.remarks} onChange={(e) => updateField("remarks", e.target.value)} />
									</div>
								</div>

							</div>
						</TabsContent>

						<TabsContent value="usage-information" className="mt-4 rounded-md border p-4 max-h-[52vh] overflow-y-auto">
							<div className="space-y-4">
								{form.usage_rows.map((row, index) => (
									<div key={`usage-row-${index}`} className="rounded-md border p-4 space-y-4">
										<div className="grid gap-4 md:grid-cols-2">
											<Field
												id={`usage_plant_part_${index}`}
												label="Plant Part"
												value={row.plant_part}
												onChange={(e) => handleUsageRowChange(index, "plant_part", e.target.value)}
											/>
											<div className="space-y-2 md:col-span-2">
												<Label htmlFor={`usage_description_${index}`}>Usage Description</Label>
												<Textarea
													id={`usage_description_${index}`}
													value={row.usage_description}
													onChange={(e) => handleUsageRowChange(index, "usage_description", e.target.value)}
												/>
											</div>
										</div>

										<div className="flex justify-end">
											<Button
												type="button"
												variant="outline"
												size="sm"
												onClick={() => handleRemoveUsageRow(index)}
												disabled={form.usage_rows.length <= 1}
											>
												Remove
											</Button>
										</div>
									</div>
								))}

								<div>
									<Button type="button" variant="outline" onClick={handleAddUsageRow}>
										Add Plant Part & Usage Description
									</Button>
								</div>

							</div>
						</TabsContent>
					</Tabs>
					</div>
				</form>
			</DialogContent>
		</Dialog>
		</>
	);
}
