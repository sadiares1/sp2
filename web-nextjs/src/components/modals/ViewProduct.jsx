"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AddStockMovement from "@/components/modals/AddStockMovement";

function toDisplay(value) {
	if (value === null || value === undefined || value === "") return "N/A";
	return String(value);
}

function formatDateTime(value) {
	if (!value) return "N/A";
	const parsed = new Date(value);
	if (Number.isNaN(parsed.getTime())) return "N/A";
	return parsed.toLocaleString();
}

function DisplayField({ label, value }) {
	return (
		<div className="rounded-md border p-3">
			<p className="text-xs font-medium text-muted-foreground">{label}</p>
			<p className="mt-1 text-sm">{toDisplay(value)}</p>
		</div>
	);
}

function MovementList({ records, emptyText }) {
	if (!Array.isArray(records) || records.length === 0) {
		return <p className="rounded-md border p-3 text-sm text-muted-foreground">{emptyText}</p>;
	}

	return (
		<div className="space-y-2">
			{records.map((item) => (
				<div key={item.id} className="rounded-md border p-3">
					<div className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
						<p><span className="font-medium">Quantity:</span> {toDisplay(item.quantity)}</p>
						<p><span className="font-medium">Unit:</span> {toDisplay(item.unit)}</p>
						<p><span className="font-medium">Movement Date:</span> {toDisplay(item.movementDate)}</p>
						<p><span className="font-medium">Location:</span> {toDisplay(item.location)}</p>
						<p><span className="font-medium">Shelf No:</span> {toDisplay(item.shelfNo)}</p>
						<p><span className="font-medium">Tray No:</span> {toDisplay(item.trayNo)}</p>
						<p><span className="font-medium">Bottle No:</span> {toDisplay(item.bottleNo)}</p>
						<p><span className="font-medium">Packet No:</span> {toDisplay(item.packetNo)}</p>
						<p><span className="font-medium">Active Base:</span> {toDisplay(item.activeBase)}</p>
						<p><span className="font-medium">Batch Reference:</span> {toDisplay(item.batchReference)}</p>
						<p><span className="font-medium">Poll Type:</span> {toDisplay(item.pollType)}</p>
						<p><span className="font-medium">Remarks:</span> {toDisplay(item.remarks)}</p>
					</div>
				</div>
			))}
		</div>
	);
}

export default function ViewProduct({ open, onOpenChange, data, onRefresh = async () => {} }) {
	const [addStockOpen, setAddStockOpen] = useState(false);
	const passport = data?.passportData || null;
	const createdByName = data?.createdBy?.fullName || data?.createdBy?.username;
	const acquisitionRecords = data?.stockMovements?.acquisition || [];
	const disposalRecords = data?.stockMovements?.disposal || [];
	const stockTakeRecords = data?.stockMovements?.stockTakes || [];
	const distributionRecords = data?.stockMovements?.distribution || [];

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-2xl">
				<DialogHeader>
					<DialogTitle>Product Details</DialogTitle>
					<DialogDescription>View product information and linked passport details.</DialogDescription>
				</DialogHeader>

				<div className={addStockOpen ? "hidden" : "block"}>
				<Tabs defaultValue="basic" className="w-full">
					<TabsList className="w-full justify-start overflow-x-auto h-auto p-1">
						<TabsTrigger value="basic" className="shrink-0">Basic</TabsTrigger>
						<TabsTrigger value="passport" className="shrink-0">Passport</TabsTrigger>
						<TabsTrigger value="additional" className="shrink-0">Additional</TabsTrigger>
						<TabsTrigger value="stock-movements" className="shrink-0">Stock & Movements</TabsTrigger>
					</TabsList>

					<TabsContent value="basic" className="mt-3 space-y-2">
						<div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
							<DisplayField label="Crop" value={data?.cropName} />
							<DisplayField label="Material" value={data?.material} />
							<DisplayField label="Description" value={data?.description} />
							<DisplayField label="Unit Price" value={data?.unitPrice} />
							<DisplayField label="Remarks" value={data?.remarks} />
						</div>
					</TabsContent>

					<TabsContent value="passport" className="mt-3 space-y-2">
						{passport ? (
							<div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
								<DisplayField label="GB Number" value={passport.gbNumber || data?.gbNumber} />
								<DisplayField label="Accession Number" value={passport.accessionNumber || data?.accessionNumber} />
								<DisplayField label="Genus" value={passport.genus || data?.genus} />
								<DisplayField label="Species" value={passport.species || data?.species} />
							</div>
						) : (
							<p className="rounded-md border p-3 text-sm text-muted-foreground">
								No passport data available for this product.
							</p>
						)}
					</TabsContent>

					<TabsContent value="additional" className="mt-3 space-y-2">
						<div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
							<DisplayField label="Created By" value={createdByName} />
							<DisplayField label="Created Date" value={formatDateTime(data?.createdDate)} />
							<DisplayField label="Updated Date" value={formatDateTime(data?.updatedDate)} />
						</div>
					</TabsContent>

					<TabsContent value="stock-movements" className="mt-3 space-y-4">
						<div className="flex justify-end">
							<AddStockMovement
								productId={data?.id}
								onCreated={onRefresh}
								open={addStockOpen}
								onOpenChange={setAddStockOpen}
							/>
						</div>
						<div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
							<DisplayField label="Acquisition" value={data?.cumulativeAcquisition ?? "0"} />
							<DisplayField label="Stock Takes" value={data?.cumulativeStockTakes ?? "0"} />
						</div>
						<p className="rounded-md border p-3 text-sm text-muted-foreground">
							Negative stock indicates data inconsistency. Please review your inventory records.
						</p>

						<div className="space-y-2">
							<h3 className="text-sm font-semibold">Stock Movements - Acquisition</h3>
							<MovementList records={acquisitionRecords} emptyText="No acquisition records found." />
						</div>

						<div className="space-y-2">
							<h3 className="text-sm font-semibold">Stock Movements - Disposal</h3>
							<MovementList records={disposalRecords} emptyText="No disposal records found." />
						</div>

						<div className="space-y-2">
							<h3 className="text-sm font-semibold">Stock Movements - Stock Takes</h3>
							<MovementList records={stockTakeRecords} emptyText="No stock take records found." />
						</div>

						<div className="space-y-2">
							<h3 className="text-sm font-semibold">Stock Movements - Distribution</h3>
							<MovementList records={distributionRecords} emptyText="No distribution records found." />
						</div>
					</TabsContent>
				</Tabs>
				</div>

				<div className="mt-3 flex justify-end">
					<Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
						Close
					</Button>
				</div>
			</DialogContent>
		</Dialog>
	);
}
