"use client";

/**
 * Main application layout that wraps all pages. Contains the header, navigation drawer, and footer.
 */
import Header, { headerHeight } from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import InspectHistorySidebar from "@/components/InspectHistorySidebar";
import { usePathname } from "next/navigation";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();

    const sidebarWidth = "350px";
    const isLoginPage = pathname === "/login";
    const isProjectsPage = pathname === "/projects";
    const isInspectRoute = pathname?.startsWith("/inspect");

    const SidebarComponent = isInspectRoute ? InspectHistorySidebar : Sidebar;

    return (
        <div className="flex flex-col min-h-screen w-full bg-background">
            {/* Header */}
            {!isLoginPage && <Header />}

            {/* Body container */}
            <div
                className="flex flex-row flex-1 min-h-0 w-full"
                style={isLoginPage ? undefined : { paddingTop: headerHeight }}
            >
                {!isLoginPage && !isProjectsPage && (
                    <div className="flex-shrink-0" style={{ width: sidebarWidth }}>
                        <div
                            className="sticky overflow-y-auto"
                            style={{ top: headerHeight, height: `calc(100vh - ${headerHeight})` }}
                        >
                            <SidebarComponent />
                        </div>
                    </div>
                )}
                <div className="flex flex-col flex-1 min-h-0">
                    <main
                        className={`h-full min-h-0 overflow-y-auto ${isLoginPage ? "p-0" : "p-6"}`}
                    >
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
}
