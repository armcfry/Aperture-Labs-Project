"use client";

/**
 * Page for creating a new inspection.
 */

import { useRouter } from "next/navigation";
import Header from "@/components/Header";

export default function InspectPage() {
    const router = useRouter();

    const handleSwitchProject = () => {
        router.push("/projects");
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 transition-colors">
            <Header onSwitchProject={handleSwitchProject} />
            <main className="max-w-[1800px] mx-auto px-6 py-8 pt-24">
                <div>new inspection</div>
            </main>
        </div>
    );
}