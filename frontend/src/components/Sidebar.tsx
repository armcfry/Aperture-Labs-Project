"use client";

import { useApp } from "@/app/AppProvider";
import { HistoryIcon, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
    getAllInspections,
    deriveStatus,
    INSPECTION_UPDATE_EVENT,
    type InspectionResult,
} from "@/lib/inspection-store";
import { Badge } from "./ui/badge";

export type HistoryItem = {
    id: string;
    project: string;
    timestamp: string;
    status: "pass" | "fail";
    photo: string;
    defectCount?: number;
};

function inspectionToHistoryItem(r: InspectionResult): HistoryItem {
    return {
        id: r.id,
        project: r.projectName ?? "Unknown Project",
        timestamp: r.timestamp,
        status: deriveStatus(r.response),
        photo: r.imageUrl,
    };
}

export default function Sidebar() {
    const router = useRouter();
    const { currentProject } = useApp();
    const [inspections, setInspections] = useState<HistoryItem[]>([]);

    const loadInspections = useCallback(() => {
        const all = getAllInspections();
        setInspections(all.map(inspectionToHistoryItem));
    }, []);

    useEffect(() => {
        loadInspections();
        const handleUpdate = () => loadInspections();
        window.addEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
        return () => window.removeEventListener(INSPECTION_UPDATE_EVENT, handleUpdate);
    }, [loadInspections]);

    const handleView = (id: string) => {
        router.push(`/inspect/result/${id}`);
    };

    const handleNew = () => {
        router.push("/inspect");
    };

    return (
        <aside className="h-full w-full flex flex-col bg-white dark:bg-zinc-900 border-r border-slate-200 dark:border-zinc-800 p-6">
            {/* Fixed header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    History
                </h2>
                <button
                    onClick={handleNew}
                    className="px-3 py-1.5 text-sm border border-slate-300 dark:border-zinc-700 rounded-lg hover:bg-slate-50 dark:hover:bg-zinc-800 transition-colors text-slate-700 dark:text-zinc-300 flex items-center gap-1"
                >
                    <Plus className="w-4 h-4" />
                    New
                </button>
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto">
                <div className="space-y-2">
                    {!currentProject || inspections.length === 0 ? (
                        <div className="text-center py-12">
                            <HistoryIcon className="w-12 h-12 text-slate-300 dark:text-zinc-700 mx-auto mb-3" />
                            <p className="text-sm text-slate-500 dark:text-zinc-500">
                                No inspections yet
                            </p>
                        </div>
                    ) : (
                        inspections.map((item) => {
                            const date = new Date(item.timestamp);
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => handleView(item.id)}
                                    className="w-full text-left p-3 rounded-lg border border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700 hover:bg-slate-50 dark:hover:bg-zinc-800 transition-colors group"
                                >
                                    <div className="flex gap-3 mb-2">
                                        {/* Thumbnail */}
                                        <div className="w-12 h-12 rounded overflow-hidden bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 flex-shrink-0">
                                            <img
                                                src={item.photo}
                                                alt="Product thumbnail"
                                                className="w-full h-full object-cover"
                                            />
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between mb-1">
                                                <span className="text-sm font-semibold text-slate-900 dark:text-white">
                                                    {date.toLocaleDateString("en-US", {
                                                        month: "short",
                                                        day: "numeric",
                                                        year: "numeric",
                                                    })}
                                                </span>
                                            </div>
                                            <p className="text-xs text-slate-500 dark:text-zinc-500">
                                                {date.toLocaleTimeString("en-US", {
                                                    hour: "2-digit",
                                                    minute: "2-digit",
                                                })}
                                            </p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <Badge
                                                    variant="secondary"
                                                    className={
                                                        item.status === "pass"
                                                            ? "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300"
                                                            : "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300"
                                                    }
                                                >
                                                    {item.status === "pass"
                                                        ? "Pass"
                                                        : "Fail"}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            );
                        })
                    )}
                </div>
            </div>
        </aside>
    );
}
