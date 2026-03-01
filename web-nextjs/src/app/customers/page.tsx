"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import AddCustomer from "@/components/modals/AddCustomer";
import EditCustomer from "@/components/modals/EditCustomer";

const ROWS_PER_PAGE = 25;

type CustomerRow = {
	id?: number;
	customerName?: string | null;
	designation?: string | null;
	office?: string | null;
	contactInfo?: string | null;
	emailAddress?: string | null;
};

export default function CustomersPage() {
	const [rows, setRows] = useState<CustomerRow[]>([]);
	const [currentPage, setCurrentPage] = useState(1);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(1);
	const [editOpen, setEditOpen] = useState(false);
	const [selectedCustomer, setSelectedCustomer] = useState<CustomerRow | null>(null);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const columns = ["Name", "Designation", "Office", "Contact", "Email", "Action"];

	const fetchCustomers = useCallback(async (page = 1) => {
		if (!API_BASE) {
			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
			return;
		}

		try {
			const response = await fetch(`${API_BASE}/api/customer/list/?page=${page}&page_size=${ROWS_PER_PAGE}`);
			const data = await response.json();

			if (response.ok && data?.success && Array.isArray(data.customers)) {
				setRows(data.customers);
				const pagination = data.pagination || {};
				setTotalCount(typeof pagination.total === "number" ? pagination.total : data.customers.length);
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

	const handleAddCustomer = async (form: {
		customerName: string;
		designation: string;
		office: string;
		contactInfo: string;
		emailAddress: string;
	}) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const response = await fetch(`${API_BASE}/api/customer/create/`, {
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
				return { success: false, message: data?.message || "Failed to add customer." };
			}

			setCurrentPage(1);
			await fetchCustomers(1);
			return { success: true, message: "" };
		} catch {
			return { success: false, message: "Unable to connect to the server." };
		}
	};

	const handleOpenEdit = async (row: CustomerRow) => {
		if (!API_BASE || !row.id) {
			setSelectedCustomer(row);
			setEditOpen(true);
			return;
		}

		try {
			const response = await fetch(`${API_BASE}/api/customer/${row.id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.customer) {
				setSelectedCustomer(data.customer);
				setEditOpen(true);
				return;
			}
		} catch {
			setSelectedCustomer(row);
			setEditOpen(true);
			return;
		}

		setSelectedCustomer(row);
		setEditOpen(true);
	};

	const handleSaveEdit = async (
		id: number,
		form: {
			customerName: string;
			designation: string;
			office: string;
			contactInfo: string;
			emailAddress: string;
		}
	) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const response = await fetch(`${API_BASE}/api/customer/${id}/update/`, {
				method: "PATCH",
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
				return { success: false, message: data?.message || "Failed to update customer." };
			}

			setRows((prev) =>
				prev.map((item) => (item.id === id ? { ...item, ...(data.customer || form) } : item))
			);

			return { success: true, message: "" };
		} catch {
			return { success: false, message: "Unable to connect to the server." };
		}
	};

	useEffect(() => {
		fetchCustomers(currentPage);
	}, [currentPage, fetchCustomers]);

	const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * ROWS_PER_PAGE + 1;
	const endEntry = totalCount === 0 ? 0 : Math.min((currentPage - 1) * ROWS_PER_PAGE + rows.length, totalCount);

	return (
		<main className="min-h-screen bg-background">
			<div className="flex min-h-screen">
				<Sidebar />

				<div className="flex-1 p-6 md:p-10">
					<div className="mx-auto max-w-7xl space-y-4">
						<div className="flex flex-wrap items-center justify-between gap-3">
							<h1 className="text-2xl font-semibold tracking-tight">Customers</h1>
							<AddCustomer onSave={handleAddCustomer} />
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
											<tr key={`${row.id ?? "customer"}-${index}`} className="border-t">
												<td className="px-4 py-3">{row.customerName || "-"}</td>
												<td className="px-4 py-3">{row.designation || "-"}</td>
												<td className="px-4 py-3">{row.office || "-"}</td>
												<td className="px-4 py-3">{row.contactInfo || "-"}</td>
												<td className="px-4 py-3">{row.emailAddress || "-"}</td>
												<td className="px-4 py-3">
													<div className="flex items-center gap-2">
														<Button type="button" size="sm" onClick={() => handleOpenEdit(row)}>Edit</Button>
													</div>
												</td>
											</tr>
										))
									) : (
										<tr className="border-t">
											<td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
												No customer records yet.
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

						<EditCustomer
							open={editOpen}
							onOpenChange={setEditOpen}
							data={selectedCustomer}
							onSave={handleSaveEdit}
						/>
					</div>
				</div>
			</div>
		</main>
	);
}
