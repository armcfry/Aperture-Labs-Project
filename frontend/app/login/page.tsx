"use client";

/**
 * Page for logging in.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, User, Activity, Moon, Sun } from "lucide-react";
import { useApp } from "@/lib/app-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormField, FormItem, FormLabel } from "@/components/ui/form";

export default function LoginPage() {
    const router = useRouter();
    const { theme, toggleTheme } = useApp();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Replace with actual authentication API call
        // Mock authentication - in production, this would validate credentials
        if (username && password) {
            // Navigate to projects page after successful login
            router.push("/projects");
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 transition-colors">
            {/* Dark Mode Toggle */}
            <Button
                onClick={toggleTheme}
                variant="secondary"
                size="icon"
                className="absolute top-6 right-6 h-9 w-9"
                title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
                {theme === "dark" ? (
                    <Sun className="w-5 h-5" />
                ) : (
                    <Moon className="w-5 h-5" />
                )}
            </Button>

            <div className="w-full max-w-md">
                {/* Logo/Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-lg mb-4">
                        <Activity
                            className="w-10 h-10 text-primary-foreground"
                            strokeWidth={2.5}
                        />
                    </div>
                    <h1 className="text-3xl font-bold text-foreground mb-2">
                        GLaDOS
                    </h1>
                    <p className="text-muted-foreground">
                        AI Anomaly Detection System
                    </p>
                </div>

                {/* Login Form */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-xl">Technician Login</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Form onSubmit={handleSubmit}>
                            <FormField>
                                <FormItem>
                                    <FormLabel htmlFor="username">
                                        Username
                                    </FormLabel>
                                    <div className="relative">
                                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                                        <Input
                                            type="text"
                                            id="username"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                            className="pl-10"
                                            placeholder="Enter username"
                                            required
                                        />
                                    </div>
                                </FormItem>
                            </FormField>

                            <FormField>
                                <FormItem>
                                    <FormLabel htmlFor="password">
                                        Password
                                    </FormLabel>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                                        <Input
                                            type="password"
                                            id="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            className="pl-10"
                                            placeholder="Enter password"
                                            required
                                        />
                                    </div>
                                </FormItem>
                            </FormField>

                            <Button type="submit" className="w-full">
                                Sign In
                            </Button>
                        </Form>
                    </CardContent>
                    <CardFooter className="flex-col">
                        <div className="w-full pt-4 border-t border-border">
                            <p className="text-xs text-muted-foreground text-center">
                                Demo credentials: Any username and password
                            </p>
                        </div>
                    </CardFooter>
                </Card>

                <div className="mt-6 text-center">
                    <p className="text-xs text-muted-foreground">
                        Manufacturing Quality Assurance Platform v1.0
                    </p>
                </div>
            </div>
        </div>
    );
}
