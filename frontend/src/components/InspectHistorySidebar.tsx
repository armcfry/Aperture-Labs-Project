"use client";

/**
 * History sidebar for the inspect page.
 * Supports batch submissions with checkboxes and Report generation.
 * Based on AI Anomaly Detection Tool Dashboard history panel.
 */

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { History as HistoryIcon, Plus } from "lucide-react";
import {
    getAllInspections,
    toSubmissions,
    deriveStatus,
    INSPECTION_UPDATE_EVENT,
    type InspectionResult,
} from "@/lib/inspection-store";
import { useApp } from "@/app/AppProvider";

type SelectedMap = Map<string, Set<string>>;

export default function InspectHistorySidebar() {
    const router = useRouter();
    const { currentProject } = useApp();
    const currentProjectId = currentProject?.id;
    const [inspections, setInspections] = useState<InspectionResult[]>([]);
    const [selectedSubmissions, setSelectedSubmissions] = useState<SelectedMap>(
        new Map()
    );

    const loadInspections = useCallback(() => {
        const all = getAllInspections();
        setInspections(all);
    }, []);

    useEffect(() => {
        loadInspections();
        const handleUpdate = () => loadInspections();
        window.addEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
        return () => window.removeEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
    }, [loadInspections]);

    const toggleSubmission = (batchId: string, subId: string) => {
        setSelectedSubmissions((prev) => {
            const next = new Map(prev);
            const set = new Set(next.get(batchId) ?? []);
            if (set.has(subId)) set.delete(subId);
            else set.add(subId);
            if (set.size === 0) next.delete(batchId);
            else next.set(batchId, set);
            return next;
        });
    };

    const selectAll = (batchId: string, subIds: string[]) => {
        setSelectedSubmissions((prev) => {
            const next = new Map(prev);
            next.set(batchId, new Set(subIds));
            return next;
        });
    };

    const deselectAll = (batchId: string) => {
        setSelectedSubmissions((prev) => {
            const next = new Map(prev);
            next.delete(batchId);
            return next;
        });
    };

    const handleReport = (batchId: string) => {
        const selected = selectedSubmissions.get(batchId);
        if (!selected || selected.size === 0) return;
        const q = `?submissions=${Array.from(selected).join(",")}`;
        router.push(`/inspect/result/${batchId}${q}`);
    };

    const handleViewItem = (item: InspectionResult) => {
        router.push(`/inspect/result/${item.id}`);
    };

    const filtered = currentProjectId
        ? inspections.filter(
              (i) => i.projectId === currentProjectId || !i.projectId
          )
        : inspections;

    return (
        <aside className="w-[350px] h-full flex-shrink-0 flex flex-col bg-white dark:bg-zinc-900 border-r border-slate-200 dark:border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-4 flex-shrink-0">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    History
                </h2>
                <Link
                    href="/inspect"
                    className="px-3 py-1.5 text-sm border border-slate-300 dark:border-zinc-700 rounded-lg hover:bg-slate-50 dark:hover:bg-zinc-800 transition-colors text-slate-700 dark:text-zinc-300 flex items-center gap-1"
                >
                    <Plus className="w-4 h-4" />
                    New
                </Link>
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto space-y-4">
                {filtered.length === 0 ? (
                    <div className="min-h-full flex flex-col items-center justify-center text-center py-12">
                        <HistoryIcon className="w-12 h-12 text-slate-300 dark:text-zinc-700 mb-3" />
                        <p className="text-sm text-slate-500 dark:text-zinc-500">
                            No inspections yet
                        </p>
                    </div>
                ) : (
                    filtered.map((item) => {
                        const subs = toSubmissions(item);
                        const selected = selectedSubmissions.get(item.id) ?? new Set();
                        const hasSelection = selected.size > 0;
                        const status = item.submissions
                            ? item.submissions.some((s) => s.status === "fail")
                                ? "fail"
                                : "pass"
                            : deriveStatus(item.response);
                        const thumb = subs[0]?.productPhoto ?? item.imageUrl;

                        return (
                            <div
                                key={item.id}
                                className="p-3 rounded-lg border border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700 bg-slate-50 dark:bg-zinc-800/50"
                            >
                                {/* Header */}
                                <div className="flex gap-3 mb-3">
                                    <div className="w-12 h-12 rounded overflow-hidden bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 flex-shrink-0">
                                        <img
                                            src={thumb}
                                            alt="Product thumbnail"
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between mb-1">
                                            <span className="text-sm font-semibold text-slate-900 dark:text-white">
                                                {new Date(
                                                    item.timestamp
                                                ).toLocaleDateString("en-US", {
                                                    month: "short",
                                                    day: "numeric",
                                                    year: "numeric",
                                                })}
                                            </span>
                                        </div>
                                        <p className="text-xs text-slate-500 dark:text-zinc-500 mb-1">
                                            {new Date(
                                                item.timestamp
                                            ).toLocaleTimeString("en-US", {
                                                hour: "2-digit",
                                                minute: "2-digit",
                                            })}
                                        </p>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-600 dark:text-zinc-400">
                                                {subs.length} submission
                                                {subs.length !== 1 ? "s" : ""}
                                            </span>
                                            <span
                                                className={`text-xs font-medium ${
                                                    status === "pass"
                                                        ? "text-green-500"
                                                        : "text-red-500"
                                                }`}
                                            >
                                                {status.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Submissions list */}
                                <div className="space-y-1.5 mb-3">
                                    {subs.map((sub) => (
                                        <div
                                            key={sub.id}
                                            className="flex items-center gap-2 p-2 bg-white dark:bg-zinc-900 rounded border border-slate-200 dark:border-zinc-700 hover:bg-slate-50 dark:hover:bg-zinc-800 transition-colors"
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selected.has(sub.id)}
                                                onChange={() =>
                                                    toggleSubmission(
                                                        item.id,
                                                        sub.id
                                                    )
                                                }
                                                className="w-4 h-4 text-blue-600 dark:text-blue-400 bg-gray-100 dark:bg-zinc-800 border-gray-300 dark:border-zinc-700 rounded focus:ring-blue-500"
                                            />
                                            <button
                                                type="button"
                                                onClick={() =>
                                                    handleViewItem(item)
                                                }
                                                className="flex-1 flex items-center gap-2 min-w-0 text-left"
                                            >
                                                <div className="w-8 h-8 rounded overflow-hidden bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 flex-shrink-0">
                                                    <img
                                                        src={sub.productPhoto}
                                                        alt={sub.photoName}
                                                        className="w-full h-full object-cover"
                                                    />
                                                </div>
                                                <span className="text-xs font-medium text-slate-900 dark:text-white truncate flex-1">
                                                    {sub.photoName}
                                                </span>
                                                <span
                                                    className={`text-xs font-medium flex-shrink-0 ${
                                                        sub.status === "pass"
                                                            ? "text-green-500"
                                                            : "text-red-500"
                                                    }`}
                                                >
                                                    {sub.status.toUpperCase()}
                                                </span>
                                            </button>
                                        </div>
                                    ))}
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2">
                                    <button
                                        type="button"
                                        onClick={() =>
                                            selectAll(
                                                item.id,
                                                subs.map((s) => s.id)
                                            )
                                        }
                                        className="flex-1 px-2 py-1.5 text-xs border border-slate-300 dark:border-zinc-700 rounded hover:bg-white dark:hover:bg-zinc-900 transition-colors text-slate-700 dark:text-zinc-300"
                                    >
                                        All
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() =>
                                            deselectAll(item.id)
                                        }
                                        className="flex-1 px-2 py-1.5 text-xs border border-slate-300 dark:border-zinc-700 rounded hover:bg-white dark:hover:bg-zinc-900 transition-colors text-slate-700 dark:text-zinc-300"
                                    >
                                        None
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => handleReport(item.id)}
                                        disabled={!hasSelection}
                                        className={`flex-1 px-2 py-1.5 text-xs font-semibold rounded transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                                            hasSelection
                                                ? "bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white"
                                                : "border border-slate-300 dark:border-zinc-700 text-slate-700 dark:text-zinc-300"
                                        }`}
                                    >
                                        Report
                                        {hasSelection &&
                                            ` (${selected.size})`}
                                    </button>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </aside>
    );
}
