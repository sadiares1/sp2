"use client";

import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

const toTabValue = (label) => label.toLowerCase().replace(/\s+/g, "-");

const passportDataFields = [
	["Collection Country Code", "collection_country_code"],
	["Accession Number", "accession_number"],
	["Old Accession Number", "old_accession_number"],
	["GB Number", "gb_number"],
	["Collection Number", "collection_number"],
	["Collecting Date", "collecting_date"],
	["Acquisition Date", "acquisition_date"],
	["Collector", "collector"],
];

const cropFields = [
	["Crop Group", "crop_group"],
	["Crop Name", "crop_name"],
	["Genus", "genus"],
	["Species", "species"],
	["Local Name", "local_name"],
	["Species Authority", "species_authority"],
	["Subtaxon", "subtaxon"],
	["Accession Name", "accession_name"],
	["Biological Status", "biologicalStatus"],
	["Storage", "storage"],
	["Sampling Method", "samplingMethod"],
	["Material Collected", "materialCollected"],
	["Sample Type", "sampleType"],
];

const locationFields = [
	["Country", "country"],
	["Province", "province"],
	["Nearest Town", "nearest_town"],
	["Barangay", "barangay"],
	["Purok/Sitio", "purok_or_sitio"],
	["Latitude", "latitude"],
	["Longitude", "longitude"],
	["Altitude", "altitude"],
];

const donorFields = [
	["Donor Name", "donor_name"],
	["Grower's Name", "growers_name"],
	["Grower's Contact Number", "growers_contact_number"],
	["Donor Code", "donor_code"],
	["Donor Accession Number", "donor_accession_number"],
	["Location Duplicate Site", "location_duplicate_site"],
	["Duplicate Institution Name", "duplicate_institution_name"],
	["Other Donor Code Name", "other_donor_code_name"],
];

const topographyFields = [
	["Site", "site"],
	["Topography", "topography"],
	["Soil Texture", "soil_texture"],
	["Soil Color", "soil_color"],
	["Drainage", "drainage"],
	["Stoniness", "stoniness"],
	["Diseases and Pests", "diseases_and_pests"],
	["Remarks", "remarks"],
	["Cultural Practice", "cultural_practice"],
];

const availabilityFields = [
	["Status of Harvest", "status_of_harvest"],
	["Characterized", "characterized"],
	["Field", "field"],
];

function Row({ label, value }) {
	const hasValue = value !== null && value !== undefined && String(value).trim() !== "";
	const displayValue = hasValue ? String(value) : "-";

	return (
		<div className="rounded-md border px-3 py-2 text-sm">
			<p className="text-muted-foreground text-xs">{label}</p>
			<p className="font-medium">{displayValue}</p>
		</div>
	);
}

function booleanDisplay(value) {
	if (value === null || value === undefined) {
		return "-";
	}
	return value ? "Yes" : "No";
}

function renderRows(fieldMap, data) {
	return fieldMap.map(([label, key]) => (
		<Row key={key} label={label} value={data?.[key]} />
	));
}

export default function ViewPassportData({ open, onOpenChange, data }) {
	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-hidden p-0">
				<div className="p-6 pb-0">
					<DialogHeader>
						<DialogTitle>View Passport Data</DialogTitle>
						<DialogDescription>
							Review passport data details by section.
						</DialogDescription>
					</DialogHeader>
				</div>

				<div className="px-6 pt-4 pb-2 border-b flex justify-end gap-2">
					<Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
						Close
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

						<TabsContent value="passport-data" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							{renderRows(passportDataFields, data)}
						</TabsContent>

						<TabsContent value="crop" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							{renderRows(cropFields, data)}
						</TabsContent>

						<TabsContent value="location" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							{renderRows(locationFields, data)}
						</TabsContent>

						<TabsContent value="donor" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							{renderRows(donorFields, data)}
						</TabsContent>

						<TabsContent value="topography" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2 max-h-[52vh] overflow-y-auto">
							{renderRows(topographyFields, data)}
							<Row label="Herbarium Specimen" value={booleanDisplay(data?.herbarium_specimen)} />
						</TabsContent>

						<TabsContent value="availability" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							<Row label="Available in Field" value={booleanDisplay(data?.available_in_the_field)} />
							<Row label="Available in Vitro" value={booleanDisplay(data?.available_at_in_vitro)} />
							<Row label="For Distribution" value={booleanDisplay(data?.available_for_distribution)} />
							{renderRows(availabilityFields, data)}
						</TabsContent>

						<TabsContent value="photo" className="mt-4 rounded-md border p-4 grid gap-3 md:grid-cols-2">
							<Row label="Photo Name" value={data?.photo_name} />
							<Row label="Photos" value={data?.photo_count ? `${data.photo_count} file(s)` : "-"} />

							<div className="md:col-span-2 space-y-3">
								<p className="text-sm font-medium">Images</p>
								{Array.isArray(data?.photos) && data.photos.length > 0 ? (
									<div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
										{data.photos.map((photo, index) => (
											<a
												key={photo.id ?? `photo-${index}`}
												href={photo.url || "#"}
												target="_blank"
												rel="noreferrer"
												className={`rounded-md border p-2 ${photo.url ? "hover:border-primary" : "opacity-60 cursor-not-allowed"}`}
												onClick={(event) => {
													if (!photo.url) {
														event.preventDefault();
													}
												}}
											>
												{photo.url ? (
													<img
														src={photo.url}
														alt={photo.photo_name || `Passport photo ${index + 1}`}
														className="h-24 w-full object-cover rounded"
													/>
												) : (
													<div className="h-24 w-full rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
														No image file
													</div>
												)}
												<p className="mt-2 text-xs truncate">{photo.photo_name || `Photo ${index + 1}`}</p>
											</a>
										))}
									</div>
								) : (
									<p className="text-sm text-muted-foreground">No photos available.</p>
								)}
							</div>
						</TabsContent>

						<TabsContent value="usage-information" className="mt-4 rounded-md border p-4 space-y-3 max-h-[52vh] overflow-y-auto">
							{Array.isArray(data?.usages) && data.usages.length > 0 ? (
								data.usages.map((usage, index) => (
									<div key={`usage-${index}`} className="rounded-md border p-3">
										<Row label="Plant Part" value={usage.plant_part} />
										<Row label="Usage Description" value={usage.usage_description} />
									</div>
								))
							) : (
								<p className="text-sm text-muted-foreground">No usage information.</p>
							)}
						</TabsContent>
					</Tabs>
				</div>
			</DialogContent>
		</Dialog>
	);
}
