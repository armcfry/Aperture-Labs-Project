/**
 * Page for creating a new inspection.
 */

import Header from "@/components/Header";

export default function InspectPage() {
    return (
        <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 transition-colors">
            <Header />
            <main className="max-w-[1800px] mx-auto px-6 py-8">
                <div>new inspection</div>
            </main>
        </div>
    );
}