"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import PassportDataModals from "@/components/modals/PassportDataModals";
import ViewPassportData from "@/components/modals/ViewPassportData";
import EditPassportData from "@/components/modals/EditPassportData";
import ImportPassportData from "@/components/modals/ImportPassportData";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";

const ROWS_PER_PAGE = 25;

type PassportRow = {
	id?: number;
	gb_number?: string | null;
	accession_number?: string | null;
	collection_number?: string | null;
	crop_group?: string | null;
	crop_name?: string | null;
	genus?: string | null;
	species?: string | null;
	country?: string | null;
	province?: string | null;
	usages?: Array<{ plant_part?: string | null; usage_description?: string | null }>;
	usage_rows?: Array<{ plant_part?: string | null; usage_description?: string | null }>;
	photos?: Array<{ id?: number; photo_name?: string | null; url?: string | null }>;
	[key: string]: unknown;
};

export default function PassportDataPage() {
	const [rows, setRows] = useState<PassportRow[]>([]);
	const [currentPage, setCurrentPage] = useState(1);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(1);
	const [viewOpen, setViewOpen] = useState(false);
	const [editOpen, setEditOpen] = useState(false);
	const [selectedRow, setSelectedRow] = useState<PassportRow | null>(null);
	const [editForm, setEditForm] = useState<PassportRow | null>(null);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const columns = [
		"GB No",
		"Accession",
		"Collection",
		"Crop Group",
		"Crop Name",
		"Genus",
		"Species",
		"Country",
		"Province",
		"Action",
	];

	const fetchPassports = useCallback(async (page = 1) => {
		if (!API_BASE) {
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/passport-data/list/?page=${page}&page_size=${ROWS_PER_PAGE}`);
			const data = await response.json();
			if (response.ok && data?.success && Array.isArray(data.passports)) {
				setRows(data.passports);
				const pagination = data.pagination || {};
				setTotalCount(typeof pagination.total === "number" ? pagination.total : data.passports.length);
				setTotalPages(typeof pagination.total_pages === "number" ? Math.max(1, pagination.total_pages) : 1);
				setCurrentPage(typeof pagination.current_page === "number" ? pagination.current_page : page);
				return;
			}

			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
		} catch {
			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
		}
	}, [API_BASE]);

	const fetchPassportDetail = useCallback(async (id?: number) => {
		if (!API_BASE || id === undefined) {
			return null;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/passport-data/${id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.passport) {
				return data.passport as PassportRow;
			}
		} catch {
			return null;
		}

		return null;
	}, [API_BASE]);

	const handleCreated = async (passport: PassportRow) => {
		setCurrentPage(1);
		await fetchPassports(1);
	};

	const handleImported = async () => {
		setCurrentPage(1);
		await fetchPassports(1);
	};

	const handleOpenView = async (row: PassportRow) => {
		const detailedRow = await fetchPassportDetail(typeof row.id === "number" ? row.id : undefined);
		setSelectedRow(detailedRow || row);
		setViewOpen(true);
	};

	const handleOpenEdit = async (row: PassportRow) => {
		const detailedRow = await fetchPassportDetail(typeof row.id === "number" ? row.id : undefined);
		const sourceRow = detailedRow || row;

		const usageRows = Array.isArray(sourceRow.usages) && sourceRow.usages.length > 0
			? sourceRow.usages.map((usage: any) => ({
				plant_part: usage.plant_part ?? "",
				usage_description: usage.usage_description ?? "",
			}))
			: [{ plant_part: "", usage_description: "" }];

		setSelectedRow(sourceRow);
		setEditForm({ ...sourceRow, usage_rows: usageRows });
		setEditOpen(true);
	};

	const handleSaveEdit = () => {
		if (!editForm) {
			return;
		}

		const updatedRow: PassportRow = {
			...editForm,
			usages: Array.isArray(editForm.usage_rows)
				? editForm.usage_rows.map((usage: any) => ({
					plant_part: usage.plant_part ?? "",
					usage_description: usage.usage_description ?? "",
				}))
				: [],
		};

		setRows((prev) => {
			if (updatedRow.id !== undefined) {
				return prev.map((item) => (item.id === updatedRow.id ? { ...item, ...updatedRow } : item));
			}

			return prev.map((item) => (item === selectedRow ? { ...item, ...updatedRow } : item));
		});

		setEditOpen(false);
		setSelectedRow(updatedRow);
	};

	useEffect(() => {
		fetchPassports(currentPage);
	}, [currentPage, fetchPassports]);

	const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * ROWS_PER_PAGE + 1;
	const endEntry = totalCount === 0 ? 0 : Math.min((currentPage - 1) * ROWS_PER_PAGE + rows.length, totalCount);

	return (
		<main className="min-h-screen bg-background">
			<div className="flex min-h-screen">
				<Sidebar />

				<div className="flex-1 p-6 md:p-10">
					<div className="mx-auto max-w-7xl space-y-4">
						<div className="flex flex-wrap items-center justify-between gap-3">
							<h1 className="text-2xl font-semibold tracking-tight">Passport Data</h1>

							<div className="flex items-center gap-2">
								<PassportDataModals onCreated={handleCreated} />
								<ImportPassportData onImported={handleImported} />
							</div>
						</div>

						<div className="overflow-x-auto rounded-lg border">
							<table className="w-full min-w-[900px] text-sm">
								<thead className="bg-muted/60">
									<tr>
										{columns.map((column) => (
											<th key={column} className="px-4 py-3 text-left font-semibold text-foreground">
												{column}
											</th>
										))}
									</tr>
								</thead>

								<tbody>
									{rows.length > 0 ? (
										rows.map((row, index) => (
											<tr key={`${row.id ?? "new"}-${index}`} className="border-t">
												<td className="px-4 py-3">{row.gb_number || "-"}</td>
												<td className="px-4 py-3">{row.accession_number || "-"}</td>
												<td className="px-4 py-3">{row.collection_number || "-"}</td>
												<td className="px-4 py-3">{row.crop_group || "-"}</td>
												<td className="px-4 py-3">{row.crop_name || "-"}</td>
												<td className="px-4 py-3">{row.genus || "-"}</td>
												<td className="px-4 py-3">{row.species || "-"}</td>
												<td className="px-4 py-3">{row.country || "-"}</td>
												<td className="px-4 py-3">{row.province || "-"}</td>
												<td className="px-4 py-3">
													<div className="flex items-center gap-2">
														<Button type="button" size="sm" variant="outline" onClick={() => handleOpenView(row)}>
															View
														</Button>
														<Button type="button" size="sm" onClick={() => handleOpenEdit(row)}>
															Edit
														</Button>
													</div>
												</td>
											</tr>
										))
									) : (
										<tr className="border-t">
											<td colSpan={10} className="px-4 py-8 text-center text-muted-foreground">
												No passport records yet.
											</td>
										</tr>
									)}
								</tbody>
							</table>
						</div>

						<div className="flex flex-wrap items-center justify-between gap-3">
							<p className="text-sm text-muted-foreground">
								Showing {startEntry}-{endEntry} of {totalCount} records
							</p>
							<div className="flex items-center gap-2">
								<Button
									type="button"
									variant="outline"
									onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
									disabled={currentPage === 1}
								>
									Previous
								</Button>
								<span className="text-sm text-muted-foreground">
									Page {currentPage} of {totalPages}
								</span>
								<Button
									type="button"
									variant="outline"
									onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
									disabled={currentPage >= totalPages}
								>
									Next
								</Button>
							</div>
						</div>

						<ViewPassportData open={viewOpen} onOpenChange={setViewOpen} data={selectedRow} />

						<EditPassportData
							open={editOpen}
							onOpenChange={setEditOpen}
							form={editForm}
							onChange={setEditForm}
							onSave={handleSaveEdit}
						/>
					</div>
				</div>
			</div>
		</main>
	);
}

