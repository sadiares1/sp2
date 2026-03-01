"use client";

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

function Field({ id, label, value, onChange, type = "text" }) {
	return (
		<div className="space-y-2">
			<Label htmlFor={id}>{label}</Label>
			<Input id={id} type={type} value={value ?? ""} onChange={onChange} />
		</div>
	);
}

export default function EditPassportData({
	open,
	onOpenChange,
	form,
	onChange,
	onSave,
}) {
	const updateField = (key, value) => {
		onChange((prev) => ({ ...(prev || {}), [key]: value }));
	};

	const usageRows = Array.isArray(form?.usage_rows)
		? form.usage_rows
		: [{ plant_part: "", usage_description: "" }];

	const updateUsageRow = (index, key, value) => {
		onChange((prev) => ({
			...(prev || {}),
			usage_rows: usageRows.map((row, rowIndex) =>
				rowIndex === index ? { ...row, [key]: value } : row
			),
		}));
	};

	const addUsageRow = () => {
		onChange((prev) => ({
			...(prev || {}),
			usage_rows: [...usageRows, { plant_part: "", usage_description: "" }],
		}));
	};

	const removeUsageRow = (indexToRemove) => {
		if (usageRows.length <= 1) {
			return;
		}

		onChange((prev) => ({
			...(prev || {}),
			usage_rows: usageRows.filter((_, index) => index !== indexToRemove),
		}));
	};

	const removeExistingPhoto = (indexToRemove) => {
		const photos = Array.isArray(form?.photos) ? form.photos : [];
		const nextPhotos = photos.filter((_, index) => index !== indexToRemove);

		onChange((prev) => ({
			...(prev || {}),
			photos: nextPhotos,
			photo_count: nextPhotos.length,
			photo_name: nextPhotos.length > 0 ? (nextPhotos[0]?.photo_name || prev?.photo_name || "") : "",
		}));
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-hidden p-0">
				<div className="p-6 pb-0">
					<DialogHeader>
						<DialogTitle>Edit Passport Data</DialogTitle>
						<DialogDescription>
							Edit passport data details by section.
						</DialogDescription>
					</DialogHeader>
				</div>

				<div className="px-6 pt-4 pb-2 border-b flex justify-end gap-2">
					<Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
						Cancel
					</Button>
					<Button type="button" onClick={onSave}>
						Save
					</Button>
				</div>

				<div className="p-6 pt-4 overflow-y-auto">
					<Tabs defaultValue={toTabValue(tabSections[0])}>
						<TabsList className="w-full justify-start overflow-x-auto h-auto p-1">
							{tabSections.map((section) => (
								<TabsTrigger key={section} value={toTabValue(section)} className="shrink-0">
									{section}
								</TabsTrigger>
							))}
						</TabsList>

						<TabsContent value="passport-data" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="edit-accession_number" label="Accession Number" value={form?.accession_number} onChange={(e) => updateField("accession_number", e.target.value)} />
								<Field id="edit-gb_number" label="GB Number" value={form?.gb_number} onChange={(e) => updateField("gb_number", e.target.value)} />
								<Field id="edit-old_accession_number" label="Old Accession Number" value={form?.old_accession_number} onChange={(e) => updateField("old_accession_number", e.target.value)} />
								<Field id="edit-collection_number" label="Collection Number" value={form?.collection_number} onChange={(e) => updateField("collection_number", e.target.value)} />
								<Field id="edit-collection_country_code" label="Collection Country Code" value={form?.collection_country_code} onChange={(e) => updateField("collection_country_code", e.target.value)} />
								<Field id="edit-collector" label="Collector" value={form?.collector} onChange={(e) => updateField("collector", e.target.value)} />
								<Field id="edit-collecting_date" label="Collecting Date" type="date" value={form?.collecting_date} onChange={(e) => updateField("collecting_date", e.target.value)} />
								<Field id="edit-acquisition_date" label="Acquisition Date" type="date" value={form?.acquisition_date} onChange={(e) => updateField("acquisition_date", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="crop" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<div className="space-y-2">
									<Label htmlFor="edit-crop_group">Crop Group</Label>
									<Select value={form?.crop_group || ""} onValueChange={(value) => updateField("crop_group", value)}>
										<SelectTrigger id="edit-crop_group" className="w-full">
											<SelectValue placeholder="Select crop group" />
										</SelectTrigger>
										<SelectContent>
											{CROP_GROUPS.map((group) => (
												<SelectItem key={group} value={group}>{group}</SelectItem>
											))}
										</SelectContent>
									</Select>
								</div>
								<Field id="edit-crop_name" label="Crop Name" value={form?.crop_name} onChange={(e) => updateField("crop_name", e.target.value)} />
								<Field id="edit-genus" label="Genus" value={form?.genus} onChange={(e) => updateField("genus", e.target.value)} />
								<Field id="edit-species" label="Species" value={form?.species} onChange={(e) => updateField("species", e.target.value)} />
								<Field id="edit-local_name" label="Local Name" value={form?.local_name} onChange={(e) => updateField("local_name", e.target.value)} />
								<Field id="edit-species_authority" label="Species Authority" value={form?.species_authority} onChange={(e) => updateField("species_authority", e.target.value)} />
								<Field id="edit-subtaxon" label="Subtaxon" value={form?.subtaxon} onChange={(e) => updateField("subtaxon", e.target.value)} />
								<Field id="edit-accession_name" label="Accession Name" value={form?.accession_name} onChange={(e) => updateField("accession_name", e.target.value)} />
								<Field id="edit-biologicalStatus" label="Biological Status" value={form?.biologicalStatus} onChange={(e) => updateField("biologicalStatus", e.target.value)} />
								<Field id="edit-storage" label="Storage" value={form?.storage} onChange={(e) => updateField("storage", e.target.value)} />
								<Field id="edit-samplingMethod" label="Sampling Method" value={form?.samplingMethod} onChange={(e) => updateField("samplingMethod", e.target.value)} />
								<Field id="edit-materialCollected" label="Material Collected" value={form?.materialCollected} onChange={(e) => updateField("materialCollected", e.target.value)} />
								<Field id="edit-sampleType" label="Sample Type" value={form?.sampleType} onChange={(e) => updateField("sampleType", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="location" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="edit-country" label="Country" value={form?.country} onChange={(e) => updateField("country", e.target.value)} />
								<Field id="edit-province" label="Province" value={form?.province} onChange={(e) => updateField("province", e.target.value)} />
								<Field id="edit-nearest_town" label="Nearest Town" value={form?.nearest_town} onChange={(e) => updateField("nearest_town", e.target.value)} />
								<Field id="edit-barangay" label="Barangay" value={form?.barangay} onChange={(e) => updateField("barangay", e.target.value)} />
								<Field id="edit-purok_or_sitio" label="Purok/Sitio" value={form?.purok_or_sitio} onChange={(e) => updateField("purok_or_sitio", e.target.value)} />
								<Field id="edit-latitude" label="Latitude" value={form?.latitude} onChange={(e) => updateField("latitude", e.target.value)} />
								<Field id="edit-longitude" label="Longitude" value={form?.longitude} onChange={(e) => updateField("longitude", e.target.value)} />
								<Field id="edit-altitude" label="Altitude" value={form?.altitude} onChange={(e) => updateField("altitude", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="donor" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="edit-donor_name" label="Donor Name" value={form?.donor_name} onChange={(e) => updateField("donor_name", e.target.value)} />
								<Field id="edit-growers_name" label="Grower's Name" value={form?.growers_name} onChange={(e) => updateField("growers_name", e.target.value)} />
								<Field id="edit-growers_contact_number" label="Grower's Contact Number" value={form?.growers_contact_number} onChange={(e) => updateField("growers_contact_number", e.target.value)} />
								<Field id="edit-donor_code" label="Donor Code" value={form?.donor_code} onChange={(e) => updateField("donor_code", e.target.value)} />
								<Field id="edit-donor_accession_number" label="Donor Accession Number" value={form?.donor_accession_number} onChange={(e) => updateField("donor_accession_number", e.target.value)} />
								<Field id="edit-location_duplicate_site" label="Location Duplicate Site" value={form?.location_duplicate_site} onChange={(e) => updateField("location_duplicate_site", e.target.value)} />
								<Field id="edit-duplicate_institution_name" label="Duplicate Institution Name" value={form?.duplicate_institution_name} onChange={(e) => updateField("duplicate_institution_name", e.target.value)} />
								<Field id="edit-other_donor_code_name" label="Other Donor Code Name" value={form?.other_donor_code_name} onChange={(e) => updateField("other_donor_code_name", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="topography" className="mt-4 rounded-md border p-4 max-h-[52vh] overflow-y-auto">
							<div className="grid gap-4 md:grid-cols-2">
								<Field id="edit-site" label="Site" value={form?.site} onChange={(e) => updateField("site", e.target.value)} />
								<Field id="edit-topography" label="Topography" value={form?.topography} onChange={(e) => updateField("topography", e.target.value)} />
								<Field id="edit-soil_texture" label="Soil Texture" value={form?.soil_texture} onChange={(e) => updateField("soil_texture", e.target.value)} />
								<Field id="edit-soil_color" label="Soil Color" value={form?.soil_color} onChange={(e) => updateField("soil_color", e.target.value)} />
								<Field id="edit-drainage" label="Drainage" value={form?.drainage} onChange={(e) => updateField("drainage", e.target.value)} />
								<Field id="edit-stoniness" label="Stoniness" value={form?.stoniness} onChange={(e) => updateField("stoniness", e.target.value)} />
								<label className="flex items-center gap-2 text-sm md:col-span-2">
									<input type="checkbox" checked={Boolean(form?.herbarium_specimen)} onChange={(e) => updateField("herbarium_specimen", e.target.checked)} />
									Herbarium Specimen
								</label>
								<div className="space-y-2 md:col-span-2">
									<Label htmlFor="edit-culture">Cultural Practice</Label>
									<Textarea id="edit-culture" value={form?.cultural_practice ?? ""} onChange={(e) => updateField("cultural_practice", e.target.value)} />
								</div>
								<div className="space-y-2 md:col-span-2">
									<Label htmlFor="edit-diseases">Diseases and Pests</Label>
									<Textarea id="edit-diseases" value={form?.diseases_and_pests ?? ""} onChange={(e) => updateField("diseases_and_pests", e.target.value)} />
								</div>
								<div className="space-y-2 md:col-span-2">
									<Label htmlFor="edit-remarks">Remarks</Label>
									<Textarea id="edit-remarks" value={form?.remarks ?? ""} onChange={(e) => updateField("remarks", e.target.value)} />
								</div>
							</div>
						</TabsContent>

						<TabsContent value="availability" className="mt-4 rounded-md border p-4">
							<div className="grid gap-4 md:grid-cols-2">
								<label className="flex items-center gap-2 text-sm">
									<input type="checkbox" checked={Boolean(form?.available_in_the_field)} onChange={(e) => updateField("available_in_the_field", e.target.checked)} />
									Available in the Field
								</label>
								<label className="flex items-center gap-2 text-sm">
									<input type="checkbox" checked={Boolean(form?.available_at_in_vitro)} onChange={(e) => updateField("available_at_in_vitro", e.target.checked)} />
									Available at In Vitro
								</label>
								<label className="flex items-center gap-2 text-sm md:col-span-2">
									<input type="checkbox" checked={Boolean(form?.available_for_distribution)} onChange={(e) => updateField("available_for_distribution", e.target.checked)} />
									Available for Distribution
								</label>
								<Field id="edit-status_of_harvest" label="Status of Harvest" value={form?.status_of_harvest} onChange={(e) => updateField("status_of_harvest", e.target.value)} />
								<Field id="edit-characterized" label="Characterized" value={form?.characterized} onChange={(e) => updateField("characterized", e.target.value)} />
								<Field id="edit-field" label="Field" value={form?.field} onChange={(e) => updateField("field", e.target.value)} />
							</div>
						</TabsContent>

						<TabsContent value="photo" className="mt-4 rounded-md border p-4 space-y-4">
							<Field id="edit-photo_name" label="Photo Name" value={form?.photo_name} onChange={(e) => updateField("photo_name", e.target.value)} />
							<div className="space-y-2">
								<Label>Existing Photos</Label>
								{Array.isArray(form?.photos) && form.photos.length > 0 ? (
									<div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
										{form.photos.map((photo, index) => (
											<div key={photo.id ?? `edit-photo-${index}`} className="rounded-md border p-2 space-y-2">
												<a
													href={photo.url || "#"}
													target="_blank"
													rel="noreferrer"
													className={`block ${photo.url ? "hover:opacity-90" : "opacity-60 cursor-not-allowed"}`}
													onClick={(event) => {
														if (!photo.url) event.preventDefault();
													}}
												>
													{photo.url ? (
														<img src={photo.url} alt={photo.photo_name || `Photo ${index + 1}`} className="h-24 w-full object-cover rounded" />
													) : (
														<div className="h-24 w-full rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">No image file</div>
													)}
												</a>
												<p className="text-xs truncate">{photo.photo_name || `Photo ${index + 1}`}</p>
												<Button type="button" variant="outline" size="sm" onClick={() => removeExistingPhoto(index)}>
													Remove
												</Button>
											</div>
										))}
									</div>
								) : (
									<p className="text-sm text-muted-foreground">No photos available.</p>
								)}
							</div>
						</TabsContent>

						<TabsContent value="usage-information" className="mt-4 rounded-md border p-4 space-y-4 max-h-[52vh] overflow-y-auto">
							{usageRows.map((usage, index) => (
								<div key={`edit-usage-${index}`} className="rounded-md border p-3 space-y-3">
									<Field
										id={`edit-usage-part-${index}`}
										label="Plant Part"
										value={usage?.plant_part}
										onChange={(e) => updateUsageRow(index, "plant_part", e.target.value)}
									/>
									<div className="space-y-2">
										<Label htmlFor={`edit-usage-desc-${index}`}>Usage Description</Label>
										<Textarea
											id={`edit-usage-desc-${index}`}
											value={usage?.usage_description ?? ""}
											onChange={(e) => updateUsageRow(index, "usage_description", e.target.value)}
										/>
									</div>
									<div className="flex justify-end">
										<Button type="button" variant="outline" size="sm" onClick={() => removeUsageRow(index)} disabled={usageRows.length <= 1}>
											Remove
										</Button>
									</div>
								</div>
							))}

							<div>
								<Button type="button" variant="outline" onClick={addUsageRow}>
									Add Plant Part & Usage Description
								</Button>
							</div>
						</TabsContent>
					</Tabs>
				</div>
			</DialogContent>
		</Dialog>
	);
}
