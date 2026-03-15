"use client";

/**
 * Hook for inspection/submission history, sourced entirely from the backend API.
 * Polls every 3 seconds while any submissions are queued or running.
 * Dispatching SUBMISSION_UPLOADED_EVENT triggers an immediate refresh.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { listSubmissions, getImageUrl, type ApiSubmission } from "@/lib/api";

export const SUBMISSION_UPLOADED_EVENT = "glados:submission-uploaded";

const ACTIVE_STATUSES = new Set(["queued", "running"]);
const POLL_INTERVAL_MS = 3000;

export function useInspectionHistory(projectId: string | undefined) {
    const [submissions, setSubmissions] = useState<ApiSubmission[]>([]);
    const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
    const pollTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
    const mountedRef = useRef(true);
    const fetchingUrls = useRef<Set<string>>(new Set());

    const refresh = useCallback(async () => {
        if (!projectId) {
            setSubmissions([]);
            return;
        }
        try {
            const subs = await listSubmissions(projectId);
            if (!mountedRef.current) return;
            setSubmissions(subs);

            // Fetch presigned image URLs for the most recent submissions
            for (const sub of subs.slice(0, 30)) {
                if (!fetchingUrls.current.has(sub.image_id)) {
                    fetchingUrls.current.add(sub.image_id);
                    getImageUrl(sub.image_id)
                        .then(url => {
                            if (mountedRef.current) {
                                setImageUrls(prev => ({ ...prev, [sub.image_id]: url }));
                            }
                        })
                        .catch(() => {
                            fetchingUrls.current.delete(sub.image_id);
                        });
                }
            }

            // Keep polling while submissions are still running
            clearTimeout(pollTimerRef.current);
            if (subs.some(s => ACTIVE_STATUSES.has(s.status))) {
                pollTimerRef.current = setTimeout(() => { refresh(); }, POLL_INTERVAL_MS);
            }
        } catch {
            // ignore transient fetch errors
        }
    }, [projectId]);

    useEffect(() => {
        mountedRef.current = true;
        void refresh();
        const handler = () => { refresh(); };
        globalThis.addEventListener(SUBMISSION_UPLOADED_EVENT, handler);
        return () => {
            mountedRef.current = false;
            clearTimeout(pollTimerRef.current);
            globalThis.removeEventListener(SUBMISSION_UPLOADED_EVENT, handler);
        };
    }, [refresh]);

    return { submissions, imageUrls, refresh };
}
