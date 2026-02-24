/**
 * Client-side storage for inspection results.
 * Uses sessionStorage so results persist across navigation but not browser close.
 * TODO: Replace with API persistence when backend supports it.
 */

export type InspectionResult = {
    id: string;
    imageUrl: string;
    response: string;
    model?: string;
    inferenceTimeMs?: number;
    timestamp: string;
    projectId?: string;
    projectName?: string;
};

const STORAGE_KEY = "glados:inspections";

function getStore(): Record<string, InspectionResult> {
    if (typeof window === "undefined") return {};
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        return {};
    }
}

function setStore(store: Record<string, InspectionResult>) {
    if (typeof window === "undefined") return;
    try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    } catch {
        // ignore quota errors
    }
}

const INSPECTION_UPDATE_EVENT = "glados:inspections-updated";

export function saveInspection(result: Omit<InspectionResult, "id">): string {
    const id = `insp-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    const store = getStore();
    store[id] = { ...result, id };
    setStore(store);
    if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
    }
    return id;
}

export { INSPECTION_UPDATE_EVENT };

export function getInspection(id: string): InspectionResult | null {
    const store = getStore();
    return store[id] ?? null;
}

export function getAllInspections(): InspectionResult[] {
    const store = getStore();
    return Object.values(store).sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
}

export function deriveStatus(response: string): "pass" | "fail" {
    const lower = response.toLowerCase();
    if (
        lower.includes("no fod") ||
        lower.includes("no foreign object") ||
        lower.includes("no debris") ||
        lower.includes("clear") ||
        lower.includes("no visible") ||
        lower.includes("no defect")
    ) {
        return "pass";
    }
    if (
        lower.includes("fod") ||
        lower.includes("foreign object") ||
        lower.includes("debris") ||
        lower.includes("defect") ||
        lower.includes("item") ||
        lower.includes("found")
    ) {
        return "fail";
    }
    return "fail";
}
