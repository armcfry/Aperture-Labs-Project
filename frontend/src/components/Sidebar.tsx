"use client";

import { useRouter } from "next/navigation";
import { useApp } from "@/app/AppProvider";
import { useInspectionHistory } from "@/hooks/useInspectionHistory";
import { deriveStatus, type InspectionResult } from "@/lib/inspection-store";
import { InspectionHistoryList, type HistoryItem } from "@/components/InspectionHistoryList";

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
    const { inspections } = useInspectionHistory(undefined);
    const items = inspections.map(inspectionToHistoryItem);

    return (
        <aside className="h-full w-full flex flex-col bg-white dark:bg-zinc-900 border-r border-slate-200 dark:border-zinc-800 p-6">
            <InspectionHistoryList
                items={items}
                onNew={() => router.push("/inspect")}
                onViewItem={(id) => router.push(`/inspect/result/${id}`)}
                requireProject
                currentProjectId={currentProject?.id}
            />
        </aside>
    );
}
