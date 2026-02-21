"use client";

/**
 * Main application layout that wraps all pages. Contains the header, navigation drawer, and footer.
 */
import { Header, Sidebar } from "@/components";
import { usePathname } from "next/navigation";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();

    const headerHeight = "60px"
    const sidebarWidth = "300px"

    const isLoginPage = pathname === "/login";
    const isProjectsPage = pathname === "/projects";

    return (
        <div className="flex flex-col min-h-screen w-full bg-background">
            {/* Header */}
            {!isLoginPage && (<Header />)}

            {/* Body container */}
            <div className={`flex flex-row flex-1 min-h-0 w-full ${isLoginPage ? "pt-0" : `pt-[${headerHeight}]`}`}>
                {!isLoginPage && !isProjectsPage && (
                    <div className={`w-[${sidebarWidth}] flex-shrink-0`}>
                        <div className={`sticky top-[${headerHeight}]`} style={{ height: `calc(100vh - ${headerHeight})` }}>
                            <Sidebar />
                        </div>
                    </div>
                )}
                <div className="flex flex-col flex-1 min-h-0">
                    <main className={`h-full min-h-0 overflow-y-auto ${isLoginPage ? "p-0" : "p-6"}`}>
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
}
