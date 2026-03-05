"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import AddRequest from "@/components/modals/AddRequest";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
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
import { apiFetch } from "@/lib/api";

const ROWS_PER_PAGE = 25;

type RequestRow = {
	id?: number;
	customerName?: string | null;
	cropName?: string | null;
	materialNeeded?: string | null;
	quantity?: string | number | null;
	unit?: string | null;
	requestDate?: string | null;
	status?: string | null;
	approved?: boolean;
	released?: boolean;
	purpose?: string | null;
	supplyName?: string | null;
	projectTitle?: string | null;
	approvedDate?: string | null;
	releasedDate?: string | null;
	quarterReleased?: string | null;
};

function deriveStatus(row: RequestRow) {
	if (row.status && row.status.trim()) return row.status;
	if (row.released) return "Released";
	if (row.approved) return "Approved";
	return "Pending";
}

function deriveProgress(row: RequestRow) {
	const status = deriveStatus(row).toLowerCase();
	if (status === "released") return "100%";
	if (status === "approved") return "50%";
	if (status === "cancelled") return "Cancelled";
	return "0%";
}

export default function RequestsPage() {
	const [rows, setRows] = useState<RequestRow[]>([]);
	const [isAdmin, setIsAdmin] = useState(false);
	const [currentPage, setCurrentPage] = useState(1);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(1);
	const [viewOpen, setViewOpen] = useState(false);
	const [editOpen, setEditOpen] = useState(false);
	const [selectedRequest, setSelectedRequest] = useState<RequestRow | null>(null);
	const [editStatus, setEditStatus] = useState("pending");
	const [approvedDate, setApprovedDate] = useState("");
	const [releasedDate, setReleasedDate] = useState("");
	const [quarterReleased, setQuarterReleased] = useState("");
	const [isSavingEdit, setIsSavingEdit] = useState(false);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	useEffect(() => {
		try {
			const rawUser = localStorage.getItem("authUser");
			if (!rawUser) {
				setIsAdmin(false);
				return;
			}

			const user = JSON.parse(rawUser);
			setIsAdmin(user?.role === "admin");
		} catch {
			setIsAdmin(false);
		}
	}, []);

	const columns = ["Customer", "Crop", "Material", "Quantity", "Request Date", "Status", "Progress", "Action"];

	const fetchRequests = useCallback(async (page = 1) => {
		if (!API_BASE) {
			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/request/list/?page=${page}&page_size=${ROWS_PER_PAGE}`);
			const data = await response.json();
			const list = Array.isArray(data?.requests) ? data.requests : [];

			if (response.ok && data?.success && Array.isArray(list)) {
				setRows(list);
				const pagination = data.pagination || {};
				setTotalCount(typeof pagination.total === "number" ? pagination.total : list.length);
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

	const fetchRequestDetail = useCallback(async (id?: number) => {
		if (!API_BASE || !id) {
			return null;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/request/${id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.request) {
				return data.request as RequestRow;
			}
		} catch {
			return null;
		}

		return null;
	}, [API_BASE]);

	const handleOpenView = async (row: RequestRow) => {
		const detail = await fetchRequestDetail(row.id);
		setSelectedRequest(detail || row);
		setViewOpen(true);
	};

	const handleOpenEdit = async (row: RequestRow) => {
		if (!isAdmin) {
			return;
		}

		const detail = await fetchRequestDetail(row.id);
		const source = detail || row;
		setSelectedRequest(source);
		setEditStatus(deriveStatus(source).toLowerCase());
		setApprovedDate(source.approvedDate || "");
		setReleasedDate(source.releasedDate || "");
		setQuarterReleased(source.quarterReleased || "");
		setEditOpen(true);
	};

	const handleSaveEdit = async () => {
		if (!API_BASE || !selectedRequest?.id) {
			return;
		}

		setIsSavingEdit(true);
		try {
			const response = await apiFetch(`${API_BASE}/api/request/${selectedRequest.id}/update/`, {
				method: "PATCH",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					status: editStatus,
					approvedDate: approvedDate || null,
					releasedDate: releasedDate || null,
					quarterReleased: quarterReleased || null,
				}),
			});

			const raw = await response.text();
			let data = null;
			try {
				data = raw ? JSON.parse(raw) : null;
			} catch {
				data = null;
			}

			if (!response.ok || !data?.success) {
				return;
			}

			setRows((prev) =>
				prev.map((item) =>
					item.id === selectedRequest.id
						? {
							...item,
							status: editStatus.charAt(0).toUpperCase() + editStatus.slice(1),
							approvedDate: approvedDate || null,
							releasedDate: releasedDate || null,
							quarterReleased: quarterReleased || null,
						}
						: item
				)
			);
			setEditOpen(false);
		} catch {
			return;
		} finally {
			setIsSavingEdit(false);
		}
	};

	const handleAddRequest = async (form: {
		customerId: string;
		gbNumber: string;
		purpose: string;
		projectTitle: string;
		useOfMaterials: string;
		supplyName: string;
		quantity: string;
		unit: string;
		sourceAcquisitionId: string;
	}) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/request/create/`, {
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
				return { success: false, message: data?.message || "Failed to add request." };
			}

			setCurrentPage(1);
			await fetchRequests(1);
			return { success: true, message: "" };
		} catch {
			return { success: false, message: "Unable to connect to the server." };
		}
	};

	useEffect(() => {
		fetchRequests(currentPage);
	}, [currentPage, fetchRequests]);

	const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * ROWS_PER_PAGE + 1;
	const endEntry = totalCount === 0 ? 0 : Math.min((currentPage - 1) * ROWS_PER_PAGE + rows.length, totalCount);

	const selectedSummary = useMemo(() => {
		if (!selectedRequest) return [];
		return [
			{ label: "Customer", value: selectedRequest.customerName || "-" },
			{ label: "Crop", value: selectedRequest.cropName || "-" },
			{ label: "Material", value: selectedRequest.materialNeeded || "-" },
			{
				label: "Quantity",
				value: selectedRequest.quantity ? `${selectedRequest.quantity} ${selectedRequest.unit || ""}` : "-",
			},
			{ label: "Purpose", value: selectedRequest.purpose || "-" },
			{ label: "Supply Name", value: selectedRequest.supplyName || "-" },
			{ label: "Status", value: deriveStatus(selectedRequest) },
		];
	}, [selectedRequest]);

	return (
		<main className="min-h-screen bg-background">
			<div className="flex min-h-screen">
				<Sidebar />

				<div className="flex-1 p-6 md:p-10">
					<div className="mx-auto max-w-7xl space-y-4">
						<div className="flex flex-wrap items-center justify-between gap-3">
							<h1 className="text-2xl font-semibold tracking-tight">Requests</h1>
							<AddRequest onSave={handleAddRequest} apiBase={API_BASE} />
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
											<tr key={`${row.id ?? "request"}-${index}`} className="border-t">
												<td className="px-4 py-3">{row.customerName || "-"}</td>
												<td className="px-4 py-3">{row.cropName || "-"}</td>
												<td className="px-4 py-3">{row.materialNeeded || "-"}</td>
												<td className="px-4 py-3">{row.quantity || "-"} {row.unit || ""}</td>
												<td className="px-4 py-3">{row.requestDate || "-"}</td>
												<td className="px-4 py-3">{deriveStatus(row)}</td>
												<td className="px-4 py-3">{deriveProgress(row)}</td>
												<td className="px-4 py-3">
													<div className="flex items-center gap-2">
														<Button type="button" size="sm" variant="outline" onClick={() => handleOpenView(row)}>View</Button>
														{isAdmin ? (
															<Button type="button" size="sm" onClick={() => handleOpenEdit(row)}>Edit</Button>
														) : null}
													</div>
												</td>
											</tr>
										))
									) : (
										<tr className="border-t">
											<td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
												No request records yet.
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

						<Dialog open={viewOpen} onOpenChange={setViewOpen}>
							<DialogContent>
								<DialogHeader>
									<DialogTitle>Request Details</DialogTitle>
									<DialogDescription>View selected request information.</DialogDescription>
								</DialogHeader>
								<div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
									{selectedSummary.map((item) => (
										<div key={item.label} className="space-y-1">
											<p className="text-xs font-medium text-muted-foreground">{item.label}</p>
											<p className="text-sm">{item.value}</p>
										</div>
									))}
								</div>
							</DialogContent>
						</Dialog>

						<Dialog open={editOpen} onOpenChange={setEditOpen}>
							<DialogContent>
								<DialogHeader>
									<DialogTitle>Edit Request Status</DialogTitle>
									<DialogDescription>Update lifecycle fields for the selected request.</DialogDescription>
								</DialogHeader>

								<div className="space-y-4">
									<div className="space-y-2">
										<Label>Status</Label>
										<Select value={editStatus} onValueChange={(value) => setEditStatus(value || "pending")}>
											<SelectTrigger>
												<SelectValue placeholder="Select status" />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="pending">Pending</SelectItem>
												<SelectItem value="approved">Approved</SelectItem>
												<SelectItem value="released">Released</SelectItem>
												<SelectItem value="cancelled">Cancelled</SelectItem>
											</SelectContent>
										</Select>
									</div>

									<div className="space-y-2">
										<Label htmlFor="approved-date">Approved Date</Label>
										<Input
											id="approved-date"
											type="date"
											value={approvedDate}
											onChange={(event) => setApprovedDate(event.target.value)}
										/>
									</div>

									<div className="space-y-2">
										<Label htmlFor="released-date">Released Date</Label>
										<Input
											id="released-date"
											type="date"
											value={releasedDate}
											onChange={(event) => setReleasedDate(event.target.value)}
										/>
									</div>

									<div className="space-y-2">
										<Label htmlFor="quarter-released">Quarter Released</Label>
										<Input
											id="quarter-released"
											placeholder="e.g., Q1"
											value={quarterReleased}
											onChange={(event) => setQuarterReleased(event.target.value)}
										/>
									</div>
								</div>

								<DialogFooter>
									<Button type="button" variant="outline" onClick={() => setEditOpen(false)} disabled={isSavingEdit}>
										Cancel
									</Button>
									<Button type="button" onClick={handleSaveEdit} disabled={isSavingEdit}>
										{isSavingEdit ? "Saving..." : "Save"}
									</Button>
								</DialogFooter>
							</DialogContent>
						</Dialog>
					</div>
				</div>
			</div>
		</main>
	);
}
