// lib/contexts/app-context.tsx
"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface Project {
    id: string;
    name: string;
    createdAt: Date;
    updatedAt: Date;
    designSpecs?: string[]; // links to design specs for this project
}

interface AppContextType {
    theme: "light" | "dark";
    currentProject: Project | null;
    setTheme: (theme: "light" | "dark") => void;
    setCurrentProject: (project: Project | null) => void;
    toggleTheme: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
    const [theme, setThemeState] = useState<"light" | "dark">("light");
    const [currentProject, setCurrentProject] = useState<Project | null>(null);
    const [mounted, setMounted] = useState(false);

    // Load theme from localStorage on mount
    useEffect(() => {
        setMounted(true);
        const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
        if (savedTheme) {
            setThemeState(savedTheme);
            document.documentElement.classList.toggle("dark", savedTheme === "dark");
        } else {
            // Apply initial theme class
            document.documentElement.classList.remove("dark");
        }
    }, []);

    const setTheme = (newTheme: "light" | "dark") => {
        setThemeState(newTheme);
        if (mounted) {
            localStorage.setItem("theme", newTheme);
        }
        document.documentElement.classList.toggle("dark", newTheme === "dark");
    };

    const toggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light";
        setTheme(newTheme);
    };

    return (
        <AppContext.Provider
            value={{
                theme,
                currentProject,
                setTheme,
                setCurrentProject,
                toggleTheme,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error("useApp must be used within an AppProvider");
    }
    return context;
}