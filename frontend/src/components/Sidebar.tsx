"use client";

import { useApp } from "@/app/AppProvider";
import { HistoryIcon, Plus, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";

export type HistoryItem = {
    id: string;
    project: string; // Corresponding project name
    timestamp: string;
    status: "pass" | "fail";
    photo: string;
    defectCount?: number;
};

export default function Sidebar() {
    const router = useRouter();
    const { currentProject } = useApp();

    // Dummy history for PoC — later replace with API call:
    // fetch(`/api/projects/${projectId}/history`) -> setHistory(...)
    const projectName = currentProject?.name ?? "Unknown Project";
    const now = new Date();
    const inspections: HistoryItem[] = [
        {
            id: "h-001",
            project: projectName,
            timestamp: now.toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=11",
            defectCount: 3,
        },
        {
            id: "h-002",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString(),
            status: "pass",
            photo: "https://picsum.photos/300/200?random=12",
            defectCount: 0,
        },
        {
            id: "h-003",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 2).toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=13",
            defectCount: 1,
        },
        {
            id: "h-001",
            project: projectName,
            timestamp: now.toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=11",
            defectCount: 3,
        },
        {
            id: "h-002",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString(),
            status: "pass",
            photo: "https://picsum.photos/300/200?random=12",
            defectCount: 0,
        },
        {
            id: "h-003",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 2).toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=13",
            defectCount: 1,
        },
        {
            id: "h-001",
            project: projectName,
            timestamp: now.toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=11",
            defectCount: 3,
        },
        {
            id: "h-002",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString(),
            status: "pass",
            photo: "https://picsum.photos/300/200?random=12",
            defectCount: 0,
        },
        {
            id: "h-003",
            project: projectName,
            timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 2).toISOString(),
            status: "fail",
            photo: "https://picsum.photos/300/200?random=13",
            defectCount: 1,
        },
    ];

    useEffect(() => {
        // Placeholder: load history for currentProject
        // if (currentProject) {
        //   fetch(`/api/projects/${currentProject.id}/history`).then(...)
        // }
    }, [currentProject]);

    // Handler for when user clicks a history item
    const handleView = (id: string) => {
        router.push(`/inspect/result/${id}`);
    };

    const handleNew = () => {
        // Signal the page to show the new inspection form using a query param.
        // This keeps the sidebar prop-free.
        router.push("/inspect");
    };

    return (
        <aside className="h-full flex flex-col bg-white dark:bg-zinc-900 border-r border-slate-200 dark:border-zinc-800 p-6 w-[290px]">
            {/* Fixed header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Inspections</h2>
                <Button onClick={handleNew} size="sm" variant="outline" className="flex flex-row">
                    <Plus className="w-4 h-4" /> New
                </Button>
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto">
                <div className="space-y-3">
                    {!currentProject || inspections.length === 0 ? (
                        <div className="text-center py-12">
                            <HistoryIcon className="w-12 h-12 text-slate-300 dark:text-zinc-700 mx-auto mb-3" />
                            <p className="text-sm text-slate-500 dark:text-zinc-500">
                                No inspections yet
                            </p>
                        </div>
                    ) : (
                        // Map inspection history item
                        inspections.map((item) => {
                            const date = new Date(item.timestamp);
                            return (
                                <Card key={item.id} onClick={() => handleView(item.id)}
                                    className="relative group cursor-pointer transition-all h-16 hover:shadow-md hover:border-slate-300 dark:hover:border-zinc-700"
                                >
                                    <CardContent className="p-0">
                                        <div className="flex gap-1">
                                            {/* LEFT IMAGE */}
                                            <div className="w-16 h-16 flex-shrink-0 overflow-hidden rounded-l-lg">
                                                <img
                                                    src={item.photo}
                                                    alt="inspection"
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>

                                            {/* RIGHT CONTENT */}
                                            <div className="flex-1 p-2 flex flex-col justify-start">
                                                <div className="text-xs font-semibold text-slate-900 dark:text-white">
                                                    {date.toLocaleDateString("en-US", {
                                                        month: "short",
                                                        day: "numeric",
                                                        year: "numeric",
                                                    })}
                                                    <>  </>
                                                    {date.toLocaleTimeString("en-US", {
                                                        hour: "2-digit",
                                                        minute: "2-digit",
                                                    })}
                                                </div>

                                                <div className="flex items-center gap-2 mt-2">
                                                    {/* STATUS BADGE */}
                                                    <Badge
                                                        variant="secondary"
                                                        className={
                                                            item.status === "pass"
                                                                ? "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300"
                                                                : "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300"
                                                        }
                                                    >
                                                        {item.status === "pass" ? "Pass" : "Fail"}
                                                    </Badge>

                                                    {/* DEFECT COUNT */}
                                                    {item.status === "fail" && (
                                                        <span className="text-xs text-muted-foreground">
                                                            {item.defectCount ?? 0} {item.defectCount === 1 ? "defect" : "defects"}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        {/* DELETE BUTTON (appears on hover) */}
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                console.log("delete", item.id);
                                            }}
                                            className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <X className="w-5 h-5 text-muted-foreground hover:text-red-500 transition-colors" />
                                        </button>
                                    </CardContent>
                                </Card>
                            )
                        })
                    )}
                </div>
            </div>
        </aside>
    );
}
