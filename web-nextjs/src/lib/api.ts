export function getCookie(name: string): string {
	if (typeof document === "undefined") return "";
	const target = `${name}=`;
	const parts = document.cookie.split(";");
	for (const part of parts) {
		const value = part.trim();
		if (value.startsWith(target)) {
			return decodeURIComponent(value.slice(target.length));
		}
	}
	return "";
}

type ApiFetchOptions = RequestInit & {
	skipAuthRedirect?: boolean;
};

function handleAuthExpired() {
	if (typeof window === "undefined") return;
	localStorage.removeItem("authUser");
	document.cookie = "auth_logged_in=; path=/; max-age=0; SameSite=Lax";
	document.cookie = "auth_role=; path=/; max-age=0; SameSite=Lax";
	window.location.href = "/";
}

function normalizeLocalApiUrl(input: RequestInfo | URL): RequestInfo | URL {
	if (typeof window === "undefined") return input;
	if (typeof input !== "string") return input;

	try {
		const url = new URL(input);
		const currentHost = window.location.hostname;
		const isLocalApiHost = url.hostname === "localhost" || url.hostname === "127.0.0.1";
		const isLocalPageHost = currentHost === "localhost" || currentHost === "127.0.0.1";

		if (isLocalApiHost && isLocalPageHost && url.hostname !== currentHost) {
			url.hostname = currentHost;
			return url.toString();
		}
	} catch {
		return input;
	}

	return input;
}

export async function apiFetch(input: RequestInfo | URL, init: ApiFetchOptions = {}) {
	const { skipAuthRedirect = false, ...requestInit } = init;
	const method = (init.method || "GET").toUpperCase();
	const headers = new Headers(requestInit.headers || {});
	const csrfToken = getCookie("csrftoken");
	const needsCsrf = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method);
	const normalizedInput = normalizeLocalApiUrl(input);

	if (needsCsrf && csrfToken && !headers.has("X-CSRFToken")) {
		headers.set("X-CSRFToken", csrfToken);
	}

	const response = await fetch(normalizedInput, {
		credentials: "include",
		...requestInit,
		headers,
	});

	if (!skipAuthRedirect && (response.status === 401 || response.status === 403)) {
		handleAuthExpired();
	}

	return response;
}
