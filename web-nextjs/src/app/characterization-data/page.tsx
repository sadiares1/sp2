"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import ViewCharacteristic from "@/components/modals/ViewCharacteristic";
import EditCharacteristic from "@/components/modals/EditCharacteristic";
import AddCharacteristic from "@/components/modals/AddCharacteristic";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";

const ROWS_PER_PAGE = 25;

type CharacterizationRow = {
	id?: number;
	passport_id?: number | null;
	source_model?: string | null;
	source_id?: number | null;
	accession_number?: string | null;
	gb_number?: string | null;
	old_accession_number?: string | null;
	crop_name?: string | null;
	genus?: string | null;
	species?: string | null;
	country?: string | null;
	province?: string | null;
	nearest_town?: string | null;
	barangay?: string | null;
};

type CharacteristicDetail = {
	id?: number;
	source_model?: string | null;
	source_id?: number | null;
	crop_name?: string | null;
	passport?: {
		id?: number | null;
		accession_number?: string | null;
		gb_number?: string | null;
		old_accession_number?: string | null;
	};
	fields?: Array<{ name?: string; label?: string; value?: string | null }>;
};

export default function CharacterizationDataPage() {
	const [rows, setRows] = useState<CharacterizationRow[]>([]);
	const [currentPage, setCurrentPage] = useState(1);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(1);
	const [viewOpen, setViewOpen] = useState(false);
	const [editOpen, setEditOpen] = useState(false);
	const [selectedCharacteristic, setSelectedCharacteristic] = useState<CharacteristicDetail | null>(null);
	const [editCharacteristic, setEditCharacteristic] = useState<CharacteristicDetail | null>(null);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const columns = [
		"Accession Number",
		"GB Number",
		"Old Accession Number",
		"Crop",
		"Genus",
		"Species",
		"Location",
		"Action",
	];

	const fetchRows = useCallback(async (page = 1) => {
		if (!API_BASE) {
			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/characterization-data/list/?page=${page}&page_size=${ROWS_PER_PAGE}`);
			const data = await response.json();

			if (response.ok && data?.success && Array.isArray(data.characterizations)) {
				setRows(data.characterizations);
				const pagination = data.pagination || {};
				setTotalCount(typeof pagination.total === "number" ? pagination.total : data.characterizations.length);
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

	const fetchCharacteristicDetail = useCallback(async (compiledId?: number) => {
		if (!API_BASE || !compiledId) {
			return null;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/characterization-data/${compiledId}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.characteristic) {
				return data.characteristic as CharacteristicDetail;
			}
		} catch {
			return null;
		}

		return null;
	}, [API_BASE]);

	const handleOpenView = async (row: CharacterizationRow) => {
		const detail = await fetchCharacteristicDetail(row.id);
		if (!detail) {
			return;
		}
		setSelectedCharacteristic(detail);
		setViewOpen(true);
	};

	const handleOpenEdit = async (row: CharacterizationRow) => {
		const detail = await fetchCharacteristicDetail(row.id);
		if (!detail) {
			return;
		}
		setEditCharacteristic(detail);
		setEditOpen(true);
	};

	const handleSaveEdit = async (compiledId: number, formValues: Record<string, unknown>, photoFile?: File | null) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const formData = new FormData();
			Object.entries(formValues).forEach(([key, value]) => {
				formData.append(key, value === null || value === undefined ? "" : String(value));
			});
			if (photoFile) {
				formData.append("photo", photoFile);
			}

			const response = await apiFetch(`${API_BASE}/api/characterization-data/${compiledId}/update/`, {
				method: "PATCH",
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
				return { success: false, message: data?.message || "Failed to update characteristic." };
			}

			const refreshed = await fetchCharacteristicDetail(compiledId);
			if (refreshed) {
				setEditCharacteristic(refreshed);
				if (viewOpen) {
					setSelectedCharacteristic(refreshed);
				}
			}

			await fetchRows(currentPage);
			return { success: true };
		} catch {
			return { success: false, message: "Unable to connect to server." };
		}
	};

	const getLocationDisplay = (row: CharacterizationRow) => {
		const parts = [row.country, row.province, row.nearest_town, row.barangay]
			.filter((part) => typeof part === "string" && part.trim().length > 0)
			.map((part) => part?.trim());
		return parts.length > 0 ? parts.join(", ") : "-";
	};

	useEffect(() => {
		fetchRows(currentPage);
	}, [currentPage, fetchRows]);

	const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * ROWS_PER_PAGE + 1;
	const endEntry = totalCount === 0 ? 0 : Math.min((currentPage - 1) * ROWS_PER_PAGE + rows.length, totalCount);

	const handleImported = async () => {
		setCurrentPage(1);
		await fetchRows(1);
	};

	return (
		<main className="min-h-screen bg-background">
			<div className="flex min-h-screen">
				<Sidebar />

				<div className="flex-1 p-6 md:p-10">
					<div className="mx-auto max-w-7xl space-y-4">
						<div className="flex flex-wrap items-center justify-between gap-3">
							<h1 className="text-2xl font-semibold tracking-tight">Characterization Data</h1>
							<AddCharacteristic onImported={handleImported} />
						</div>

						<div className="overflow-x-auto rounded-lg border">
							<table className="w-full min-w-[1000px] text-sm">
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
											<tr key={`${row.id ?? "characterization"}-${index}`} className="border-t">
												<td className="px-4 py-3">{row.accession_number || "-"}</td>
												<td className="px-4 py-3">{row.gb_number || "-"}</td>
												<td className="px-4 py-3">{row.old_accession_number || "-"}</td>
												<td className="px-4 py-3">{row.crop_name || "-"}</td>
												<td className="px-4 py-3">{row.genus || "-"}</td>
												<td className="px-4 py-3">{row.species || "-"}</td>
												<td className="px-4 py-3">{getLocationDisplay(row)}</td>
												<td className="px-4 py-3">
													<div className="flex items-center gap-2">
														<Button
															type="button"
															size="sm"
															variant="outline"
															onClick={() => handleOpenView(row)}
															disabled={!row.id}
														>
															View
														</Button>
														<Button
															type="button"
															size="sm"
															onClick={() => handleOpenEdit(row)}
															disabled={!row.passport_id}
														>
															Edit
														</Button>
													</div>
												</td>
											</tr>
										))
									) : (
										<tr className="border-t">
											<td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
												No characterization records yet.
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

						<ViewCharacteristic open={viewOpen} onOpenChange={setViewOpen} data={selectedCharacteristic} />

						<EditCharacteristic
							open={editOpen}
							onOpenChange={setEditOpen}
							data={editCharacteristic}
							onSave={handleSaveEdit}
						/>
					</div>
				</div>
			</div>
		</main>
	);
}
