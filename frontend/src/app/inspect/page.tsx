"use client";

/**
 * Page for creating a new inspection.
 */

import { useRouter } from "next/navigation";

export default function InspectPage() {
    const router = useRouter();

    return (
        <div className="h-auto bg-slate-50 dark:bg-zinc-950 transition-colors">
            <main className="max-w-[1800px] mx-auto">
                <div>new inspection</div>
            </main>
        </div>
    );
}
