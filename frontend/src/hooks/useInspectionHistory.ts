"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import {
    getAllInspections,
    INSPECTION_UPDATE_EVENT,
    type InspectionResult,
    type InspectionSubmission,
} from "@/lib/inspection-store";
import { listSubmissions, getImageUrl } from "@/lib/api";

const API_SUBMISSION_RUNNING_STATUSES = new Set(["running", "queued"]);

function submissionImageName(imageId: string): string {
    const parts = imageId.split("/");
    return parts.at(-1) ?? "image.png";
}

/**
 * Shared hook for inspection history. Returns merged local + API inspections when projectId is set.
 * Both sidebars can use this and subscribe to the same event.
 */
export function useInspectionHistory(projectId: string | undefined) {
    const [inspections, setInspections] = useState<InspectionResult[]>([]);
    const imageUrlCache = useRef<Map<string, string>>(new Map());

    const refresh = useCallback(async () => {
        if (!projectId) {
            setInspections(getAllInspections());
            return;
        }
        try {
            const apiSubs = await listSubmissions(projectId);
            const local = getAllInspections();
            const localIds = new Set(
                local.flatMap((i) => (i.submissions ?? []).map((s) => s.id)),
            );
            const newApiResults: InspectionResult[] = [];
            for (const sub of apiSubs) {
                if (localIds.has(sub.id)) continue;
                let thumbUrl = imageUrlCache.current.get(sub.image_id) ?? "";
                if (!thumbUrl) {
                    try {
                        thumbUrl = await getImageUrl(sub.image_id);
                        imageUrlCache.current.set(sub.image_id, thumbUrl);
                    } catch {
                        /* presigned URL failed */
                    }
                }
                const isRunning = API_SUBMISSION_RUNNING_STATUSES.has(sub.status);
                const submissionStatus: "pass" | "fail" | "pending" = isRunning
                    ? "pending"
                    : sub.pass_fail === "unknown"
                      ? "fail"
                      : sub.pass_fail;
                const submission: InspectionSubmission = {
                    id: sub.id,
                    timestamp: sub.submitted_at,
                    productPhoto: thumbUrl,
                    photoName: submissionImageName(sub.image_id),
                    designSpec: [],
                    status: submissionStatus,
                    defects: [],
                    analysis: "",
                };
                const inspection: InspectionResult = {
                    id: `api-${sub.id}`,
                    imageUrl: thumbUrl,
                    response: "",
                    timestamp: sub.submitted_at,
                    projectId: sub.project_id,
                    submissions: [submission],
                };
                if (isRunning) {
                    inspection.status = "running";
                    inspection.progress = 0;
                }
                newApiResults.push(inspection);
            }
            const merged = [...newApiResults, ...local].sort(
                (a, b) =>
                    (new Date(b.timestamp).getTime() || 0) -
                    (new Date(a.timestamp).getTime() || 0),
            );
            setInspections(merged);
        } catch {
            setInspections(getAllInspections());
        }
    }, [projectId]);

    useEffect(() => {
        const local = getAllInspections();
        if (local.length > 0) setInspections(local);
        refresh();
        const handleUpdate = () => {
            const local = getAllInspections();
            if (!projectId) {
                setInspections(local);
                return;
            }
            setInspections((prev) => {
                const byId = new Map(prev.map((i) => [i.id, i]));
                local.forEach((i) => byId.set(i.id, i));
                return Array.from(byId.values()).sort(
                    (a, b) =>
                        (new Date(b.timestamp).getTime() || 0) -
                        (new Date(a.timestamp).getTime() || 0),
                );
            });
            refresh();
        };
        globalThis.addEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
        return () => globalThis.removeEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
    }, [refresh, projectId]);

    return { inspections, refresh };
}
