/**
 * Client-side storage for inspection results.
 * Uses sessionStorage so results persist across navigation but not browser close.
 * Supports both legacy single-result and new batch (multi-submission) format.
 * TODO: Replace with API persistence when backend supports it.
 */

import { parseDefectsFromResponse, type Defect } from "./defect-parser";

export type { Defect };

export type InspectionSubmission = {
    id: string;
    timestamp: string;
    productPhoto: string;
    photoName: string;
    designSpec: string[];
    status: "pass" | "fail";
    defects: Defect[];
    analysis: string;
    model?: string;
    inferenceTimeMs?: number;
};

export type InspectionResult = {
    id: string;
    imageUrl: string;
    response: string;
    model?: string;
    inferenceTimeMs?: number;
    timestamp: string;
    projectId?: string;
    projectName?: string;
    /** New: batch with multiple submissions */
    submissions?: InspectionSubmission[];
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

/** Save a single inspection (legacy or new batch) */
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

/** Save a batch inspection with multiple submissions */
export function saveInspectionBatch(params: {
    submissions: Omit<InspectionSubmission, "id">[];
    projectId?: string;
    projectName?: string;
    designSpecs: string[];
}): string {
    const id = `batch-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    const subs: InspectionSubmission[] = params.submissions.map((s, i) => ({
        ...s,
        id: `${id}-sub-${i}`,
    }));
    const overallStatus = subs.some((s) => s.status === "fail") ? "fail" : "pass";
    const first = subs[0];
    const result: InspectionResult = {
        id,
        imageUrl: first.productPhoto,
        response: first.analysis,
        model: first.model,
        inferenceTimeMs: first.inferenceTimeMs,
        timestamp: first.timestamp,
        projectId: params.projectId,
        projectName: params.projectName,
        submissions: subs,
    };
    const store = getStore();
    store[id] = result;
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

/** Convert legacy single-result to submission for unified display */
export function toSubmissions(result: InspectionResult): InspectionSubmission[] {
    if (result.submissions && result.submissions.length > 0) {
        return result.submissions;
    }
    const defects = parseDefectsFromResponse(result.response);
    const status = deriveStatus(result.response);
    return [
        {
            id: result.id,
            timestamp: result.timestamp,
            productPhoto: result.imageUrl,
            photoName: "product.png",
            designSpec: [],
            status,
            defects,
            analysis: result.response,
            model: result.model,
            inferenceTimeMs: result.inferenceTimeMs,
        },
    ];
}
