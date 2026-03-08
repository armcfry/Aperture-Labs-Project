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
    status: "pass" | "fail" | "pending";
    defects: Defect[];
    analysis: string;
    model?: string;
    inferenceTimeMs?: number;
    /** Base64 PNG with bounding boxes drawn by Qwen2.5-VL grounding (when detected) */
    annotatedImage?: string;
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
    /** When set to "running", entry is a placeholder; progress 0-100. */
    status?: "running" | "complete";
    progress?: number;
};

const STORAGE_KEY = "glados:inspections";

/** In-memory cache for just-saved results so the result page finds them before sessionStorage is fully visible (e.g. after navigation). */
const memoryCache: Record<string, InspectionResult> = {};

function getStore(): Record<string, InspectionResult> {
    if (globalThis.window === undefined) return {};
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        return {};
    }
}

function setStore(store: Record<string, InspectionResult>) {
    if (globalThis.window === undefined) return;
    try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    } catch {
        // ignore quota errors
    }
}

const INSPECTION_UPDATE_EVENT = "glados:inspections-updated";

/** Save a single inspection (legacy or new batch) */
export function saveInspection(result: Omit<InspectionResult, "id">): string {
    const id = `insp-${globalThis.crypto.randomUUID()}`;
    const full: InspectionResult = { ...result, id };
    const store = getStore();
    store[id] = full;
    setStore(store);
    memoryCache[id] = full;
    if (globalThis.window !== undefined) {
        globalThis.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
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
    const id = `batch-${globalThis.crypto.randomUUID()}`;
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
    memoryCache[id] = result;
    if (globalThis.window !== undefined) {
        globalThis.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
    }
    return id;
}

/** Create a placeholder inspection (status "running") so it appears in history; update with updateInspectionProgress and updateInspectionWithResult. */
export function saveInspectionPlaceholder(params: {
    projectId?: string;
    projectName?: string;
    designSpecs: string[];
    submissions: Array<{ productPhoto: string; photoName: string }>;
}): string {
    const id = `batch-${globalThis.crypto.randomUUID()}`;
    const now = new Date().toISOString();
    const subs: InspectionSubmission[] = params.submissions.map((s, i) => ({
        id: `${id}-sub-${i}`,
        timestamp: now,
        productPhoto: s.productPhoto,
        photoName: s.photoName,
        designSpec: params.designSpecs,
        status: "pending",
        defects: [],
        analysis: "",
    }));
    const first = subs[0];
    const result: InspectionResult = {
        id,
        imageUrl: first?.productPhoto ?? "",
        response: "",
        timestamp: now,
        projectId: params.projectId,
        projectName: params.projectName,
        submissions: subs,
        status: "running",
        progress: 0,
    };
    const store = getStore();
    store[id] = result;
    setStore(store);
    memoryCache[id] = result;
    if (globalThis.window !== undefined) {
        globalThis.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
    }
    return id;
}

/** Update progress (0-100) for a running inspection. */
export function updateInspectionProgress(id: string, progress: number): void {
    const store = getStore();
    const entry = store[id];
    if (!entry || entry.status !== "running") return;
    store[id] = { ...entry, progress: Math.min(100, Math.max(0, progress)) };
    setStore(store);
    if (memoryCache[id]) memoryCache[id] = store[id];
    if (globalThis.window !== undefined) {
        globalThis.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
    }
}

/** Replace a running placeholder with the final result. */
export function updateInspectionWithResult(
    id: string,
    payload: Omit<InspectionResult, "id" | "status" | "progress">
): void {
    const store = getStore();
    const entry = store[id];
    if (!entry) return;
    const result: InspectionResult = {
        ...payload,
        id,
        status: "complete",
        progress: 100,
    };
    store[id] = result;
    setStore(store);
    memoryCache[id] = result;
    if (globalThis.window !== undefined) {
        globalThis.dispatchEvent(new CustomEvent(INSPECTION_UPDATE_EVENT));
    }
}

export { INSPECTION_UPDATE_EVENT };

export function getInspection(id: string): InspectionResult | null {
    const fromMemory = memoryCache[id];
    if (fromMemory) return fromMemory;
    const store = getStore();
    return store[id] ?? null;
}

export function getAllInspections(): InspectionResult[] {
    try {
        const store = getStore();
        return Object.values(store).sort(
            (a, b) =>
                (new Date(b.timestamp).getTime() || 0) -
                (new Date(a.timestamp).getTime() || 0)
        );
    } catch {
        return [];
    }
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

/** True if the inspection is still running (placeholder). */
export function isInspectionRunning(result: InspectionResult): boolean {
    return result.status === "running";
}
