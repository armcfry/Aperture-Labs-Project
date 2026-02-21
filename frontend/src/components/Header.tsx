"use client";

/**
 * Header component for the application.
 */

import { usePathname, useRouter } from "next/navigation";
import { Activity, FolderOpen, Sun, Moon, LogOut } from "lucide-react";
import { useApp } from "@/app/AppProvider";
import { Button } from "@/components/ui/button";

export const headerHeight = "60px"

export default function Header() {
    const router = useRouter();
    const pathname = usePathname();

    // App context
    const { theme, currentProject, toggleTheme, setCurrentProject, clearProjectOnLogout } = useApp();

    const handleLogout = () => {
        // Clear only the persisted/current project
        clearProjectOnLogout();
        // Also clear in-memory state (defensive; clearProjectOnLogout already clears)
        setCurrentProject(null);
        // Navigate to login page
        router.push("/login");
    };

    const handleSwitchProject = () => {
        // clear current project and go to projects list
        setCurrentProject(null);
        router.push("/projects");
    };

    return (
        <header className={`fixed top-0 left-0 right-0 z-50 bg-white dark:bg-zinc-900 border-b border-slate-200 dark:border-zinc-800 h-[${headerHeight}]`}>
            <div className="max-w-[1800px] mx-auto px-6 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded flex items-center justify-center">
                                <Activity className="text-white" strokeWidth={2.5} size={18} />
                            </div>
                            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                                GLaDOS
                            </h1>
                        </div>

                        {/* Current Project Display */}
                        {currentProject && (
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-zinc-800 rounded-lg border border-slate-200 dark:border-zinc-700">
                                <FolderOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                <span className="text-sm font-medium text-slate-900 dark:text-white">
                                    {currentProject.name}
                                </span>
                                <Button
                                    onClick={handleSwitchProject}
                                    variant="ghost"
                                    size="sm"
                                    className="text-xs h-auto py-0 px-2 ml-2 text-muted-foreground hover:text-primary"
                                >
                                    Switch
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Right side */}
                    <div className="flex items-center gap-0">
                        <Button
                            onClick={toggleTheme}
                            variant="ghost"
                            size="icon"
                            title="Toggle theme"
                        >
                            {theme === "dark" ? <Sun /> : <Moon />}
                        </Button>
                        {pathname !== "/login" && (
                            <Button
                                onClick={handleLogout}
                                variant="ghost"
                                size="icon"
                                title="Logout"
                            >
                                <LogOut />
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
