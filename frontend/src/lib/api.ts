/**
 * API configuration for backend requests.
 * Set NEXT_PUBLIC_API_URL in .env.local to override (e.g. for production).
 */
export const API_BASE_URL =
    (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_API_URL) || "http://localhost:8000";

export type DetectionResponse = {
    response: string;
    model?: string;
    inference_time_ms?: number;
};

export async function detectFod(file: File): Promise<DetectionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}/api/detect`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail ?? `Detection failed: ${res.status}`);
    }

    return res.json();
}
