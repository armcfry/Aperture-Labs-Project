"use client";

/**
 * Main application layout that wraps all pages. Contains the header, navigation drawer, and footer.
 */
import { Header } from "@/components/layout";
import { usePathname } from "next/navigation";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();

    const isLoginPage = pathname === "/login";

    return (
        <div className="flex flex-col min-h-screen w-full bg-background">
            {/* Header (fixed height) */}
            {!isLoginPage && (
                <header>
                    <Header />
                </header>
            )}

            {/* Body container */}
            <div className={`flex flex-col flex-1 w-auto ${isLoginPage ? "pt-0" : "pt-[60px]"}`}>
                {/* Nav drawer here */}
                <div className="flex flex-col flex-1 overflow-hidden">
                    <main className={`flex-1 overflow-y-auto ${isLoginPage ? "p-0" : "p-6"}`}>
                        {children}
                    </main>
                    {/* Footer here */}
                </div>
            </div>
        </div>
    );
}
