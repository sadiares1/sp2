"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import AddProduct from "@/components/modals/AddProduct";
import EditProduct from "@/components/modals/EditProduct";
import ViewProduct from "@/components/modals/ViewProduct";
import { apiFetch } from "@/lib/api";

const ROWS_PER_PAGE = 25;

type ProductRow = {
	id?: number;
	cropName?: string | null;
	material?: string | null;
	gbNumber?: string | null;
	accessionNumber?: string | null;
	description?: string | null;
	unitPrice?: string | null;
	remarks?: string | null;
};

export default function ProductsPage() {
	const [rows, setRows] = useState<ProductRow[]>([]);
	const [currentPage, setCurrentPage] = useState(1);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(1);
	const [viewOpen, setViewOpen] = useState(false);
	const [editOpen, setEditOpen] = useState(false);
	const [selectedProduct, setSelectedProduct] = useState<ProductRow | null>(null);
	const API_BASE = process.env.NEXT_PUBLIC_API_URL;

	const columns = ["Crop", "Material", "GB Number", "Accession Number", "Unit Price", "Action"];

	const fetchProducts = useCallback(async (page = 1) => {
		if (!API_BASE) {
			setRows([]);
			setTotalCount(0);
			setTotalPages(1);
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/list/?page=${page}&page_size=${ROWS_PER_PAGE}`);
			const data = await response.json();

			if (response.ok && data?.success && Array.isArray(data.products)) {
				setRows(data.products);
				const pagination = data.pagination || {};
				setTotalCount(typeof pagination.total === "number" ? pagination.total : data.products.length);
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

	const handleAddProduct = async (form: {
		material: string;
		gbNumber: string;
		accessionNumber: string;
		description: string;
		unitPrice: string;
		remarks: string;
	}) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/create/`, {
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
				return { success: false, message: data?.message || "Failed to add product." };
			}

			setCurrentPage(1);
			await fetchProducts(1);
			return { success: true, message: "" };
		} catch {
			return { success: false, message: "Unable to connect to the server." };
		}
	};

	const handleOpenEdit = async (row: ProductRow) => {
		if (!API_BASE || !row.id) {
			setSelectedProduct(row);
			setEditOpen(true);
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/${row.id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.product) {
				setSelectedProduct(data.product);
				setEditOpen(true);
				return;
			}
		} catch {
			setSelectedProduct(row);
			setEditOpen(true);
			return;
		}

		setSelectedProduct(row);
		setEditOpen(true);
	};

	const handleOpenView = async (row: ProductRow) => {
		if (!API_BASE || !row.id) {
			setSelectedProduct(row);
			setViewOpen(true);
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/${row.id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.product) {
				setSelectedProduct(data.product);
				setViewOpen(true);
				return;
			}
		} catch {
			setSelectedProduct(row);
			setViewOpen(true);
			return;
		}

		setSelectedProduct(row);
		setViewOpen(true);
	};

	const handleRefreshViewDetail = useCallback(async () => {
		if (!API_BASE || !selectedProduct?.id) {
			return;
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/${selectedProduct.id}/`);
			const data = await response.json();
			if (response.ok && data?.success && data?.product) {
				setSelectedProduct(data.product);
			}
		} catch {
			return;
		}
	}, [API_BASE, selectedProduct?.id]);

	const handleSaveEdit = async (
		id: number,
		form: {
			material: string;
			gbNumber: string;
			accessionNumber: string;
			description: string;
			unitPrice: string;
			remarks: string;
		}
	) => {
		if (!API_BASE) {
			return { success: false, message: "API base URL is not configured." };
		}

		try {
			const response = await apiFetch(`${API_BASE}/api/product/${id}/update/`, {
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
				return { success: false, message: data?.message || "Failed to update product." };
			}

			setRows((prev) =>
				prev.map((item) => (item.id === id ? { ...item, ...(data.product || form) } : item))
			);

			return { success: true, message: "" };
		} catch {
			return { success: false, message: "Unable to connect to the server." };
		}
	};

	useEffect(() => {
		fetchProducts(currentPage);
	}, [currentPage, fetchProducts]);

	const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * ROWS_PER_PAGE + 1;
	const endEntry = totalCount === 0 ? 0 : Math.min((currentPage - 1) * ROWS_PER_PAGE + rows.length, totalCount);

	return (
		<main className="min-h-screen bg-background">
			<div className="flex min-h-screen">
				<Sidebar />

				<div className="flex-1 p-6 md:p-10">
					<div className="mx-auto max-w-7xl space-y-4">
						<div className="flex flex-wrap items-center justify-between gap-3">
							<h1 className="text-2xl font-semibold tracking-tight">Products</h1>
							<AddProduct onSave={handleAddProduct} />
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
											<tr key={`${row.id ?? "product"}-${index}`} className="border-t">
												<td className="px-4 py-3">{row.cropName || "-"}</td>
												<td className="px-4 py-3">{row.material || "-"}</td>
												<td className="px-4 py-3">{row.gbNumber || "-"}</td>
												<td className="px-4 py-3">{row.accessionNumber || "-"}</td>
												<td className="px-4 py-3">{row.unitPrice || "-"}</td>
												<td className="px-4 py-3">
													<div className="flex items-center gap-2">
														<Button type="button" size="sm" variant="outline" onClick={() => handleOpenView(row)}>View</Button>
														<Button type="button" size="sm" onClick={() => handleOpenEdit(row)}>Edit</Button>
													</div>
												</td>
											</tr>
										))
									) : (
										<tr className="border-t">
											<td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
												No product records yet.
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

						<EditProduct
							open={editOpen}
							onOpenChange={setEditOpen}
							data={selectedProduct}
							onSave={handleSaveEdit}
						/>

						<ViewProduct
							open={viewOpen}
							onOpenChange={setViewOpen}
							data={selectedProduct}
							onRefresh={handleRefreshViewDetail}
						/>
					</div>
				</div>
			</div>
		</main>
	);
}
